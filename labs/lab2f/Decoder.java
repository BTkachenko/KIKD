
import java.io.*;

public class Decoder {

    private static long totalCount;
    private static long lowerBound = 0;
    private static long upperBound = 0xffffffffL;
    private static final long[] cumulativeCount = new long[258];
    private static final long[] dictionary = new long[257];
    private static int readBuffer = 0;
    private static int bitsInReadBuffer = 0;
    private static long tag;
    private static BufferedOutputStream outputStream;
    private static BufferedInputStream inputStream;
    private static boolean isFinished = false;

    public static void main(String[] args) {
        totalCount = Commons.initializeDictionaries(dictionary, cumulativeCount);

        File inputFile = new File(args[0]);
        File outputFile = new File(args[1]);
        try (DataInputStream dataInputStream = new DataInputStream(new FileInputStream(inputFile));
             BufferedOutputStream bufferedOutputStream = new BufferedOutputStream(new FileOutputStream(outputFile))) {
            tag = Integer.toUnsignedLong(dataInputStream.readInt());
            inputStream = new BufferedInputStream(dataInputStream);
            outputStream = bufferedOutputStream;
            while (!isFinished) {
                decode();
            }
            outputStream.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void decode() throws IOException {
        int symbolIndex = 0;
        long range = ((tag - lowerBound + 1) * totalCount - 1) / (upperBound - lowerBound + 1);
        while (range >= cumulativeCount[symbolIndex + 1]) {
            symbolIndex++;
        }
        if (symbolIndex == 256) {
            isFinished = true;
            return;
        }
        writeSymbol(symbolIndex);
        updateBounds(symbolIndex);
        totalCount = Commons.updateDict(symbolIndex, totalCount, dictionary, cumulativeCount);
    }

    private static void updateBounds(int symbolIndex) throws IOException {
        symbolIndex &= 0xff;
        long previousLowerBound = lowerBound;
        lowerBound = lowerBound + ((upperBound - lowerBound + 1) * cumulativeCount[symbolIndex] / totalCount);
        upperBound = previousLowerBound + ((upperBound - previousLowerBound + 1) * cumulativeCount[symbolIndex + 1] / totalCount) - 1;

        while ((lowerBound & 0x80000000L) == (upperBound & 0x80000000L) || ((lowerBound & 0x40000000L) != 0 && (upperBound & 0x40000000L) == 0)) {
            if ((lowerBound & 0x80000000L) == (upperBound & 0x80000000L)) {
                lowerBound = (lowerBound << 1) & 0xffffffffL;
                upperBound = (upperBound << 1) & 0xffffffffL | 1L;
                updateTag();
            } else if ((lowerBound & 0x40000000L) != 0) {
                lowerBound = (lowerBound << 1) & 0xffffffffL ^ 0x80000000L;
                upperBound = (upperBound << 1) & 0xffffffffL | 1L ^ 0x80000000L;
                updateTag();
                tag ^= 0x80000000L;
            }
        }
    }

    private static void updateTag() throws IOException {
        if (bitsInReadBuffer == 0) {
            readBuffer = inputStream.read();
            if (readBuffer == -1) {
                isFinished = true;
                return;
            }
            bitsInReadBuffer = 8;
        }
        tag = ((tag << 1) & 0xffffffffL) | ((readBuffer >>> 7) & 1);
        readBuffer <<= 1;
        bitsInReadBuffer--;
    }

    private static void writeSymbol(int symbolIndex) throws IOException {
        outputStream.write(symbolIndex);
    }
}
