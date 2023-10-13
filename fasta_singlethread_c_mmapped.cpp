#include <boost/iostreams/device/mapped_file.hpp>  // for mmap
#include <cstring>                                 // for memchr

int main(int argc, char *argv[]) {
  if (argc < 2) {
    fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
    return 1;
  }

  boost::iostreams::mapped_file mmap(argv[1],
                                     boost::iostreams::mapped_file::readonly);
  auto f = mmap.const_data();
  auto l = f + mmap.size();

  size_t line_start_pos = 0;  // Position of the start of the current line
  size_t end_pos = 0;         // Position of the end of the current line

  while (f && f != l) {
    // Find the next newline character
    if ((f = static_cast<const char *>(memchr(f, '\n', l - f)))) {
      end_pos = line_start_pos +
                (f - (mmap.const_data() + line_start_pos));  // Update end_pos

      // Check for '>' at the start of the line and print positions
      if (*(mmap.const_data() + line_start_pos) == '>') {
        printf("%zu %zu\n", line_start_pos, end_pos);
      }

      line_start_pos = end_pos + 1;  // Update line_start_pos for the next line
      f++;
    }
  }

  return 0;
}
