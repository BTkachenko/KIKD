import java.io.*;
import java.util.*;

public class Encoder {

    private static double calculateEntropy(File file) throws IOException {
        Map<Integer, Long> frequencyMap = new HashMap<>();
        long totalBytes = file.length();
        double entropy = 0.0;

        try (BufferedInputStream inputStream = new BufferedInputStream(new FileInputStream(file))) {
            int currentByte;
            while ((currentByte = inputStream.read()) != -1) {
                frequencyMap.put(currentByte, frequencyMap.getOrDefault(currentByte, 0L) + 1);
            }
        }

        for (Map.Entry<Integer, Long> entry : frequencyMap.entrySet()) {
            double probability = entry.getValue() / (double) totalBytes;
            entropy -= probability * (Math.log(probability) / Math.log(2));
        }

        return entropy;
    }

    // Zmienne globalne i stałe
    private static long totalCount; // Całkowita liczba symboli
    private static long l = 0; // Dolna granica przedziału
    private static long u = 0xffffffffL; // Górna granica przedziału
    private static final long[] dict = new long[257]; // Słownik frekwencji symboli
    private static final long[] cumCount = new long[258]; // Skumulowane liczniki dla symboli
    private static int scale3; // Zmienna do skalowania granic
    private static int buffer = 0; // Bufor do przechowywania bitów wyjściowych
    private static int bitsInBuffer = 0; // Liczba bitów w buforze
    private static BufferedOutputStream outStream; // Strumień wyjściowy dla danych zakodowanych
    private static long bytesRead = 0; // Liczba przeczytanych bajtów z danych wejściowych
    private static long totalBitsWritten = 0; // Placeholder for actual bits written

    public static void main(String[] args) throws IOException {
        // Inicjalizacja słowników
        totalCount = Commons.initializeDictionaries(dict, cumCount);
        // Pliki wejściowe i wyjściowe
        File initialFile = new File(args[0]);
        File destination = new File(args[1]);
        try {
            // Przygotowanie strumieni
            BufferedInputStream stream = new BufferedInputStream(new DataInputStream(new FileInputStream(initialFile)));
            outStream = new BufferedOutputStream(new PrintStream(destination));
            // Czytanie danych i kodowanie
            int b = stream.read();
            while (b != -1) {
                bytesRead++;
                encode(b); // Kodowanie pojedynczego bajtu
                totalCount = Commons.updateDict(b, totalCount, dict, cumCount); // Aktualizacja słownika po każdym bajcie
                b = stream.read();
            }
            // Kodowanie specjalnego symbolu końca pliku
            encode(256);
            // Zakończenie kodowania i zapis pozostałych bitów
            writeReminder();
            // Zamknięcie strumieni
            stream.close();
            outStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // Wydrukowanie statystyk
        double entropy = calculateEntropy(initialFile);
        System.out.println("Entropy: " + entropy); // Entropia danych wejściowych
        double averageCodeLength = (double) totalBitsWritten / bytesRead;
        System.out.println("Average Code Length: " + averageCodeLength + " bits"); // Średnia długość kodowania
        double compressionRatio = (double) bytesRead / (double) destination.length();
        System.out.println("Compression Ratio: " + compressionRatio); // Stopień kompresji
    } 

   


    

/**
 * Wypisuje pozostałe bity do strumienia wyjściowego. Ta metoda jest wywoływana po przetworzeniu wszystkich danych wejściowych,
 * aby upewnić się, że ostatnie bity zostały zapisane.
 */
private static void writeReminder() throws IOException {
    // Musimy zapisać dokładnie 32 bity, aby zakończyć proces kodowania.
    for (int i = 0; i < 32; i++) {
        // Wyślij najbardziej znaczący bit z 'l'.
        send(l >>> 31 & 0x1);
        // Jeśli pozostały jakieś bity skalowania, wyślij je (zainwertowane).
        while (scale3 > 0) {
            send(l >>> 31 & 0x1 ^ 0x1);
            scale3--;
        }
        // Przesuń 'l' w lewo, skutecznie odrzucając najbardziej znaczący bit,
        // który właśnie został wysłany.
        l = l << 1 & 0xffffffffL;
    }
    // Jeśli w buforze pozostały jakieś bity, wyślij je jako ostatni bajt.
    if (bitsInBuffer > 0) {
        outStream.write(buffer << (8 - bitsInBuffer));
        totalBitsWritten += bitsInBuffer; // Aktualizuj tylko faktyczną liczbę zapisanych bitów.
        outStream.flush(); // Upewnij się, że ostatni bajt został zapisany do strumienia wyjściowego.
    }
}


private static void encode(int b) throws IOException {
    // Zapisz obecne dolne ograniczenie przed aktualizacją.
    long prevL = l;
    // Oblicz nowe dolne i górne granice dla bieżącego symbolu.
    l = l + ((u - l + 1) * cumCount[b] / totalCount);
    u = prevL + ((u - prevL + 1) * cumCount[b + 1] / totalCount) - 1;

    // Poniższa pętla będzie działać do momentu, gdy 'l' i 'u' będą miały różne najbardziej znaczące bity,
    // co oznacza, że bieżący przedział jest jednoznacznie określony.
    while ((l & 0x80000000L) == (u & 0x80000000L) || (l & 0x40000000L) == 0x40000000L && (u & 0x40000000L) == 0) {
        if ((l & 0x80000000L) == (u & 0x80000000L)) {
            // Jeśli 'l' i 'u' mają ten sam najbardziej znaczący bit, wyślij ten bit.
            long bit = (l & 0xffffffffL) >>> 31;
            send(bit);
            // Przesuń 'l' i 'u' w lewo, tworząc miejsce na następny bit.
            l = l << 1 & 0xffffffffL;
            u = u << 1 & 0xffffffffL | 0x1L;
            // Wyślij zanegowany bit tyle razy, ile wynosi współczynnik skalowania.
            while (scale3 > 0) {
                send(bit ^ 0x1L);
                scale3--;
            }
        }
        // Jeśli drugi najbardziej znaczący bit 'l' jest ustawiony, a 'u' jest zerowy, może to powodować niejednoznaczność.
        // Ta część zapewnia rozwiązanie tej sytuacji.
        if ((l & 0x40000000L) == 0x40000000L && (u & 0x40000000L) == 0) {
            // Skalowanie E3: Zaneguj drugi najbardziej znaczący bit 'l' i 'u'.
            l = l << 1 & 0xffffffffL ^ 0x80000000L;
            u = u << 1 & 0xffffffffL | 0x1L ^ 0x80000000L;
            scale3++; // Zwiększ 'scale3', ponieważ właśnie rozwiązano warunek E3.
        }
    }
}

/**
 * Wysyła pojedynczy bit do bufora wyjściowego. Kiedy bufor jest pełny (8 bitów), zapisuje go do strumienia wyjściowego.
 *
 * @param bit Bit do wysłania, 0 lub 1.
 */
private static void send(long bit) throws IOException {
    // Rzutowanie bitu na liczbę całkowitą i zachowanie tylko najmniej znaczącego bitu.
    int b = (int) bit & 0x1;
    // Dodanie bitu do bufora i zwiększenie liczby bitów w buforze.
    buffer = buffer << 1 | b;
    bitsInBuffer++;

    // Jeśli bufor jest pełny (8 bitów), zapisz go do strumienia wyjściowego.
    if (bitsInBuffer == 8) {
        outStream.write(buffer);
        totalBitsWritten += 8; // Inkrementacja 'totalBitsWritten' o 8, kiedy bufor jest opróżniany.
        buffer = 0; // Resetowanie bufora.
        bitsInBuffer = 0; // Resetowanie liczby bitów.
    }
}

    
}
