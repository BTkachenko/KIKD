import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;

public class FibonacciEncoding implements UniversalEncoding {

    private int buffer = 0;
    private int bitsInBuffer = 0;
    private final BufferedInputStream in;
    private final BufferedOutputStream out;
    private int bitsInReadBuffer = 0;
    private int readBuffer = 0;

    private final int[] fibonacciTable = {
            1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986, 102334155, 165580141, 267914296, 433494437, 701408733, 1134903170, 1836311903
    };

    FibonacciEncoding(BufferedInputStream in, BufferedOutputStream out) {
        this.in = in;
        this.out = out;
    }

    @Override
    public void outputInteger(int value) throws IOException {
        value += 1;
        int temp = 0;
        while (value > 0){
            int i = 1;
            while (fibonacciTable[i] <= value){
                i++;
            }
            temp |= 1 << (i - 1);
            value = value - fibonacciTable[i - 1];
        }

        while (temp > 0){
            send(temp);
            temp = temp >> 1;
        }
        send(1);
    }

    @Override
    public int readInteger() throws IOException {
        int temp = 0;
        int counter = 0;
        int previousBit = 0;
        int nextBit = readNextBit();
        if (nextBit == -1){
            return -1;
        }
        while (previousBit == 0 || nextBit == 0){
            if(nextBit == 1){
                temp += fibonacciTable[counter];
            }
            previousBit = nextBit;
            counter++;
            nextBit = readNextBit();
            if (nextBit == -1) {
                return -1;
            }
        }

        return temp - 1;
    }

    @Override
    public void flush() throws IOException {
        buffer = buffer << (8 - bitsInBuffer);
        out.write(buffer);
        out.flush();
    }

    private void send(int bit) throws IOException {
        int b = bit & 0x1;
        buffer = buffer << 1 | b;
        bitsInBuffer++;
        if (bitsInBuffer == 8) {
            out.write(buffer);
            buffer = 0;
            bitsInBuffer = 0;
        }
    }

    private int readNextBit() throws IOException {
        if (bitsInReadBuffer == 0) {
            readBuffer = in.read();
            if (readBuffer == -1) {
                return -1;
            }
            bitsInReadBuffer = 8;
        }
        int bit = (readBuffer >> 7) & 1;
        readBuffer = readBuffer << 1;
        bitsInReadBuffer--;
        return bit;
    }
}
