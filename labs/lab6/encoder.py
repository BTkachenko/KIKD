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
            neighbors_sum = [0, 0, 0]
            count = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors_sum[0] += pixels[ny * width + nx][0]
                        neighbors_sum[1] += pixels[ny * width + nx][1]
                        neighbors_sum[2] += pixels[ny * width + nx][2]
                        count += 1
            filtered_pixels.append(tuple(c // count for c in neighbors_sum))
    return filtered_pixels

def high_pass_filter(pixels, width, height):
    filtered_pixels = []
    for y in range(height):
        for x in range(width):
            center_pixel = pixels[y * width + x]
            neighbors_sum = [0, 0, 0]
            count = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors_sum[0] += pixels[ny * width + nx][0]
                        neighbors_sum[1] += pixels[ny * width + nx][1]
                        neighbors_sum[2] += pixels[ny * width + nx][2]
                        count += 1
            avg_neighbor = tuple(c // count for c in neighbors_sum)
            filtered_pixel = tuple(max(0, min(255, 2 * center - avg)) for center, avg in zip(center_pixel, avg_neighbor))
            filtered_pixels.append(filtered_pixel)
    return filtered_pixels

def non_uniform_quantization(value, bits):
    max_val = 2 ** bits - 1
    return int((value ** 0.5 / 15) * max_val)

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
    max_value = 2**bits
    min_value = -2**bits
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

def main():
    if len(sys.argv) != 4:
        print("Usage: main.py <input_file> <output_file> <quantizer_bits>")
        return
    file = sys.argv[1]
    out = sys.argv[2]
    bits = int(sys.argv[3])

    header, footer, pixels, image_width, image_height = read_TGA(file)

    # Zastosowanie filtrów
    low_passed = low_pass_filter(pixels, image_width, image_height)
    high_passed = high_pass_filter(pixels, image_width, image_height)

    # Kwantyzacja nierównomierna
    quantized_low_passed = apply_non_uniform_quantization(low_passed, bits)
    quantized_high_passed = apply_non_uniform_quantization(high_passed, bits)

    # Kombinacja wyników filtrów
    combined = [(quantized_low_passed[i][0] + quantized_high_passed[i][0],
                 quantized_low_passed[i][1] + quantized_high_passed[i][1],
                 quantized_low_passed[i][2] + quantized_high_passed[i][2]) 
                for i in range(len(pixels))]

    # Kodowanie i dekodowanie
    diffs = diff_encoding(combined, bits)
    result = diff_decoding(diffs)
    
    result = [(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))) for r, g, b in result]
    # Obliczenie MSE i SNR
    msr = msr_result(pixels, result) / 3
    msr_r = msr_color(pixels, result, 2)
    msr_g = msr_color(pixels, result, 1)
    msr_b = msr_color(pixels, result, 0)
    msr_snr_res = msr_snr(pixels) / 3
    msr_snr_r = msr_snr_color(pixels, 2)
    msr_snr_g = msr_snr_color(pixels, 1)
    msr_snr_b = msr_snr_color(pixels, 0)

    print("MSE= ", msr)
    print("MSE (R)= ", msr_r)
    print("MSE (G)= ", msr_g)
    print("MSE (B)= ", msr_b)
    print("SNR= ", 10 * math.log10(msr_snr_res))
    print("SNR (R)= ", 10 * math.log10(msr_snr_r))
    print("SNR (G)= ", 10 * math.log10(msr_snr_g))
    print("SNR (B)= ", 10 * math.log10(msr_snr_b))

    write_TGA(header, pixels_to_bytes(result), footer, out)

if __name__ == '__main__':
    main()
