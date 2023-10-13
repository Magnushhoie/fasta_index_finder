# Finds header byte offsets
grep -A 1 -b "^>" $1 |  grep -Eo '^[0-9]+' |  awk '{printf "%s\n%s\n", $1-1, $1}' | tail -n +2 | paste - - - -
