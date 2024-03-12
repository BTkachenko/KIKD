public class Commons {

    private static final int SYMBOLS = 257;
    private static final int SCALING_THRESHOLD = 1073741823;

    public static long updateDict(int b, long totalCount, long[] dict, long[] cumCount) {
        dict[b]++;
        totalCount++;
        // reskalujemy jeśli suma w słowniku mniejsza niz limit
        if (totalCount == SCALING_THRESHOLD) {
            for (int i = 0; i < SYMBOLS; i++) {
                long temp = dict[i];
                dict[i] = (long) (Math.ceil((double) dict[i] / 2.0));
                totalCount -= temp - dict[i];
            }
            //recalculate cumCount
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

    public static long initializeDictionaries(long[] dict, long[] cumCount) {
        for (int b = 0; b < SYMBOLS; b++) {
            dict[b] = 1;
        }
        for (int i = 0; i < SYMBOLS + 1; i++) {
            cumCount[i] = i;
        }
        return SYMBOLS;
    }
}
