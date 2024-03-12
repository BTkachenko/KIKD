#ifndef COMMONS_H
#define COMMONS_H

#include <vector>
#include <cmath>

class Commons {
public:
    static const int SYMBOLS = 257;
    static const long SCALING_THRESHOLD = 1073741823;

    static long updateDict(int b, long totalCount, std::vector<long>& dict, std::vector<long>& cumCount);
    static long initializeDictionaries(std::vector<long>& dict, std::vector<long>& cumCount);
};

#endif // COMMONS_H
