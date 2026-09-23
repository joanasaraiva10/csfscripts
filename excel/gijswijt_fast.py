"""
Faster Gijswijt sequence generator using the Z-function to compute each term's
curling number in O(n) instead of the naive O(n^2), making full generation
O(n^2) instead of O(n^3).
"""

def z_function(s):
    n = len(s)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z

def curling_number_fast(seq):
    n = len(seq)
    if n == 0:
        return 1
    rev = seq[::-1]
    z = z_function(rev)
    best = 1
    for L in range(1, n + 1):
        z_val = z[L] if L < n else 0
        period_len = L + z_val
        k = period_len // L
        if k > best:
            best = k
    return best

def gijswijt_fast(N):
    seq = [1]
    while len(seq) < N:
        seq.append(curling_number_fast(seq))
    return seq

if __name__ == "__main__":
    print(gijswijt_fast(50))
