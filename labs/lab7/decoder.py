import sys
from bitarray import bitarray

def hamming_decoding(data):
    # Sprawdza, czy długość danych wejściowych to dokładnie 8 bitów.
    if len(data) != 8:
        raise ValueError("Data length is not 8")

    # Rozdziela bity na bity parzystości i bity danych.
    p1, p2, d1, p3, d2, d3, d4, p4 = data

    # Oblicza bity parzystości na podstawie bitów danych.
    p1_calc = d1 ^ d2 ^ d4
    p2_calc = d1 ^ d3 ^ d4
    p3_calc = d2 ^ d3 ^ d4
    p4_calc = d1 ^ d2 ^ d3 ^ d4 ^ p1 ^ p2 ^ p3

    # Wyznacza pozycję błędu.
    error_pos = 0
    if p1 != p1_calc:
        error_pos += 1
    if p2 != p2_calc:
        error_pos += 2
    if p3 != p3_calc:
        error_pos += 4

    # Wykonuje korekcję błędu jeśli to możliwe.
    if p4 != p4_calc:
        if error_pos == 0:
            data[7] = not data[7]  # Korekcja błędu w bicie parzystości.
        else:
            data[error_pos - 1] = not data[error_pos - 1]  # Korekcja błędu w bicie danych.
    elif error_pos != 0:
        return (False, [d1, d2, d3, d4])  # Wykryto podwójny błąd bitowy.

    return (True, [d1, d2, d3, d4])  # Zwraca bity danych.

def main():
    # Sprawdza, czy skrypt został uruchomiony z odpowiednią liczbą argumentów.
    if len(sys.argv) != 3:
        raise Exception("Wrong argument count")
    
    # Przypisuje ścieżki do plików wejściowego i wyjściowego.
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    # Otwiera plik wejściowy i czyta zawartość jako bajty.
    with open(input_file_path, "rb") as file:
        input_bytes = file.read()
    
    # Konwertuje odczytane bajty na ciąg bitów.
    input_bits = bitarray()
    input_bits.frombytes(input_bytes)

    packet = bitarray()
    decoding = bitarray()
    uncorrectable = 0

    # Iteruje przez każdy bit danych wejściowych.
    for bit in input_bits:
        # Dodaje bit do tymczasowego pakietu.
        packet.append(bit)

        # Gdy pakiet osiągnie 8 bitów, dekoduje go.
        if len(packet) == 8:
            success, res = hamming_decoding(packet)
            if not success:
                uncorrectable += 1  # Liczy błędy, których nie można skorygować.
            decoding.extend(res)
            packet.clear()

    # Wyświetla liczbę błędów, których nie można skorygować.
    print("Uncorrectable Errors:", uncorrectable)

    # Otwiera plik wyjściowy i zapisuje zdekodowane bity.
    with open(output_file_path, "wb") as file:
        file.write(decoding.tobytes())

# Uruchamia główną funkcję programu, jeśli skrypt jest wywołany bezpośrednio.
if __name__ == "__main__":
    main()
