import numpy as np
import struct
import sys
from PIL import Image

def read_encoded_data_from_file(encoded_file):
    """
    Read the encoded image data and quantization intervals from the file.
    """
    with open(encoded_file, 'rb') as f:
        # Read the shape of the image
        height, width = struct.unpack('2I', f.read(8))

        # Read the encoded image data
        encoded_image = np.frombuffer(f.read(height * width * 3), dtype=np.uint8).reshape((height, width, 3))

        # Read the quantization intervals
        remaining_data = f.read()
        intervals = [struct.unpack('2I', remaining_data[i:i+8]) for i in range(0, len(remaining_data), 8)]
        half = len(intervals) // 2
        low_intervals = intervals[:half]
        high_intervals = intervals[half:]

    return encoded_image, low_intervals, high_intervals

def dequantize_image(image, intervals):
    """
    Dequantize the image using the given intervals.
    """
    dequantized_image = np.zeros_like(image)

    for low, high in intervals:
        mask = np.logical_and(image >= low, image <= high)
        dequantized_image[mask] = (low + high) // 2

    return dequantized_image

def decode_image(encoded_image, low_intervals, high_intervals):
    """
    Decode the image using the low and high quantization intervals.
    """
    # Separate the encoded image back into low-passed and high-passed components
    # This is a simplified approach and may not perfectly separate the components
    low_passed_approx = dequantize_image(encoded_image, low_intervals)
    high_passed_approx = dequantize_image(encoded_image, high_intervals)

    # Combine the components to reconstruct the original image
    reconstructed_image = low_passed_approx + high_passed_approx
    return reconstructed_image

def main(encoded_file, output_image_path):
    encoded_image, low_intervals, high_intervals = read_encoded_data_from_file(encoded_file)
    decoded_image = decode_image(encoded_image, low_intervals, high_intervals)
    
    # Save the decoded image using PIL (or any other method to save the image)
    Image.fromarray(decoded_image).save(output_image_path)

if __name__ == "__main__":
    encoded_file = sys.argv[1]
    output_image_path = sys.argv[2]
    main(encoded_file, output_image_path)
