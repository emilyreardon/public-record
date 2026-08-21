import os, re

RAW_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_core")
path = os.path.join(RAW_DIR, "amendments_11-27_extracted.txt")

with open(path, encoding="utf-8") as f:
    text = f.read()

print("total_len=" + str(len(text)))
print("")

# Case-insensitive search for the word "amendment" and print each hit with context
print("=== all case-insensitive 'amendment' hits with context ===")
for m in re.finditer(r"amendment", text, flags=re.I):
    idx = m.start()
    snippet = text[max(0,idx-60):idx+80].replace(chr(10), " | ")
    print(str(idx) + ": ..." + snippet + "...")

print("")
print("=== rfind check for footer boundary ===")
last_online_exhibits = text.rfind("Online Exhibits")
print("last 'Online Exhibits' at index: " + str(last_online_exhibits))
first_online_exhibits = text.find("Online Exhibits")
print("first 'Online Exhibits' at index: " + str(first_online_exhibits))

print("")
print("=== content right after header nav (chars 900-1600) ===")
print(text[900:1600])
