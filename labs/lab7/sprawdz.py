import sys

def main():
    if len(sys.argv) != 3:
        raise Exception("Wrong argument count")

    file0_path = sys.argv[1]
    file1_path = sys.argv[2]

    # Otwiera oba pliki w trybie binarnym i czyta ich zawartość.
    with open(file0_path, "rb") as file0, open(file1_path, "rb") as file1:
        buf0 = file0.read()
        buf1 = file1.read()

    # Inicjalizuje licznik błędów.
    errors = 0

    # Iteruje przez każdą parę bajtów z obu plików.
    for byte0, byte1 in zip(buf0, buf1):
        # Dzieli bajty na segmenty górne (4 starsze bity) i porównuje je.
        segment0_upper = byte0 >> 4
        segment1_upper = byte1 >> 4

        # Inkrementuje licznik błędów, jeśli górne segmenty się różnią.
        if segment0_upper != segment1_upper:
            errors += 1

        # Dzieli bajty na segmenty dolne (4 młodsze bity) i porównuje je.
        segment0_lower = (byte0 & 0x0F)
        segment1_lower = (byte1 & 0x0F)

        # Inkrementuje licznik błędów, jeśli dolne segmenty się różnią.
        if segment0_lower != segment1_lower:
            errors += 1

    print("Found {} Errors".format(errors))

if __name__ == "__main__":
    main()
