import mmap
import re
import sys
from multiprocessing import Pool


def process_chunk(start, end, file_path):
    """
    Process a chunk of the file individually, to find
    header start/end indices and sequences start/end indices.
    """

    # Memory-map the file
    with open(file_path, "rb") as f:
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        chunk = mmapped_file[start:end]

    #
    # Core logic:
    # Find all headers in the chunk and store their start and end positions
    headers = [(m.start() + start, m.end() + start) for m in re.finditer(b'>[^n]*', mmapped_file)]
    results = []

    # If there are no headers in the chunk, return an empty list
    if len(headers) == 0:
        return results

    # Process each header to find the associated sequence start and end positions
    for i, (s, e) in enumerate(headers[:-1]):
        seq_start = e + 1  # Sequence starts after the header
        seq_end = headers[i + 1][0] - 1  # Sequence ends before the next header
        out = [s, e, seq_start, seq_end]
        results.append(out)

    # Handle the last header and sequence
    s, e = headers[-1]
    seq_start = e + 1  # Sequence starts after the header
    out = [
        s,
        e,
        seq_start,
        "X",
    ]  # Use "X" as a placeholder for the sequence end position
    results.append(out)

    return results


def find_chunk_starts(mmapped_file, chunk_size=500):
    """
    Determine start positions of chunks to process the file in parallel.
    """

    chunk_starts = []

    # Determine chunk start positions by finding newlines
    for start in range(0, len(mmapped_file), chunk_size):
        end = start + 100  # Additional bytes to ensure we find a newline
        chunk = mmapped_file[start:end]

        # Find the first newline
        chunk = mmapped_file[start:end]
        pos = chunk.find(b"\n")
        if pos == -1:
            continue

        linestart = start + pos
        chunk_starts.append(linestart)

    return chunk_starts


def parallel_processing(file_path, num_processes):
    """
    Distribute processing of the file across multiple processes.
    """

    # Open and memory-map the file
    with open(file_path, "rb") as f:
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        file_size = len(mmapped_file)

    # Determine chunk start positions
    chunk_size = file_size // num_processes
    start_positions = find_chunk_starts(mmapped_file, chunk_size=chunk_size)
    start_positions = [0] + start_positions + [file_size]

    # Distribute chunks among processes and gather results
    with Pool(num_processes) as pool:
        results = pool.starmap(
            process_chunk,
            [
                (start_positions[i], start_positions[i + 1], file_path)
                for i in range(len(start_positions) - 1)
            ],
        )

    # Flatten and sort the results
    results = [item for sublist in results for item in sublist]
    # results = sorted(results, key=lambda x: x[0])

    # Update sequence end positions (X) w/ next header start position :-)
    for i, l in enumerate(results[:-1]):
        results[i][3] = results[i + 1][0] - 1
    results[-1][3] = len(mmapped_file) - 1

    return results


def main():
    """
    Prints indices of all headers and sequences in a FASTA file:
    1. Header start position
    2. Header end position
    3. Sequence start position
    4. Sequence end position

    Since header start/end also gives start/ends of sequences
    only the first is required, found with this code logic:

    headers = [(m.start() + start, m.end() + start) for m in re.finditer(b">.*", chunk)]

    The rest of the code is for parallel processing.
    """

    # Ensure correct number of command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_file_path> <num_processes>")
        sys.exit(1)

    infile = sys.argv[1]  # Input file path
    num_processes = int(sys.argv[2])  # Number of processes for parallelization

    # Retrieve results through parallel processing
    results = parallel_processing(infile, num_processes)

    # Print results
    for L in results:
        string = " ".join([str(x) for x in L])
        print(string)


if __name__ == "__main__":
    main()
