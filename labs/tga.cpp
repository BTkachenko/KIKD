#include <iostream>
#include <string>
#include <bitset>
#include <cmath>
#include <map>
#include <filesystem>
using namespace std;

FILE *fIN;
int*** bgr;
int*** bgr2;
int*** bgr3;
int x;
int y;
int getval(int*** arr, int a, int b, int c) {
    if (0 <=a && a < x && 0 <= b && b < y) {
        return arr[a][b][c];
    }
    return 0;
}
int getN(int*** arr, int a, int b, int c) {
    return getval(arr,a+1,b,c);
}
int getW(int*** arr, int a, int b, int c) {
    return getval(arr,a,b-1,c);
}
int getNW(int*** arr, int a, int b, int c) {
    return getval(arr,a+1,b-1,c);
}
int encode_tab7(int*** arr1, int*** arr2, int type) {
    for (int i = 0; i < x; i++) {
        for (int j = 0; j < y; j++) {
            for (int k = 0; k < 3; k++) {
                int N = getN(arr1,i,j,k);
                int NW = getNW(arr1,i,j,k);
                int W = getW(arr1,i,j,k);
                arr2[i][j][k] = arr1[i][j][k];
                switch (type) {
                    case 1:
                        arr2[i][j][k] -= W;
                        break;
                    case 2:
                        arr2[i][j][k] -= N;
                        break;
                    case 3:
                        arr2[i][j][k] -= NW;
                        break;
                    case 4:
                        arr2[i][j][k] -= N + W - NW;
                        break;
                    case 5:
                        arr2[i][j][k] -= N + (W - NW)/2;
                        break;
                    case 6:
                        arr2[i][j][k] -= W + (N - NW)/2;
                        break;
                    case 7:
                        arr2[i][j][k] -= (N + W)/2;
                        break;
                    case 8:
                        int X;
                        if (NW > max(W,N)) {
                            X = max(W,N);
                        }
                        else if (NW <= min(W,N)) {
                            X = min(W,N);
                        }
                        else {
                            X = W + N - NW;
                        }
                        arr2[i][j][k] -= X;
                    default:
                        break;
                }
                if (arr2[i][j][k] < 0) {
                    arr2[i][j][k] = 256 + arr2[i][j][k];
                }
                if (arr2[i][j][k] < 0) {
                    arr2[i][j][k] = 256 + arr2[i][j][k];
                }
            }
        }
    }
    return 0;
}
int decode_tab7(int*** arr1, int*** arr2, int type) {
    for (int i = x-1; i >= 0; i--) {
        for (int j = 0; j < y; j++) {
            for (int k = 0; k < 3; k++) {
                int N = getN(arr2,i,j,k);
                int NW = getNW(arr2,i,j,k);
                int W = getW(arr2,i,j,k);
                arr2[i][j][k] = arr1[i][j][k];
                switch (type) {
                    case 1:
                        arr2[i][j][k] += W;
                        break;
                    case 2:
                        arr2[i][j][k] += N;
                        break;
                    case 3:
                        arr2[i][j][k] += NW;
                        break;
                    case 4:
                        arr2[i][j][k] += N + W - NW;
                        break;
                    case 5:
                        arr2[i][j][k] += N + (W - NW)/2;
                        break;
                    case 6:
                        arr2[i][j][k] += W + (N - NW)/2;
                        break;
                    case 7:
                        arr2[i][j][k] += (N + W)/2;
                        break;
                    case 8:
                        int X;
                        if (NW > max(W,N)) {
                            X = max(W,N);
                        }
                        else if (NW <= min(W,N)) {
                            X = min(W,N);
                        }
                        else {
                            X = W + N - NW;
                        }
                        arr2[i][j][k] += X;
                    default:
                        break;
                }
                if (arr2[i][j][k] > 255) {
                    arr2[i][j][k] = arr2[i][j][k] - 256;
                }
                if (arr2[i][j][k] > 255) {
                    arr2[i][j][k] = arr2[i][j][k] - 256;
                }
            }
            
        }
    }
    return 0;

}
bool compare_tabs(int*** arr1, int*** arr2) {
    for (int i = x-1; i >= 0; i--) {
        for (int j = 0; j < y; j++) {
            for (int k = 0; k < 3; k++) {
                if (arr1[i][j][k] != arr2[i][j][k]) {
                    cout << "Blad: " << i << " " << j << " "<< arr1[i][j][k] << " " << arr2[i][j][k] << "\n";
                    return false;
                }
            }
        }
    }
    return true;
}
double entropy(int*** arr, string name, string color, int b, int g, int r) {
    int L[256]; //liczba wystąpień bytów
    double P[256]; //P[i] = P(X = i)
    double H[256]; // H(Y|x)
    for (int i = 0; i <= 255; i++) {
        L[i] = 0;
    }
    for (int i = 0; i < x; i++) {
        for (int j = 0; j < y; j++) {
                if (b)
                    L[int(arr[i][j][0])]++;
                if (g)
                    L[int(arr[i][j][1])]++;
                if (r)
                    L[int(arr[i][j][2])]++;
        }
    }
    for (int i = 0; i <= 255; i++) {
        P[i] = (double)L[i]/(double)(x*y*(b+g+r));
    }

    double entropia = 0;
    for (int i = 0; i <= 255; i++) {
        /*if (name == "predykcja 2")
        cout << i << " " << P[i] << "\n";*/
        if (L[i] && P[i]) {
            entropia+= P[i]*(-log2(P[i]));
        }
    }

    cout << "Entropia " << color << " " << name << " obrazu wynosi: " << setprecision(10)<< entropia << '\n';

    return entropia;
}
int readBytes(string input) {
    int c = 0;
    fIN = fopen( input.c_str(), "rb" );
    if (!fIN) {
        cerr << "Nie ma takiego pliku.\n";
        return 1;
    }
    
    
    auto size = filesystem::file_size(input.c_str());
    auto size1 = size;
    cout << "Rozmiar oryginalnego pliku w bajtach: " << size << endl;

    unsigned char z;
    bool endoffile = false;
    fread(&z, 1, 12, fIN);
    fread(&z, 1, 1, fIN);
    x = int(z);
    fread(&z, 1, 1, fIN);
    x += z * 256;
    cout <<"x: " << x << "\n";
    fread(&z, 1, 1, fIN);
    y = int(z);
    fread(&z, 1, 1, fIN);
    y += z * 256;
    cout <<"y: " << y << "\n";
    fread(&z, 1, 2, fIN);

    bgr = new int**[x];
    for (int j = 0; j < x; j++) {
        bgr[j] = new int*[y];
        for(int i = 0; i < y; i++) {
            bgr[j][i] = new int[3];
        }
    }
    bgr2 = new int**[x];
    for (int j = 0; j < x; j++) {
        bgr2[j] = new int*[y];
        for(int i = 0; i < y; i++) {
            bgr2[j][i] = new int[3];
        }
    }
    for (int i = 0; i < x; i++) {
        for (int j = 0; j < y; j++) {
            for (int k = 0; k < 3; k++) {
                fread(&z, 1, 1, fIN);
               
                bgr[i][j][k] = z;
            }
        }
    }
    return 0;
}

int main(int argc, char** argv) {
    string arg = argv[1];
    readBytes(arg);
    double min_c=8.0; double min_b=8.0; double min_g = 8.0; double min_r =8.0;
    bgr3 = new int**[x];
    for (int j = 0; j < x; j++) {
        bgr3[j] = new int*[y];
        for(int i = 0; i < y; i++) {
            bgr3[j][i] = new int[3];
        }
    }
    string c,b,g,r;
    entropy(bgr,"org","calosc", 1,1,1);
    entropy(bgr,"org","blue",1,0,0);
    entropy(bgr,"org","green",0,1,0);
    entropy(bgr,"org","red",0,0,1);

    for (int i =1; i <=7; i++) {
        cout << "\n";
        encode_tab7(bgr,bgr2,i);
        double e_c = entropy(bgr2,"predykcja " + to_string(i),"calosc", 1,1,1);
        double e_b = entropy(bgr2,"predykcja " + to_string(i),"blue",1,0,0);
        double e_g = entropy(bgr2,"predykcja " + to_string(i),"green",0,1,0);
        double e_r = entropy(bgr2,"predykcja " + to_string(i),"red",0,0,1);
        if (e_c < min_c) {
            min_c = e_c;
            c = "predykcja " + to_string(i);
        }
        if (e_b < min_b) {
            min_b = e_b;
            b = "predykcja " + to_string(i);
        }
        if (e_g < min_g) {
            min_g = e_g;
            g = "predykcja " + to_string(i);
        }
        if (e_r < min_r) {
            min_r = e_r;
            r = "predykcja " + to_string(i);
        }
        decode_tab7(bgr2,bgr3,i);
        if (compare_tabs(bgr,bgr3)) {
            cout << "OK\n";
        }
    }
    cout << "\n";
    encode_tab7(bgr,bgr2,8);
    double e_c = entropy(bgr2,"predykcja nowy","calosc", 1,1,1);
    double e_b = entropy(bgr2,"predykcja nowy","blue",1,0,0);
    double e_g = entropy(bgr2,"predykcja nowy","green",0,1,0);
    double e_r = entropy(bgr2,"predykcja nowy","red",0,0,1);
    if (e_c < min_c) {
        min_c = e_c;
        c = "predykcja nowy";
    }
    if (e_b < min_b) {
        min_b = e_b;
        b = "predykcja nowy";
    }
    if (e_g < min_g) {
        min_g = e_g;
        g = "predykcja nowy";
    }
    if (e_r < min_r) {
        min_r = e_r;
        r = "predykcja nowy";
    }
    decode_tab7(bgr2,bgr3,8);
    if (compare_tabs(bgr,bgr3)) {
        cout << "OK\n";
    }
    cout << "\n";
    cout << "Najlepsza predykcja calosci: " << c << ", " << min_c << "\n";
    cout << "Najlepsza predykcja red: " << r << ", " << min_r << "\n";
    cout << "Najlepsza predykcja green: " << g << ", " << min_g << "\n";
    cout << "Najlepsza predykcja blue: " << b << ", " << min_b << "\n";
    
}