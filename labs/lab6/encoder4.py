import sys
import math

def write_encoded_data(encoded_data, filename):
    try:
        with open(filename, 'wb') as file:
            for item in encoded_data:
                blue, green, red = item
                # Zamień wartości z zakresu -128 do 127 na 0 do 255
                blue = blue + 128
                green = green + 128
                red = red + 128
                # Zapisuj trzy składowe koloru jako wartości 8-bitowe
                file.write(bytes([blue, green, red]))
        print(f'Dane zapisane do pliku: {filename}')
    except Exception as e:
        print(f'Błąd podczas zapisywania danych do pliku: {str(e)}')

def read_encoded_data(filename):
    try:
        encoded_data = []
        with open(filename, 'rb') as file:
            while True:
                data = file.read(3)  # Czytaj 3 bajty (BGR)
                if not data:
                    break
                blue, green, red = data
                # Przywróć wartości z zakresu 0 do 255 na -128 do 127
                blue = blue - 128
                green = green - 128
                red = red - 128
                encoded_data.append((blue, green, red))
        return encoded_data
    except Exception as e:
        print(f'Błąd podczas odczytywania danych z pliku: {str(e)}')
        return []


def read_TGA(filename):
    with open(filename,"rb") as f:
        byte=f.read()
        data=[int(x) for x in byte]
        image_width = data[13]*256 + data[12]
        image_height = data[15]*256 + data[14]
        header = byte[:18]
        source = data[18:18+(3*image_height*image_width)]
        footer = byte[18+(3*image_height*image_width):] 
        source.reverse() #Własność tych plików, bez reverse byłoby B G R
        pixels_list=[]
        for i in range(image_height):
            for j in range(image_width):
                index = (image_width*i+j)*3
                pixels_list.append((source[index],
                                    source[index+1],
                                    source[index+2])
                                    )
        return(header,footer,pixels_list, image_width, image_height)

def write_TGA(header,source_to_bytes,footer,filename):
    with open(filename,"wb") as out:
        out.write(header)
        out.write(source_to_bytes)
        out.write(footer)








# Filtr dolnoprzepustowy: Uśrednia wartości pikseli w obrębie 3x3 okna wokół każdego piksela.
# Używany do wygładzania obrazu i redukcji szumu.
def low_pass_filter(pixels, width, height):
    filtered_pixels = []
    for y in range(height):
        for x in range(width):
            sum_r, sum_g, sum_b = 0, 0, 0
            count = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        r, g, b = pixels[ny * width + nx]
                        sum_r += r
                        sum_g += g
                        sum_b += b
                        count += 1
            # Upewnij się, że zaokrąglenie jest wykonane w taki sposób, aby nie obniżać jasności
            avg_r = round(sum_r / count)
            avg_g = round(sum_g / count)
            avg_b = round(sum_b / count)
            filtered_pixels.append((avg_r, avg_g, avg_b))
    return filtered_pixels


# Filtr górnoprzepustowy: Wyostrza obraz poprzez podkreślenie różnic intensywności pikseli.
# Oblicza średnią wartość pikseli wokół każdego piksela i odejmuje ją od wartości aktualnego piksela.

def high_pass_filter(pixels, width, height):
    filtered_pixels = []
    for y in range(height):
        for x in range(width):
            original = pixels[y * width + x]
            sum_r, sum_g, sum_b = 0, 0, 0
            count = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        r, g, b = pixels[ny * width + nx]
                        sum_r += r
                        sum_g += g
                        sum_b += b
                        count += 1
            avg_r, avg_g, avg_b = sum_r // count, sum_g // count, sum_b // count
            filtered_r = min(255, max(0, original[0] + (original[0] - avg_r)))
            filtered_g = min(255, max(0, original[1] + (original[1] - avg_g)))
            filtered_b = min(255, max(0, original[2] + (original[2] - avg_b)))
            filtered_pixels.append((filtered_r, filtered_g, filtered_b))
    return filtered_pixels


def distance_euclid(source,variable):
    return sum((sourceElement-variableElement) ** 2
    for sourceElement, variableElement 
    in zip(source, variable))

# Kodowanie różnicowe dla pojedynczego kanału koloru.
 # Oblicza różnicę między kolejnymi wartościami pikseli, ograniczając wartości różnic do określonego zakresu.
 
def diff_encoding_color(pixels,bits):
    prev = 0
    max_value = 2**(bits)-1
    min_value = -2**(bits)
    diffs = []
    result = []
    M = list(range(min_value,max_value))
    for item in pixels:
        temp = item - prev
        current = min(M, key=lambda x:abs(x-temp))
        diffs.append(current)
        prev = sum(diffs)

    
    return diffs



def pixels_to_bytes(pixels):
    pixels.reverse()
    pixels_bytes = [] 
    for pixel in pixels:
        for color in reversed(pixel):
            color_clamped = max(0, min(255, color))  # Ograniczenie wartości do zakresu 0-255
            pixels_bytes.append(color_clamped)
    return bytes(pixels_bytes)

# Kodowanie różnicowe dla całego obrazu.
# Stosuje kodowanie różnicowe oddzielnie dla każdego kanału koloru (RGB).
def diff_encoding(pixels,bits):
    result = []
    result_blue = []
    result_green = []
    result_red = []
    for item in pixels:
        result_blue.append(item[0])
        result_green.append(item[1])
        result_red.append(item[2])
    result_blue = diff_encoding_color(result_blue,bits)
    result_green = diff_encoding_color(result_green,bits)
    result_red = diff_encoding_color(result_red,bits)

    for i in range(len(result_blue)):
        result.append((result_blue[i],result_green[i],result_red[i]))
    return result

# Dekodowanie różnicowe dla pojedynczego kanału koloru.
# Odwraca proces kodowania różnicowego, odtwarzając oryginalne wartości pikseli.

def diff_decoding_color(diffs):
    result = []
    for i in range(len(diffs)):
        result.append(sum(diffs[:i+1]))
    return result



# Dekodowanie różnicowe dla całego obrazu.
# Stosuje dekodowanie różnicowe oddzielnie dla każdego kanału koloru (RGB).

def diff_decoding(diffs):
    result = []
    result_blue = []
    result_green = []
    result_red = []
    for item in diffs:
        result_blue.append(item[0])
        result_green.append(item[1])
        result_red.append(item[2])
    result_blue = diff_decoding_color(result_blue)
    result_green = diff_decoding_color(result_green)
    result_red = diff_decoding_color(result_red)

    for i in range(len(result_blue)):
        result.append((result_blue[i],result_green[i],result_red[i]))
    return result

def msr_result(original,new):
    result = 0
    return (1 / len(original)) * sum([distance_euclid(original[i], new[i]) for i in range(len(original))])

def msr_color(original,new,i):
    result = 0
    for j in range(len(original)):
        result += (original[j][i]-new[j][i])**2
    return result/len(original)

def msr_snr(original):
    result = 0
    ref = [0,0,0]
    return (1 / len(original)) * sum([distance_euclid(original[i], ref) for i in range(len(original))])
    
def msr_snr_color(original,i):
    result = 0
    for j in range(len(original)):
        result += (original[j][i]-0)**2
    return result/len(original)

# Kwantyzacja równomierna dla pojedynczej wartości.
# Przekształca wartość piksela do mniejszej liczby poziomów, bazując na ilości bitów kwantyzatora.
def uniform_quantization(value, bits):
    max_val = 2 ** bits - 1
    # Normalizacja wartości do zakresu 0-1
    normalized_value = value / 255.0
    # Przeskalowanie do nowego zakresu i zaokrąglenie do najbliższej wartości całkowitej
    quantized_value = round(normalized_value * max_val)
    # Ponowne skalowanie do zakresu 0-255
    rescaled_value = int((quantized_value / max_val) * 255)
    return rescaled_value


# Stosuje kwantyzację równomierną dla całego obrazu.
# Każdy piksel jest przetwarzany oddzielnie, z zastosowaniem kwantyzacji do każdego kanału koloru.
def apply_uniform_quantization(pixels, bits):
    return [(uniform_quantization(pixel[0], bits),
             uniform_quantization(pixel[1], bits),
             uniform_quantization(pixel[2], bits)) for pixel in pixels]




def non_uniform_quantization(value, bits):
    # Definiowanie zakresów kwantyzacji
    thresholds = [0.3, 0.6, 0.9]  # Progi podziału pasm
    scales = [0.5, 1.0, 1.5, 2.0]  # Skale kwantyzacji dla różnych pasm

    # Normalizacja wartości do zakresu 0-1
    normalized_value = value / 255.0

    # Dobór skali kwantyzacji w zależności od pasma
    scale = None
    for i, threshold in enumerate(thresholds):
        if normalized_value < threshold:
            scale = scales[i]
            break
    if scale is None:
        scale = scales[-1]

    max_val = 2 ** (bits) - 1
    quantized_value = round(normalized_value * max_val * scale) / scale

    # Skalowanie z powrotem do zakresu 0-255
    rescaled_value = round(quantized_value / max_val * 255)
    return rescaled_value

def apply_non_uniform_quantization(image, bits):
    return [(non_uniform_quantization(pixel[0], bits),
             non_uniform_quantization(pixel[1], bits),
             non_uniform_quantization(pixel[2], bits)) for pixel in image]





def print_stats(color, original, processed):
    mse = msr_result(original, processed)
    snr = 10 * math.log10(msr_snr(original))
    print(f"{color} - MSE: {mse}, SNR: {snr} dB")

def main():
    if len(sys.argv) != 5:
        print("Usage: main.py <input_file> <output_file_low_pass> <output_file_high_pass> <quantizer_bits>")
        return
    file = sys.argv[1]
    out_low_pass = sys.argv[2]
    out_high_pass = sys.argv[3]
    bits = int(sys.argv[4])

    header, footer, pixels, image_width, image_height = read_TGA(file)

    # Zastosowanie filtrów
    low_passed = low_pass_filter(pixels, image_width, image_height)
    high_passed = high_pass_filter(pixels, image_width, image_height)

    # Kodowanie różnicowe i kwantyzacja równomierna
    encoded_low_passed = diff_encoding(low_passed, bits)
    write_encoded_data(encoded_low_passed, "encoded_low_pass.bin")
    encoded_data = read_encoded_data("encoded_low_pass.bin")
    decoded_low_passed = diff_decoding(encoded_data)
    quantized_high_passed = apply_non_uniform_quantization(high_passed, bits)

    # Obliczanie MSE i SNR dla filtru dolnoprzepustowego
    msr_low = msr_result(pixels, decoded_low_passed)
    msr_snr_low = msr_snr(pixels)

    # Obliczanie MSE i SNR dla filtru górnoprzepustowego
    msr_high = msr_result(pixels, quantized_high_passed)
    msr_snr_high = msr_snr(pixels)

    # Obliczanie MSE i SNR dla filtru dolnoprzepustowego
    print("Filtr dolnoprzepustowy (Low Pass Filter):")
    print_stats("Całkowity", pixels, decoded_low_passed)
    print_stats("Czerwony", [(p[0],) for p in pixels], [(p[0],) for p in decoded_low_passed])
    print_stats("Zielony", [(p[1],) for p in pixels], [(p[1],) for p in decoded_low_passed])
    print_stats("Niebieski", [(p[2],) for p in pixels], [(p[2],) for p in decoded_low_passed])

    # Obliczanie MSE i SNR dla filtru górnoprzepustowego
    print("\nFiltr górnoprzepustowy (High Pass Filter):")
    print_stats("Całkowity", pixels, quantized_high_passed)
    print_stats("Czerwony", [(p[0],) for p in pixels], [(p[0],) for p in quantized_high_passed])
    print_stats("Zielony", [(p[1],) for p in pixels], [(p[1],) for p in quantized_high_passed])
    print_stats("Niebieski", [(p[2],) for p in pixels], [(p[2],) for p in quantized_high_passed])


    # Zapisywanie wyników do plików
    write_TGA(header, pixels_to_bytes(decoded_low_passed), footer, out_low_pass)
    write_TGA(header, pixels_to_bytes(quantized_high_passed), footer, out_high_pass)

if __name__ == '__main__':
    main()
