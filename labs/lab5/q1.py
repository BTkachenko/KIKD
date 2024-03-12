import struct
import numpy as np
import sys
import math

def read_tga(filename):
    """Wczytuje obraz TGA z pliku."""
    with open(filename, 'rb') as f:
        f.seek(12)  # Pomijanie nagłówka
        width, height = struct.unpack('2H', f.read(4))
        f.seek(2, 1)
        data = np.frombuffer(f.read(), dtype=np.uint8)
        return data.reshape((height, width, 3))

def write_tga(filename, data):
    with open(filename, 'wb') as f:
        # Nagłówek TGA
        header = struct.pack(
            'B'   # ID length
            'B'   # No color map
            'B'   # Uncompressed true-color image
            '2H'  # Color map specification
            '2H'  # X-origin, Y-origin
            '2H'  # Width, Height
            'B'   # Pixel depth
            'B',  # Image descriptor
            0,    # ID length
            0,    # No color map
            2,    # Uncompressed true-color image
            0, 0, # Color map specification
            0, 0, # X-origin, Y-origin
            data.shape[1], data.shape[0],  # Width, Height
            24,   # Pixel depth (24 bits: 8 red, 8 green, 8 blue)
            32    # Image descriptor (8th bit: origin in upper left corner)
        )
        f.write(header)
        f.write(data[::-1, :, :].astype(np.uint8).tobytes())  # Flip the image vertically

def quantize_channel(channel, bits):
    """Kwantyzuje dany kanał koloru."""
    if bits == 0:
        return np.zeros_like(channel)
    levels = 2 ** bits
    quantized = np.floor(channel / (256 / levels)) * (256 / levels)
    return quantized

def calculate_mse(original, quantized):
    """Oblicza błąd średniokwadratowy (MSE)."""
    return np.mean((original - quantized) ** 2)

def snr(image, mse):
    """Oblicza stosunek sygnału do szumu (SNR) dla obrazu."""
    signal_power = np.sum(image.astype(np.float64) ** 2) / image.size
    return 10 * math.log10(signal_power / mse) if mse != 0 else float('inf')

def print_snr(snr_value):
    """Drukowanie wartości SNR z obsługą nieskończonych i niepoprawnych wartości."""
    if snr_value == float('inf'):
        return 'inf dB'
    elif snr_value <= 0:  # Unikaj logarytmu z wartości niepoprawnych
        return 'undefined'
    else:
        return f"{snr_value} ({10 * np.log10(snr_value)} dB)" if snr_value != 0 else "0 (undefined)"

def main(input_image_path, output_image_path, red_bits, green_bits, blue_bits):
    original = read_tga(input_image_path)

    """Główna funkcja programu."""
    original = read_tga(input_image_path)

    # Kwantyzacja kanałów w formacie BGR
    b, g, r = original[:, :, 0], original[:, :, 1], original[:, :, 2]
    qb = quantize_channel(b, blue_bits)
    qg = quantize_channel(g, green_bits)
    qr = quantize_channel(r, red_bits)
    quantized = np.stack([qb, qg, qr], axis=2)

    # Zapisywanie przetworzonego obrazu
    write_tga(output_image_path, quantized)

    # Obliczanie MSE i SNR
    mse_total = calculate_mse(original, quantized)
    mse_r = calculate_mse(original[:, :, 2], quantized[:, :, 2])
    mse_g = calculate_mse(original[:, :, 1], quantized[:, :, 1])
    mse_b = calculate_mse(original[:, :, 0], quantized[:, :, 0])

    snr_total = snr(original, mse_total)
    snr_r = snr(original[:, :, 2], mse_r)
    snr_g = snr(original[:, :, 1], mse_g)
    snr_b = snr(original[:, :, 0], mse_b)

    # Wypisywanie wyników
    print(f"mse = {mse_total}")
    print(f"mse(r) = {mse_r}")
    print(f"mse(g) = {mse_g}")
    print(f"mse(b) = {mse_b}")
    print(f"SNR = {print_snr(snr_total)}")
    print(f"SNR(r) = {print_snr(snr_r)}")
    print(f"SNR(g) = {print_snr(snr_g)}")
    print(f"SNR(b) = {print_snr(snr_b)}")

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    r_bits = int(sys.argv[3])
    g_bits = int(sys.argv[4])
    b_bits = int(sys.argv[5])
    main(input_path, output_path, r_bits, g_bits, b_bits)