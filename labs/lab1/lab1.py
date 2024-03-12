import math
import os
import sys

from collections import defaultdict

def file_reader(file_name):
    file_entropy = defaultdict(int)
    file_cond_entropy = defaultdict(int)
    entropy = 0
    cond_entropy = 0
    with open(file_name, "br") as file:
        text = file.read()
        for i, c in enumerate(text):
            file_entropy[c] = file_entropy[c] + 1
            file_cond_entropy[c, text[i-1]] = file_cond_entropy[(c, text[i-1] if i > 0 else 0)] + 1

    bytes_in_file = os.stat(file_name).st_size
    log_bytes_in_file = math.log2(bytes_in_file)

    for single_byte, byte_freq in file_entropy.items():
        entropy += -(math.log2(byte_freq) - log_bytes_in_file) * byte_freq
        for bytes_tuple, tuple_freq in file_cond_entropy.items():
            if bytes_tuple[0] == single_byte and tuple_freq >= 1:        
                cond_entropy += tuple_freq * - (math.log2(tuple_freq) - math.log2(byte_freq))

    print(entropy / bytes_in_file)
    print(cond_entropy / bytes_in_file)

if __name__ == "__main__":
    filename = sys.argv[1]
    file_reader(filename)
