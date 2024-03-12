import java.io.*;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.Map;

public class Main {

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

    public static void main(String[] args) {

        //encoding
        File inFile = new File(args[0]);
        File outFile = new File("encoded.txt");
        BufferedInputStream in = null;
        BufferedOutputStream out = null;
        try {
            in = new BufferedInputStream(Files.newInputStream(inFile.toPath()));
            out = new BufferedOutputStream(new FileOutputStream(outFile));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        Encoder enc;
        if (args.length < 3){
            enc = new Encoder(in, out, new OmegaEncoding(in, out));
            System.out.println("using Omega");
        } else if (args[2].equals("gamma")){
            enc = new Encoder(in, out, new GammaEncoding(in, out));
            System.out.println("using Gamma");
        } else if (args[2].equals("delta")) {
            enc = new Encoder(in, out, new DeltaEncoding(in, out));
            System.out.println("using Delta");
        } else if (args[2].equals("fib")) {
            enc = new Encoder(in, out, new FibonacciEncoding(in, out));
            System.out.println("using Fibonacci");
        } else {
            enc = new Encoder(in, out, new OmegaEncoding(in, out));
            System.out.println("using Omega");
        }

        try {
            enc.encode();
            in.close();
            out.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        //decoding
        File decodedFile = new File(args[1]);

        BufferedInputStream encoded = null;
        BufferedOutputStream decoded = null;
        try {
            encoded = new BufferedInputStream(new FileInputStream(outFile));
            decoded = new BufferedOutputStream(new FileOutputStream(decodedFile));
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);
        }

        Decoder dec;
        if (args.length < 3){
            dec = new Decoder(encoded, decoded, new OmegaEncoding(encoded, decoded));
        } else if (args[2].equals("gamma")){
            dec = new Decoder(encoded, decoded, new GammaEncoding(encoded, decoded));
        } else if (args[2].equals("delta")) {
            dec = new Decoder(encoded, decoded, new DeltaEncoding(encoded, decoded));
        } else if (args[2].equals("fib")) {
            dec = new Decoder(encoded, decoded, new FibonacciEncoding(encoded, decoded));
        } else {
            dec = new Decoder(encoded, decoded, new OmegaEncoding(encoded, decoded));
        }

        double entropykod;
        double entropyu;
        try {
            dec.decode();
            encoded.close();
            decoded.close();
             entropyu = calculateEntropy(outFile);
             entropykod = calculateEntropy(inFile);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        System.out.println("Dlugosc kodowanego pliku:" + inFile.length());
        System.out.println("Dlugosc zakodowanego pliku:" + outFile.length());
        System.out.println("Stopien kompresji: " + ((double) inFile.length() / (double) outFile.length()));
        System.out.println("Entropia kodowanego: " + entropykod);
        System.out.println("Entropia zakodowanego: " + entropyu);
    }
}
