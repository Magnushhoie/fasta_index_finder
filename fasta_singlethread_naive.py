import sys

infile = sys.argv[1]

indices = []
counter = 0
with open(infile, "r") as f:
    for line in f:
        length = len(line)
        header = line[0] == ">"

        if header:
            # Previous sequence end
            indices.append(counter - 1)
            # Header start
            indices.append(counter)
            # Header end
            indices.append(counter + length - 1)
            # Next sequence start
            indices.append(counter + length)

        # Next iteration
        counter += length

# Exclude first index (no previous sequence)
indices = indices[1:]
# Add last sequence end (assumes no ending newline)
indices.append(counter - 1)

# Print
for i in range(0, len(indices), 4):
    print(f"{indices[i]} {indices[i+1]} {indices[i+2]} {indices[i+3]}")
