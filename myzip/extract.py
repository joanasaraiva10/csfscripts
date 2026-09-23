import re

with open("subtitles.srt", encoding="utf-8") as f:
    raw = f.read()

blocks = re.split(r"\n\s*\n", raw.strip())

lines = []
speakers = set()

for b in blocks:
    b_lines = b.splitlines()
    # drop index number and timestamp line
    text_lines = [l for l in b_lines if l.strip() and not l.strip().isdigit() and "-->" not in l]
    if not text_lines:
        continue
    joined = " ".join(text_lines)
    # pull out [SPEAKER] tags
    for m in re.findall(r"\[([A-Z' ]+)\]", joined):
        speakers.add(m.strip().title())
    clean = re.sub(r"\[[^\]]*\]", "", joined)
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = clean.strip("♪").strip()
    if clean:
        lines.append(clean)

print("=== Speakers/character names found ===")
print(sorted(speakers))

print("\n=== Sample cleaned lines ===")
for l in lines[:10]:
    print(l)

with open("clean_lines.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

with open("speakers.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(speakers)))

print(f"\nTotal lines: {len(lines)}")
