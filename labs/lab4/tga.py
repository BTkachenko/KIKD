''' Skróty kierunków geograficznych tradycyjne
      NW |  N
      -------
       W |  X
    7 schematów predykcji:
    1. X=W
    2. X=N
    3. X=NW
    4. X=N+W-NW
    5. X=N+(W-NW)
    6. X=W+((N-NW)/2)
    7. X=(N+W)/2
    8. Nowy standard

'''
import sys
import math

# Klasa reprezentująca piksel obrazu.
class Pixel:
    def __init__(self, red, green, blue):
        # Inicjalizacja obiektu Pixel.
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        # Tekstowa reprezentacja obiektu Pixel.
        return "({}, {}, {})".format(self.red, self.green, self.blue)

    def __str__(self):
        # Tekstowa reprezentacja obiektu Pixel.
        return "({}, {}, {})".format(self.red, self.green, self.blue)

    def __sub__(self, other):
        # Operator odejmowania pikseli.
        return Pixel((self.red - other.red) % 256, (self.green - other.green) % 256, (self.blue - other.blue) % 256)

    def __add__(self, other):
        # Operator dodawania pikseli.
        return Pixel((self.red + other.red) % 256, (self.green + other.green) % 256, (self.blue + other.blue) % 256)

    def __floordiv__(self, other):
        # Operator dzielenia piksela przez liczbę całkowitą.
        return Pixel(self.red // other, self.green // other, self.blue // other)

# Funkcja obliczająca entropię pikseli w obrazie.
def get_entropy(pixels, type):
    # Oblicza entropię pikseli w obrazie.
    result = {}
    for i in range(256):
        result[i] = 0
    size = 0
    if type == 'basic':
        for pixel in pixels:
            result[pixel.red] += 1
            result[pixel.green] += 1
            result[pixel.blue] += 1
            size += 3
    else:
        for pixel in pixels:
            result[getattr(pixel, type)] += 1
            size += 1
    entropy = 0

    for item in result.values():
        if item == 0:
            continue
        entropy = entropy + item * (-math.log2(item))
    entropy = entropy / size + math.log2(size)
    return entropy

# Funkcja kodująca obraz z wykorzystaniem schematu predykcji.
def encode(pixels, image_width, image_height, mode):
    # Koduje obraz z wykorzystaniem schematu predykcji.
    encoded = []
    for i in range(image_width):
        for j in range(image_height):
            if j == 0:
                w = Pixel(0, 0, 0)
            else:
                w = pixels[image_width * i + (j - 1)]
            if i == 0:
                n = Pixel(0, 0, 0)
            else:
                n = pixels[image_width * (i - 1) + j]
            if j == 0 or i == 0:
                nw = Pixel(0, 0, 0)
            else:
                nw = pixels[image_width * (i - 1) + (j - 1)]
            encoded.append(pixels[image_width * i + j] - predict_option(mode, w, n, nw))
    return encoded

# Funkcja implementująca nowy standard predykcji.
def new_standard(w, n, nw):
    # Implementacja nowego standardu predykcji.
    if nw >= max(w, n):
        return min(w, n)
    if nw <= min(w, n):
        return max(w, n)
    return w + n - nw

# Funkcja zwracająca wynik predykcji w zależności od trybu.
def predict_option(mode, w, n, nw):
    # Wybór trybu predykcji na podstawie numeru trybu.
    return {
        1: w,
        2: n,
        3: nw,
        4: n + w - nw,
        5: n + (w - nw),
        6: w + ((n - nw) // 2),
        7: (n + w) // 2,
        8: Pixel(new_standard(w.red, n.red, nw.red),
                new_standard(w.green, n.green, nw.green),
                new_standard(w.blue, n.blue, nw.blue)
                )
    }[mode]

# Funkcja odczytująca plik TGA i zwracająca listę pikseli.
def read_TGA(filename):
    # Odczytuje plik TGA i zwraca listę pikseli oraz wymiary obrazu.
    with open(filename, "rb") as f:
        byte = f.read()
        data = [int(x) for x in byte]
        image_width = data[13] * 256 + data[12]
        image_height = data[15] * 256 + data[14]
        source = data[18:]
        pixels_list = []
        for i in range(image_height):
            for j in range(image_width):
                index = (image_width * i + j) * 3
                pixels_list.append(Pixel(source[index], source[index + 1], source[index + 2]))
        return (pixels_list, image_width, image_height)

def main():
    # Słownik mapujący numery trybów predykcji na ich nazwy.
    predict = {
        0: 'Basic',
        1: 'W',
        2: 'N',
        3: 'NW',
        4: 'N+W-NW',
        5: 'N+(W-NW)',
        6: 'W+(N-NW)/2',
        7: '(N+W)/2',
        8: 'New Standard'
    }

    # Sprawdzenie, czy podano prawidłową liczbę argumentów.
    if len(sys.argv) < 2:
        print("Usage: jpegls.py <input_file>")
        return

    # Pobranie nazwy pliku z argumentu linii poleceń.
    file = sys.argv[1]

    # Odczytanie obrazu TGA i uzyskanie listy pikseli oraz wymiarów obrazu.
    pixels, image_width, image_height = read_TGA(file)

    # Lista typów entropii do obliczenia.
    types = ['basic', 'red', 'green', 'blue']

    # Lista dostępnych trybów predykcji.
    modes = [1, 2, 3, 4, 5, 6, 7, 8]

    # Lista wyników entropii dla różnych trybów i typów entropii.
    outcome = []

    # Obliczanie entropii dla każdego typu entropii i trybu predykcji.
    for x in types:
        entropy_value = get_entropy(pixels, x)
        print(f"Entropy for {x.capitalize()} (Basic): {entropy_value:.4f}")
        for i in modes:
            encoded = encode(pixels, image_width, image_height, i)
            entropy_encoded = get_entropy(encoded, x)
            outcome.append((i, x, entropy_encoded))
            print(f"Entropy for {x.capitalize()} with Prediction {predict[i]}: {entropy_encoded:.4f}")

    # Znalezienie najlepszego trybu predykcji dla każdego typu entropii.
    for x in types:
        temp = [item for item in outcome if item[1] == x]
        best_prediction = min(temp, key=lambda t: t[2])
        print(f"\nBest Prediction for {x.capitalize()}: {predict[best_prediction[0]]}, Entropy: {best_prediction[2]:.4f}")

if __name__ == "__main__":
    main()