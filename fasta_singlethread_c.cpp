#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    // Check for correct number of command-line arguments
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    // Open the file for reading
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", argv[1]);
        return 1;
    }

    // Initialize variables to store line data and positions
    char *line = NULL;  // Pointer to the current line being read
    size_t len = 0;     // Length of the line
    ssize_t read;       // Number of characters read
    size_t pos = 0;     // Current position in the file
    
    // Initialize variables to store header and sequence start/end positions
    size_t seq_start = 0, seq_end = 0;
    size_t header_start = 0, header_end = 0;
    size_t last_header_start = 0, last_header_end = 0;

    // Loop through each line of the file
    while ((read = getline(&line, &len, file)) != -1) {
        // Check if the line is a header (starts with '>')
        if (line[0] == '>') {
            // Update header start and end positions
            header_start = pos;
            header_end = pos + read - 1;

            // If not the first header, print the last header and sequence positions
            if (seq_start != 0) {
                seq_end = pos - 1;
                printf("%zu %zu %zu %zu\n", last_header_start, last_header_end,
                       seq_start, seq_end);
            }

            // Update sequence start position and last header positions
            seq_start = pos + read;
            last_header_start = header_start;
            last_header_end = header_end;
        }

        // Update the current position in the file
        pos += read;
    }

    // Print the last header and sequence positions
    seq_end = pos - 1;
    printf("%zu %zu %zu %zu\n", last_header_start, last_header_end, seq_start,
           seq_end);

    // Free allocated memory and close the file
    free(line);
    fclose(file);

    return 0;
}