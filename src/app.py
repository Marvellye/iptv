import requests
import os
import time

INPUT_FILE = "./files/files.m3u"
OUTPUT_FILE = "./files/working.m3u"
CACHE_FILE = "./files/cache.txt"
TIMEOUT = 10  # updated timeout

# Load already-checked URLs
checked_urls = set()
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8", errors="ignore") as f:
        checked_urls = set(line.strip() for line in f)

# Open output and cache files in append mode
working_file = open(OUTPUT_FILE, "a", encoding="utf-8", errors="ignore")
cache_file = open(CACHE_FILE, "a", encoding="utf-8", errors="ignore")

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()

    # Only process lines starting with #EXTINF
    if line.startswith("#EXTINF:"):
        info_line = line
        url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        if url_line in checked_urls:
            i += 2
            continue

        try:
            # GET request with streaming to avoid downloading full playlist
            response = requests.get(url_line, timeout=TIMEOUT, stream=True)
            if response.status_code == 200:
                # Write both info and URL to working.m3u
                working_file.write(info_line + "\n")
                working_file.write(url_line + "\n")
                working_file.flush()
                print(f"WORKING: {url_line}")
            else:
                print(f"FAILED ({response.status_code}): {url_line}")
        except requests.RequestException as e:
            print(f"FAILED ({e}): {url_line}")
        finally:
            # Update cache no matter what
            cache_file.write(url_line + "\n")
            cache_file.flush()
            checked_urls.add(url_line)

        i += 2  # Skip next line because it's the URL
    else:
        i += 1

working_file.close()
cache_file.close()
print("Done!")
