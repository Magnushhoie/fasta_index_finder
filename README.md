## FASTA index finder

Inspired by 22112 High Performance Computing in Life Science: What affects performance?
[https://teaching.healthtech.dtu.dk/22112/index.php/What_affects_performance](https://teaching.healthtech.dtu.dk/22112/index.php/What_affects_performance)

Prints indices of all headers and sequences in a FASTA file:
1. Header start position
2. Header end position
3. Sequence start position
4. Sequence end position

Running:
```bash
# Find mini.fasta header start/end, sequence start/end indices, using 4 cores
$ fasta_parallel.py data/mini.fasta 4

0 8 9 246
247 255 256 499
500 508 509 750
751 759 760 997
998 1006 1007 1241
1242 1250 1251 1493
1494 1502 1503 1754
1755 1763 1764 2006
```

Example input [data/mini.fasta](data/mini.fasta):

```fasta
>1AHW_ED
eiqlqqsgaelvrpgalvklsckasgfniKDYYmhwvkqrpeqglewigliDpENgNTIy
dpkfqgkasitadtssntaylqlssltsedtavyycarDNSYyfdywgqgttltvss---
-------DikmtqspssmyaslgervtitckasQdiRkYlnwyqqkpwkspktliyYats
ladgvpsrfsgsgsgqdysltisslesddtatyyclqHGESpYtfgggtklein
>1BJ1_HL
...
```

## Speed comparison (3.0 GB FASTA file, repeated runs)

| Method                          | Approximate Time | Code/Command       | Description                                   |
|---------------------------------|-----------------|--------------------|-----------------------------------------------|
| Python (Single-threaded, naive)        | ~25.0s           | [fasta_singlethread_naive.py](fasta_singlethread_naive.py) | Python process lines while reading        |
| Python (Single-threaded, mmapped)        | ~2.9s           | [fasta_singlethread_mmaped.py](fasta_singlethread_mmapped.py) | Python process memory-mapped file        |
| C++ (Single-threaded)           | ~2.5s           | [fasta_singlethread_c.cpp](fasta_singlethread_c.cpp) | C++ process lines while reading            |
| C++ (Single-threaded mmapped)   | ~1.2s           | [fasta_singlethread_c_mmapped.cpp](fasta_singlethread_c_mmaped.cpp) | C++ process memory-mapped file |
| Python (Single-threaded, chunked)                  | ~1.1s           | [fasta_singlethread_chunked.py](fasta_singlethread_chunked.py) | Processes 1 MB of file at once      |
| BASH one-liner                  | ~1.1s           | [bash_oneliner.sh](bash_oneliner.sh) | BASH one-liner that finds byte offsets        |
| Python (Parallel Processing, mmapped)    | ~1.0s           | [fasta_parallel_mmapped.py](fasta_parallel_mmapped.py) | Python with parallel processing on mmaped file, using 16 cores |
| Baseline: Cat read file         | ~0.7s           | `time cat data/humangenome.fsa > /dev/null` | Using `cat` to read the file as a baseline    |

Effect of chunk-size (Python single-threaded, chunked)
- 100 bytes: ~50 s
- 512 bytes: ~11 s
- 1024 bytes ~7 s
- 0.5 MB: ~1.5 s
- 1 MB: ~1.0 s
- 2 MB: ~1.1 s
- 8 MB: 1.4 s
- 128 MB: ~ 2.5 s

## Usage

```bash
# Python: Single-threaded: ~2.9 s
time python fasta_singlethread_mmapped.py data/humangenome.fsa

# C++ single-threaded: ~2.5 s
# Compile and run:
g++ -std=c++11 -O3 fasta_singlethread_c.cpp -o fasta_singlethread_c
time ./fasta_singlethread_c data/humangenome.fsa

# C++ single-threaded mmapped: ~1.2 s
# Compile and run:
g++ -std=c++11 -O3  fasta_singlethread_c_mmapped.cpp -o fasta_singlethread_cmmapped -lboost_iostreams
time ./fasta_singlethread_mmaped data/humangenome.fsa

# BASH one-liner, finds byte offsets: ~1.1 s
grep -A 1 -b "^>" data/humangenome.fsa |  grep -Eo '^[0-9]+' |  awk '{printf "%s\n%s\n", $1-1, $1}' | tail -n +2 | paste - - - -
```

### Parallel processing logic

Parallel processing works by first reading the file into memory with mmap, then accessing separate chunks and processing in parallell.


```python
# Read file
mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

# Find chunk start positions (only start at new lines)
start_positions = find_chunk_starts(mmapped_file, chunk_size=chunk_size)

# Distribute
with Pool(num_processes) as pool:
    results = pool.starmap(
        process_chunk,
        [
            (start_positions[i], start_positions[i + 1], file_path)
            for i in range(len(start_positions) - 1)
        ],
    )
```

Since header start/end also gives start/ends of sequences
only the first is required, found with this code logic:

```python
# Process chunk code:
headers = [(m.start() + start, m.end() + start) for m in re.finditer(b">.*", chunk)]

# Calculate sequence start/end from header/start end
for i, (s, e) in enumerate(headers[:-1]):
    seq_start = e + 1  # Sequence starts after the header
    seq_end = headers[i + 1][0] - 1  # Sequence ends before the next header
    out = [s, e, seq_start, seq_end]
    results.append(out)
```
