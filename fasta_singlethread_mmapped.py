import mmap
import re
import sys

infile = sys.argv[1]

with open(infile, "r") as f:
    # Memory-map the file
    mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    # Finding headers
    headers = [(m.start(), m.end()) for m in re.finditer(b">.*", mmapped_file)]

    for i, (start, end) in enumerate(headers):
        seq_start = end + 1
        seq_end = (
            headers[i + 1][0] - 1 if i + 1 < len(headers) else len(mmapped_file) - 1
        )
        print(f"{start} {end} {seq_start} {seq_end}")

    # Close the mmap object
    mmapped_file.close()
