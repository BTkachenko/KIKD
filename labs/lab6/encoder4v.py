import sys
import math

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



def non_uniform_quantization(value, bits):
    max_val = 2 ** bits 
    normalized_value = value / 255.0

    # Dostosowanie krzywej kwantyzacji w zależności od wartości piksela
    if normalized_value < 0.3:
        # Więcej poziomów kwantyzacji dla bardzo ciemnych wartości
        quantized_value = (normalized_value ** 3) * max_val
    elif normalized_value < 0.7:
        # Umiarkowana kwantyzacja dla średnich wartości
        quantized_value = (normalized_value ** 2) * max_val
    else:
        # Mniej poziomów kwantyzacji dla jasnych wartości
        quantized_value = normalized_value * max_val

    return int(quantized_value)



def apply_non_uniform_quantization(pixels, bits):
    return [(non_uniform_quantization(pixel[0], bits),
             non_uniform_quantization(pixel[1], bits),
             non_uniform_quantization(pixel[2], bits)) for pixel in pixels]


def distance_euclid(source,variable):
    return sum((sourceElement-variableElement) ** 2
    for sourceElement, variableElement 
    in zip(source, variable))

def diff_encoding_color(pixels,bits):
    prev = 0
    max_value = 2**(bits-1)-1
    min_value = -2**(bits-1)
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

def diff_decoding_color(diffs):
    result = []
    for i in range(len(diffs)):
        result.append(sum(diffs[:i+1]))
    return result

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


def uniform_quantization(value, bits):
    max_val = 2 ** bits - 1
    quantized_value = int(value / 255 * max_val)
    return quantized_value

def apply_uniform_quantization(pixels, bits):
    return [(uniform_quantization(pixel[0], bits),
             uniform_quantization(pixel[1], bits),
             uniform_quantization(pixel[2], bits)) for pixel in pixels]


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
    decoded_low_passed = diff_decoding(encoded_low_passed)
    quantized_high_passed = apply_uniform_quantization(high_passed, bits)

    # Obliczanie MSE i SNR dla filtru dolnoprzepustowego
    msr_low = msr_result(pixels, decoded_low_passed)
    msr_snr_low = msr_snr(pixels)

    # Obliczanie MSE i SNR dla filtru górnoprzepustowego
    msr_high = msr_result(pixels, quantized_high_passed)
    msr_snr_high = msr_snr(pixels)

    # Wypisywanie statystyk
    print("Filtr dolnoprzepustowy (Low Pass Filter):")
    print("MSE= ", msr_low)
    print("SNR= ", 10 * math.log10(msr_snr_low))

    print("\nFiltr górnoprzepustowy (High Pass Filter):")
    print("MSE= ", msr_high)
    print("SNR= ", 10 * math.log10(msr_snr_high))

    # Zapisywanie wyników do plików
    write_TGA(header, pixels_to_bytes(decoded_low_passed), footer, out_low_pass)
    write_TGA(header, pixels_to_bytes(quantized_high_passed), footer, out_high_pass)

if __name__ == '__main__':
    main()
