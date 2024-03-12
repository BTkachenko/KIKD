#include "Commons.h"

long Commons::updateDict(int b, long totalCount, std::vector<long>& dict, std::vector<long>& cumCount) {
    dict[b]++;
    totalCount++;
    if (totalCount == SCALING_THRESHOLD) {
        for (int i = 0; i < SYMBOLS; i++) {
            long temp = dict[i];
            dict[i] = static_cast<long>(std::ceil(static_cast<double>(dict[i]) / 2.0));
            totalCount -= temp - dict[i];
        }
        cumCount[0] = 0;
        for (int i = 1; i < SYMBOLS + 1; i++) {
            cumCount[i] = cumCount[i - 1] + dict[i - 1];
        }
    } else {
        for (int i = b & 0xff; i < SYMBOLS; i++) {
            cumCount[i + 1]++;
        }
    }
    return totalCount;
}

long Commons::initializeDictionaries(std::vector<long>& dict, std::vector<long>& cumCount) {
    for (int b = 0; b < SYMBOLS; b++) {
        dict[b] = 1;
    }
    cumCount[0] = 0;
    for (int i = 1; i < SYMBOLS + 1; i++) {
        cumCount[i] = i;
    }
    return SYMBOLS;
}
