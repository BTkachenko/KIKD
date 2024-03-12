#ifndef ENCODER_H
#define ENCODER_H

#include <vector>
#include <fstream>
#include "Commons.h"

class Encoder {
private:
    static long totalCount;
    static long l;
    static long u;
    static std::vector<long> dict;
    static std::vector<long> cumCount;
    static int scale3;
    static int buffer;
    static int bitsInBuffer;
    static std::ofstream outStream;
    static long bytesRead;

public:
    static void encode(int b);
    static void flushBuffer();
    static void writeBit(int bit);
    static void finalize();
    static void runEncoding(const std::string &inputFile, const std::string &outputFile);
};

#endif // ENCODER_H
