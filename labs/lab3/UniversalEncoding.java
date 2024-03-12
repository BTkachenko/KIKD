import java.io.IOException;

public interface UniversalEncoding {
    void outputInteger(int value) throws IOException;
    int readInteger() throws IOException;

    void flush() throws IOException;

}
