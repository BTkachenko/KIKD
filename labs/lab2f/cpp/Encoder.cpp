#include "Encoder.h"
#include <iostream>

long Encoder::totalCount = 0;
long Encoder::l = 0;
long Encoder::u = 0xffffffffL;
std::vector<long> Encoder::dict(Commons::SYMBOLS, 0);
std::vector<long> Encoder::cumCount(Commons::SYMBOLS + 1, 0);
int Encoder::scale3 = 0;
int Encoder::buffer = 0;
int Encoder::bitsInBuffer = 0;
std::ofstream Encoder::outStream;
long Encoder::bytesRead = 0;

void Encoder::encode(int b) {
    long range = u - l + 1;
    u = l + (range * cumCount[b + 1] / totalCount) - 1;
    l = l + (range * cumCount[b] / totalCount);

    for (;;) {
        if ((u & 0x80000000) == (l & 0x80000000)) {
            writeBit((u & 0x80000000) >> 31);
            while (scale3 > 0) {
                writeBit(~((u & 0x80000000) >> 31) & 1);
                scale3--;
            }
        } else if ((l & 0x40000000) && !(u & 0x40000000)) {
            scale3++;
            l &= 0x3fffffff;
            u |= 0x40000000;
        } else {
            break;
        }
        l <<= 1;
        u <<= 1;
        u |= 1;
    }

    totalCount = Commons::updateDict(b, totalCount, dict, cumCount);
}

void Encoder::flushBuffer() {
    outStream.put(static_cast<char>(buffer));
    bitsInBuffer = 0;
    buffer = 0;
}

void Encoder::writeBit(int bit) {
    buffer = (buffer << 1) | bit;
    bitsInBuffer++;
    if (bitsInBuffer == 8) {
        flushBuffer();
    }
}

void Encoder::finalize() {
    for (int i = 0; i < 5; i++) {
        writeBit((l >> (31 - i)) & 1);
    }
    flushBuffer();
}

void Encoder::runEncoding(const std::string &inputFile, const std::string &outputFile) {
    totalCount = Commons::initializeDictionaries(dict, cumCount);

    std::ifstream inStream(inputFile, std::ios::binary);
    outStream.open(outputFile, std::ios::binary);

    if (!inStream.is_open() || !outStream.is_open()) {
        std::cerr << "Could not open files." << std::endl;
        return;
    }

    int b;
    while ((b = inStream.get()) != EOF) {
        bytesRead++;
        encode(static_cast<unsigned char>(b));
    }

    finalize();

    inStream.close();
    outStream.close();
}


int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <input file> <output file>" << std::endl;
        return 1;
    }

    std::string inputFile = argv[1];
    std::string outputFile = argv[2];

    try {
        Encoder::runEncoding(inputFile, outputFile);
    } catch (const std::exception& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}