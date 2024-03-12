import numpy as np
import sys
from PIL import Image
import struct

def differential_decoding(encoded_channel):
    """
    Apply differential decoding to a channel of the encoded image.
    Reconstructs the original pixel values from their differences.
    """
    decoded_channel = np.zeros_like(encoded_channel, dtype=np.uint8)
    decoded_channel[0, :] = encoded_channel[0, :]  # First row remains the same
    for i in range(1, encoded_channel.shape[0]):
        decoded_channel[i, :] = decoded_channel[i - 1, :] + encoded_channel[i, :]
    return decoded_channel

def decode_image(encoded_image):
    """
    Decode the entire image using differential decoding on each color channel.
    """
    decoded_image = np.zeros_like(encoded_image, dtype=np.uint8)
    for channel in range(encoded_image.shape[2]):
        decoded_image[:, :, channel] = differential_decoding(encoded_image[:, :, channel])
    return decoded_image

def main(encoded_file, output_image_path):
    with open(encoded_file, 'rb') as f:
        # Odczytanie wymiarów obrazu
        height, width = struct.unpack('2I', f.read(8))
        encoded_data = f.read()
    encoded_image = np.frombuffer(encoded_data, dtype=np.uint8).reshape((height, width, 3))

    decoded_image = decode_image(encoded_image)

    Image.fromarray(decoded_image).save(output_image_path)

if __name__ == "__main__":
    encoded_file = sys.argv[1]
    output_image_path = sys.argv[2]
    main(encoded_file, output_image_path)