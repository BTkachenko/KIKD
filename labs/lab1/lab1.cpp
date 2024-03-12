#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cmath>

using namespace std;

void countSymbolsAndConditional(const string& filePath, unordered_map<unsigned char, int>& symbolCounts, unordered_map<unsigned char, unordered_map<unsigned char, int>>& conditionalCounts) {
    ifstream file(filePath, ios::binary);
    if (!file.is_open()) {
        cerr << "Nie można otworzyć pliku." << endl;
        exit(1);
    }
    unsigned char prevChar = 0;
    unsigned char c;
    while (file.read(reinterpret_cast<char*>(&c), sizeof(c))) {
        symbolCounts[c]++;
        conditionalCounts[prevChar][c]++;
        prevChar = c;
    }
}

double calculateEntropy(const unordered_map<unsigned char, int>& symbolCounts, int totalSymbols) {
    double entropy = 0.0;
    for (const auto& pair : symbolCounts) {
        double p = static_cast<double>(pair.second) / totalSymbols;
        entropy -= p * log2(p);
    }
    return entropy;
}

double calculateConditionalEntropy(const unordered_map<unsigned char, int>& symbolCounts, const unordered_map<unsigned char, unordered_map<unsigned char, int>>& conditionalCounts, int totalSymbols) {
    double conditionalEntropy = 0.0;
    for (const auto& xPair : conditionalCounts) {
        unsigned char x = xPair.first;
        if (symbolCounts.find(x) == symbolCounts.end()) continue; // Upewniamy się, że x istnieje w symbolCounts
        double pX = static_cast<double>(symbolCounts.at(x)) / totalSymbols;
        double hYGivenX = 0.0;
        for (const auto& yPair : xPair.second) {
            unsigned char y = yPair.first;
            if (symbolCounts.find(x) == symbolCounts.end()) continue; // Upewniamy się, że x istnieje w symbolCounts
            double pYGivenX = static_cast<double>(yPair.second) / symbolCounts.at(x);
            hYGivenX -= pYGivenX * log2(pYGivenX);
        }
        conditionalEntropy += pX * hYGivenX;
    }
    return conditionalEntropy;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        cerr << "Podaj ścieżkę do pliku jako argument." << endl;
        return 1;
    }
    string filePath = argv[1];
    unordered_map<unsigned char, int> symbolCounts;
    unordered_map<unsigned char, unordered_map<unsigned char, int>> conditionalCounts;
    
    countSymbolsAndConditional(filePath, symbolCounts, conditionalCounts);

    int totalSymbols = 0;
    for (const auto& pair : symbolCounts) {
        totalSymbols += pair.second;
    }

    double entropy = calculateEntropy(symbolCounts, totalSymbols);
    double conditionalEntropy = calculateConditionalEntropy(symbolCounts, conditionalCounts, totalSymbols);
    double difference = entropy - conditionalEntropy;

    cout << "Entropia: " << entropy << endl;
    cout << "Entropia warunkowa: " << conditionalEntropy << endl;
    cout << "Różnica: " << difference << endl;

    return 0;
}

