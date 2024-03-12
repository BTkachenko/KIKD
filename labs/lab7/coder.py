import sys
from bitarray import bitarray

def hamming_encoding(data):
    # Sprawdza, czy długość danych wejściowych to dokładnie 4 bity.
    if len(data) != 4:
        raise ValueError("Data too long")
    
    # Oblicza bity parzystości dla kodowania Hamminga.
    # p1, p2, p3 są obliczane poprzez XORowanie określonych kombinacji bitów danych.
    p1 = data[0] ^ data[1] ^ data[3]
    p2 = data[0] ^ data[2] ^ data[3]
    p3 = data[1] ^ data[2] ^ data[3]

    # p4 jest obliczany jako XOR wszystkich bitów danych i pozostałych bitów parzystości.
    p4 = data[0] ^ data[1] ^ data[2] ^ data[3] ^ p1 ^ p2 ^ p3

    # Zwraca 8-bitowy zakodowany ciąg: bity parzystości i oryginalne bity danych.
    return [p1, p2, data[0], p3, data[1], data[2], data[3], p4]

def main():
    # Sprawdza, czy skrypt został uruchomiony z odpowiednią liczbą argumentów.
    if len(sys.argv) != 3:
        raise Exception("Wrong argument count")
    
    # Przypisuje ścieżki do plików wejściowego i wyjściowego.
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    # Otwiera plik wejściowy i czyta zawartość jako bajty.
    with open(input_file_path, "rb") as file:
        input_bytes = file.read()
    
    # Konwertuje odczytane bajty na ciąg bitów.
    input_bits = bitarray()
    input_bits.frombytes(input_bytes)

    # Inicjalizuje bitarray do przechowywania zakodowanych danych.
    packet = bitarray()
    encoding = bitarray()

    # Iteruje przez każdy bit danych wejściowych.
    for bit in input_bits:
        # Dodaje bit do tymczasowego pakietu.
        packet.append(bit)

        # Gdy pakiet osiągnie 4 bity, koduje go i resetuje do kolejnej partii.
        if len(packet) == 4:
            res = hamming_encoding(packet)
            encoding.extend(res)
            packet.clear()

    # Otwiera plik wyjściowy i zapisuje zakodowane bity.
    with open(output_file_path, "wb") as file:
        file.write(encoding.tobytes())

# Uruchamia główną funkcję programu, jeśli skrypt jest wywołany bezpośrednio.
if __name__ == "__main__":
    main()
