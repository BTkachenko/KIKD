import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

public class Encoder {
    private final BufferedInputStream inputStream;
    private final UniversalEncoding universalEncoding;
    private HashMap<ArrayList<Byte>, Integer> dictionary;
    private BufferedOutputStream outputStream;
    private int valuesInDictionary;

    Encoder(BufferedInputStream in, BufferedOutputStream out, UniversalEncoding universalEncoding) {
        initializeDictionary();
        inputStream = in;
        outputStream = out;
        this.universalEncoding = universalEncoding;
    }

    private void initializeDictionary() {
        dictionary = new HashMap<>();
        for (int i = 0; i < 256; i++) {
            ArrayList<Byte> temp = new ArrayList<>(1);
            temp.add((byte) i);
            dictionary.put(temp, i);
        }
        valuesInDictionary = 256;
    }

    public void encode() throws IOException {
        int first = inputStream.read();
        int next = inputStream.read();

        ArrayList<Byte> key = new ArrayList<>();
        key.add((byte) first);
        while (next != -1) {
            key.add((byte) next);
            if (!dictionary.containsKey(key)) {
                key.remove(key.size() - 1);
                output(dictionary.get(key));
                key.add((byte) next);
                dictionary.put(key, valuesInDictionary);
                valuesInDictionary++;
                key = new ArrayList<>();
                key.add((byte) next);
            }
            next = inputStream.read();
        }
        output(dictionary.get(key));
        universalEncoding.flush();
    }

    private void output(int value) throws IOException {
        universalEncoding.outputInteger(value);
    }

}
