import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;

public class Decoder {
    private HashMap<Integer, ArrayList<Byte>> dictionary;
    private BufferedInputStream inputStream;
    private BufferedOutputStream outputStream;
    private int valuesInDictionary;

    private UniversalEncoding universalEncoding;

    Decoder(BufferedInputStream in, BufferedOutputStream out, UniversalEncoding universalEncoding) {
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
            dictionary.put(i, temp);
        }
        valuesInDictionary = 256;
    }

    private void output(ArrayList<Byte> value) throws IOException {
        for (Byte b : value) {
            outputStream.write((int) b);
        }
    }

    public void decode() throws IOException {
        int code;
        ArrayList<Byte> w, temp;

        code = readInt();
        w = dictionary.get(code);
        output(w);

        code = readInt();

        while(code != -1){
            if(dictionary.containsKey(code)){
                temp = new ArrayList<>(w);
                w = dictionary.get(code);
                temp.add(w.get(0));
                dictionary.put(valuesInDictionary, temp);
                valuesInDictionary++;
            } else {
                w = new ArrayList<>(w);
                w.add(w.get(0));
                dictionary.put(valuesInDictionary, w);
                valuesInDictionary++;
                w = dictionary.get(code);
            }

            output(w);
            code = readInt();
        }
        outputStream.flush();
    }

    private int readInt() throws IOException {
        return universalEncoding.readInteger();
    }

}
