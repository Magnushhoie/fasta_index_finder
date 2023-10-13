#!/usr/bin/env python3
# Lesson 4, ex 3
import sys
import time

if len(sys.argv) != 2:
    print("Usage: index1.py <input fasta file>")
    sys.exit(1)

# Define the size of the chunks to read from the file (in bytes)
chunksize = 1024 * 1024  # 1 MB

# Attempt to open the FASTA file for reading in binary mode
try:
    fasta_file = sys.argv[1]
    infile = open(fasta_file, "rb")
except IOError as err:
    print("Cant open file:", str(err))
    sys.exit(1)

# Initialize variables
file_pos = 0  # Keep track of the global file position (bytes)
header_L = list()  # List to store the starting indices of header_L
newline_L = list()  # List to store the ending indices of header_L

# Parse through the file chunk by chunk
while True:
    # Read a (1 MB) chunk of the file
    content = infile.read(chunksize)

    # Break the loop if we've reached the end of the file
    if len(content) == 0:
        break

    # First find header start positions (lines starting with ">")
    chunk_pos = 0

    # Continue until no more '>' characters are found (content.find(b'>') returns -1)
    while chunk_pos != -1:
        # Find the next '>' character in the chunk
        chunk_pos = content.find(b">", chunk_pos)

        # If found, add the header position to list
        # and move pointer to the next position for next search
        if chunk_pos != -1:
            header_L.append(chunk_pos + file_pos)
            chunk_pos += 1

    # Next, backtrack to identify header ending position (first newline character)
    for i in range(len(newline_L), len(header_L)):
        # Determine the starting position for the search within the chunk
        chunk_pos = max(0, header_L[i] - file_pos)

        # Find next newline character
        chunk_pos = content.find(b"\n", chunk_pos)

        # If found, add the global position to the newline_L list
        if chunk_pos != -1:
            newline_L.append(chunk_pos + file_pos)

    # Update the global file position pointer
    file_pos += len(content)

# Close the file after reading
infile.close()

# Display the start and end indices of headers and sequences
for i in range(len(header_L)):
    headstart = header_L[i]
    headend = newline_L[i]
    seqstart = headend + 1

    # Sequence end is either the next header start or the end of the file
    if i < len(header_L) - 1:
        seqend = header_L[i + 1] - 1
    else:
        seqend = file_pos - 1

    # Print the indices
    print(headstart, headend, seqstart, seqend)
