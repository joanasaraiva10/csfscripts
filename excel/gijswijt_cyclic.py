"""
Gijswijt position selector, but with the key sequence cycling every 500 terms
key[i] = gijswijt_term[i % 500]
"""

from gijswijt_fast import gijswijt_fast

CYCLE_LEN = 500
_base_terms = gijswijt_fast(CYCLE_LEN)  # computed once, cheap (fast version)

def gijswijt_positions_cyclic(n_positions):
    """
    position[0] = 0
    position[i] = position[i-1] + key[i-1]   for i >= 1
    where key[i] = _base_terms[i % CYCLE_LEN]
    Returns exactly n_positions positions.
    """
    n_keys_needed = max(n_positions - 1, 0)
    positions = [0]
    for i in range(n_keys_needed):
        term = _base_terms[i % CYCLE_LEN]
        positions.append(positions[-1] + term)
    return positions[:n_positions]

if __name__ == "__main__":
    print("First 20 base terms:", _base_terms[:20])
    print("First 20 positions:", gijswijt_positions_cyclic(20))
