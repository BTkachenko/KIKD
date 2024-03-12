from PIL import Image
import numpy as np
import sys
import struct

def differential_coding(image):
    """
    Apply differential coding to the image.
    Each pixel value is replaced with the difference from the previous pixel.
    """
    diff_encoded = np.zeros_like(image, dtype=np.int16)
    diff_encoded[:, 0, :] = image[:, 0, :]  # First column remains the same
    for i in range(1, image.shape[1]):
        diff_encoded[:, i, :] = image[:, i, :] - image[:, i - 1, :]
    return diff_encoded

def uniform_quantization(image, k):
    """
    Apply uniform quantization to the image.
    Each pixel value is quantized to a fixed number of levels determined by k.
    """
    levels = 2 ** k
    step = 256 / levels
    quantized_image = (image // step) * step + step / 2
    return quantized_image.astype(np.uint8)

def encode_image(image, k):
    """
    Encode the image using differential coding and uniform quantization.
    """
    diff_encoded = differential_coding(image)
    quantized_diff_encoded = np.zeros_like(diff_encoded, dtype=np.uint8)
    for channel in range(image.shape[2]):
        quantized_diff_encoded[:, :, channel] = uniform_quantization(diff_encoded[:, :, channel], k)
    return quantized_diff_encoded

def main(input_image_path, output_file, k):
    with Image.open(input_image_path) as img:
        image = np.array(img)

    encoded_image = encode_image(image, k)

    with open(output_file, 'wb') as f:
        # Zapisanie wymiarów obrazu na początku pliku
        f.write(struct.pack('2I', image.shape[0], image.shape[1]))
        f.write(encoded_image.tobytes())

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_file = sys.argv[2]
    k = int(sys.argv[3])
    main(input_path, output_file, k)
