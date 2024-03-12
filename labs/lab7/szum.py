import sys
import random
from bitarray import bitarray

def main():

    if len(sys.argv) != 4:
        raise Exception("Wrong argument count")

    p = float(sys.argv[1])
    input_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    # Otwiera plik wejściowy, czyta jego zawartość i przechowuje jako bytearray.
    with open(input_file_path, "rb") as file:
        file_bytes = bytearray(file.read())
    
    # Iteruje przez każdy bajt w pliku.
    for i, byte in enumerate(file_bytes):
        # Iteruje przez każdy bit w bajcie.
        for n in range(8):
            # Decyduje losowo, czy wprowadzić błąd na podstawie podanego prawdopodobieństwa.
            if random.random() < p:
                # Wprowadza błąd bitowy poprzez wykonanie operacji XOR na konkretnym bicie.
                file_bytes[i] ^= 1 << n

    # Otwiera plik wyjściowy i zapisuje zmodyfikowany bytearray.
    with open(output_file_path, "wb") as file:
        file.write(file_bytes)

# Uruchamia główną funkcję programu, jeśli skrypt jest wywołany bezpośrednio.
if __name__ == "__main__":
    main()
