# Description
Program extract non-obvious strong moves with the help of uci server and engines.
# Usage
usage: client.py [-h] [--header {all,concise,minimal}] [-cp CENTIPAWNS]
                 [-d DEPTH] [-n N_VARIATIONS] [-e E]
                 input_pgn_path output_pgn_path
where:
 - `--header` defines header type,
 - `-cp` min required centipawns difference between best and second best move,
 - `-d` min engine search depth,
 - `-n` number of variations (min: 2),
 - `-e` path to UCI Server configuration file
 - `input_pgn_path` path to the game in pgn format,
 - `output_pgn_path` where to save extracted moves (in pgn format).

# Filters
Filters description is given in `filters.md` file.