import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;

public class OmegaEncoding implements UniversalEncoding {

    private int buffer = 0;
    private int bitsInBuffer = 0;
    private final BufferedInputStream in;
    private final BufferedOutputStream out;
    private int bitsInReadBuffer = 0;
    private int readBuffer = 0;

    OmegaEncoding(BufferedInputStream in, BufferedOutputStream out) {
        this.in = in;
        this.out = out;
    }

    @Override
    public void outputInteger(int value) throws IOException {
        long intermediate = 0;
        int bitsInIntermediate = 1;
        int k = value + 1;
        while(k > 1){
            int temp = k;
            int n = 0;
            while(temp > 0){
                temp = temp >> 1;
                n++;
            }
            intermediate |= (long) k << bitsInIntermediate;
            bitsInIntermediate += n;
            k = n - 1;
        }

        for(int i = 0; i < bitsInIntermediate; i++){
            send((int) intermediate >> (bitsInIntermediate - 1 - i));
        }
    }


    @Override
    public int readInteger() throws IOException {
        int n = 1;
        int nextBit = readNextBit();
        if (nextBit == -1) {
            return -1;
        }

        while(nextBit > 0){
            int len = n;
            n = 1;
            for (int i = 0; i < len; i++){
                n <<= 1;
                nextBit = readNextBit();
                if (nextBit == -1){
                    return -1;
                }
                if(nextBit > 0){
                    n |= 1;
                }
            }
            nextBit = readNextBit();
            if (nextBit == -1){
                return -1;
            }
        }
        return n - 1;
    }

    @Override
    public void flush() throws IOException {
        for(int i = 0; i < (8 - bitsInBuffer); i++){
            buffer = buffer << 1;
            buffer = buffer | 1;
        }
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
