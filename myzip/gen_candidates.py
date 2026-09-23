import re
import itertools

with open("clean_lines.txt", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

with open("speakers.txt", encoding="utf-8") as f:
    speakers = [l.strip() for l in f if l.strip()]

def normalize(s):
    # strip punctuation, keep letters/numbers/spaces
    s = re.sub(r"[^\w\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()

candidates = set()

# 1. Full memorable lines (as-is, normalized, no-space, and title/lower/upper variants)
for l in lines:
    norm = normalize(l)
    if not norm:
        continue
    variants = {
        l,
        norm,
        norm.replace(" ", ""),
        norm.replace(" ", "_"),
        norm.lower().replace(" ", ""),
        norm.upper().replace(" ", ""),
        norm.title().replace(" ", ""),
    }
    candidates.update(variants)

# 2. Word-level n-grams (2-4 words) from each line - short punchy phrases are common password sources
words_per_line = [normalize(l).split() for l in lines]
for w in words_per_line:
    for n in (2, 3, 4):
        for i in range(len(w) - n + 1):
            gram = w[i:i+n]
            joined = "".join(gram)
            joined_us = "_".join(gram)
            candidates.add(joined)
            candidates.add(joined_us)
            candidates.add(joined.lower())
            candidates.add(joined.title().replace(" ", ""))

# 3. Character names, alone and combined with common suffixes
suffixes = ["", "123", "1", "!", "2013", "2025"]  # AoT anime aired 2013
for name in speakers:
    n = name.replace(" ", "").replace("'", "")
    for suf in suffixes:
        candidates.add(n + suf)
        candidates.add(n.lower() + suf)
        candidates.add(n.upper() + suf)

# 4. Pairs of character names (e.g. ErenMikasa, MikasaEren)
name_tokens = [s.replace(" ", "").replace("'", "") for s in speakers]
for a, b in itertools.permutations(name_tokens, 2):
    candidates.add(a + b)
    candidates.add((a + b).lower())

# 5. Single distinctive words (longer than 3 chars) from all lines
single_words = set()
for w in words_per_line:
    for tok in w:
        if len(tok) > 3:
            single_words.add(tok)
            single_words.add(tok.lower())
            single_words.add(tok.capitalize())
candidates.update(single_words)

# Clean empties
candidates = {c for c in candidates if c}

with open("wordlist.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(candidates)))

print(f"Generated {len(candidates)} candidate passwords -> wordlist.txt")
