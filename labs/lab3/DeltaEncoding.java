import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;

public class DeltaEncoding implements UniversalEncoding {

    private int buffer = 0;
    private int bitsInBuffer = 0;
    private final BufferedInputStream in;
    private final BufferedOutputStream out;
    private int bitsInReadBuffer = 0;
    private int readBuffer = 0;

    DeltaEncoding(BufferedInputStream in, BufferedOutputStream out) {
        this.in = in;
        this.out = out;
    }


    @Override
    public void outputInteger(int value) throws IOException {
        value += 1;
        int temp = value;
        int n = 0;
        while(temp > 0){
            temp = temp >> 1;
            n++;
        }

        temp = n;
        int lenght = 0;
        while (temp > 0){
            temp = temp >> 1;
            lenght++;
        }

        for (int i = 0; i < lenght - 1; i++){
            send(0);
        }
        for (int i = 0; i < lenght; i++){
            int bit = n >> lenght - 1 - i;
            send(bit);
        }
        for (int i = 0; i < n - 1; i++){
            int bit = value >> n - 2 - i;
            send(bit);
        }
    }

    @Override
    public int readInteger() throws IOException {
        int count = 0;
        int nextBit = readNextBit();
        while (nextBit == 0){
            count++;
            nextBit = readNextBit();
            if (nextBit == -1){
                return -1;
            }
        }
        int temp = 1;
        for (int i = 0; i < count; i++){
            temp = temp << 1;
            nextBit = readNextBit();
            if (nextBit == -1){
                return -1;
            }
            temp |= nextBit;
        }
        // długość naszej liczby
        int n = temp;

        temp = 1;
        for (int i = 0; i < n - 1; i++){
            temp = temp << 1;
            nextBit = readNextBit();
            if (nextBit == -1){
                return -1;
            }
            temp |= nextBit;
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
