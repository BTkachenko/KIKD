import numpy as np
import sys

def calculate_mse(original, decoded):
    return np.mean((original - decoded) ** 2)

def calculate_snr(original, mse):
    signal_power = np.mean(original ** 2)
    return 10 * np.log10(signal_power / mse) if mse != 0 else float('inf')

def main(original_image_path, decoded_image_path):
    original = np.fromfile(original_image_path, dtype=np.uint8).reshape((200, 133, 3))  # Adjust shape as needed
    decoded = np.fromfile(decoded_image_path, dtype=np.uint8).reshape((200, 133, 3))  # Adjust shape as needed
    mse = calculate_mse(original, decoded)
    snr = calculate_snr(original, mse)
    print(f"MSE = {mse}")
    print(f"SNR = {snr} dB")

if __name__ == "__main__":
    original_path = sys.argv[1]
    decoded_path = sys.argv[2]
    main(original_path, decoded_path)
