import struct
import numpy as np
import sys
import math
import random

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


def calculate_mse(original, quantized):
    """Oblicza błąd średniokwadratowy (MSE)."""
    return np.mean((original - quantized) ** 2)

def calculate_snr(image, mse):
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


def manhattan_distance(p1, p2):
    return np.sum(np.abs(p1 - p2))

def initialize_centroids(image, num_colors):
    unique_colors = np.unique(image.reshape(-1, 3), axis=0)
    return unique_colors[np.random.choice(len(unique_colors), num_colors, replace=False)]

def assign_pixels_to_centroids(image, centroids):
    flat_image = image.reshape(-1, 3)
    labels = np.argmin([[manhattan_distance(pixel, centroid) for centroid in centroids] for pixel in flat_image], axis=1)
    return labels.reshape(image.shape[0], image.shape[1])

def update_centroids(image, labels, num_colors):
    new_centroids = np.zeros((num_colors, 3))
    for i in range(num_colors):
        pixels = image[labels == i]
        if len(pixels) > 0:
            new_centroids[i] = np.mean(pixels, axis=0)
    return new_centroids

def lbg_quantization(image, num_colors):
    # Inicjalizacja centroidów
    centroids = np.random.randint(0, 256, (num_colors, 3))
    for _ in range(10):  # Ilość iteracji
        # Przypisanie pikseli do najbliższych centroidów
        flat_image = image.reshape(-1, 3)
        distances = np.array([np.sum(np.abs(pixel - centroids), axis=1) for pixel in flat_image])
        labels = np.argmin(distances, axis=1)

        # Aktualizacja centroidów
        for i in range(num_colors):
            centroids[i] = np.mean(flat_image[labels == i], axis=0) if len(flat_image[labels == i]) > 0 else centroids[i]

    # Tworzenie skwantyzowanego obrazu
    quantized_image = centroids[labels].reshape(image.shape)
    return quantized_image.astype(np.uint8)

def main(input_image_path, output_image_path, num_colors_pow):
    original = read_tga(input_image_path)
    num_colors = 2 ** num_colors_pow

    # Kwantyzacja wektorowa
    quantized = lbg_quantization(original, num_colors)

    # Obliczanie MSE i SNR
    mse = calculate_mse(original, quantized)
    snr = calculate_snr(original, mse)

    # Zapisywanie przetworzonego obrazu
    write_tga(output_image_path, quantized)

    # Wypisywanie wyników
    print(f"MSE = {mse}")
    print(f"SNR = {snr} dB")

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    num_colors_pow = int(sys.argv[3])
    main(input_path, output_path, num_colors_pow)
