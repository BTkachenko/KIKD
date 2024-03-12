import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;

public class GammaEncoding implements UniversalEncoding {

    private int buffer = 0;
    private int bitsInBuffer = 0;
    private final BufferedInputStream in;
    private final BufferedOutputStream out;
    private int bitsInReadBuffer = 0;
    private int readBuffer = 0;

    GammaEncoding(BufferedInputStream in, BufferedOutputStream out){
        this.in = in;
        this.out = out;
    }

    @Override
    public void outputInteger(int value) throws IOException {
        // nie potrafimy kodować 0
        value += 1;

        int temp = value;
        int length = 0;

        while (temp > 0) {
            length++;
            temp = temp >> 1;
        }

        for (int i = 0; i < length - 1; i++){
                send(0);
        }
        for (int i = 0; i < length; i++){
                int bit = value >> length - 1 - i;
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
        int bit = (readBuffer >> 7 ) & 1;
        readBuffer = readBuffer << 1;
        bitsInReadBuffer--;
        return bit;
    }
}
