# Sudoku Solver & Benchmark

A Python-based Sudoku solver that implements and benchmarks a basic backtracking algorithm against an optimized Constraint Satisfaction Problem (CSP) solver.

This project includes two Sudoku solvers for performance comparison, a random puzzle generator, and a suite of unit tests.

## Features

* Basic Solver (`solve_basic`): A simple brute-force backtracking solver.
* Smart Solver (`solve_smart`): An optimized CSP solver using the Minimum Remaining Values (MRV) heuristic.
* Puzzle Generator: Creates new 9×9 Sudoku puzzles with a guaranteed unique solution.
* Benchmarking Suite: Compares performance (time and recursion steps) of the two solvers using a puzzle library.
* Unit Tests: Includes tests built with Python’s `unittest` module to validate core logic.

## How to Run

```bash
# Clone the repository (once it's on GitHub)
git clone https://github.com/your-username/sudoku-solver.git
cd sudoku-solver

# Run the main application
python main.py
```

## Development Roadmap

### Week 1: Foundations and Basic Backtracking Solver

Goal: Build a fully functional baseline solver for benchmarking.

Primary Developer Tasks:

* Board representation: Decide on a 9×9 data structure (e.g., list of lists with 0 for empty cells).
* Helper functions:

  * `get_peers(row, col)`: Return all peers in the same row, column, and 3×3 box.
  * `is_valid_move(board, row, col, num)`: Check if a move is valid.
* Basic solver (`solve_basic`):

  * Implement recursive backtracking.
  * Find the next empty cell top-to-bottom, left-to-right.
  * Try numbers 1–9 in order and backtrack when needed.

Team Tasks:

* Set up the Python `unittest` framework.
* Write tests for `get_peers` and `is_valid_move`.
* Create a puzzle library of 10–15 puzzles (easy, medium, hard) with solutions.

### Week 2: Smart CSP Solver (MRV and Optional Forward Checking)

Goal: Build an optimized solver for comparison.

Primary Developer Tasks:

* `get_domain(board, row, col)`: Return valid candidate values for a cell.
* MRV heuristic:

  * `find_best_cell(board)`: Return the empty cell with the smallest domain.
* Smart solver (`solve_smart`):

  * Modify the basic solver to use MRV.
  * Try only values from the cell’s domain.
  * Optional: Add forward checking to prune the search early if domains become empty.

Team Tasks:

* Add tests to validate that `solve_smart` solves known puzzles correctly.

### Week 3: Puzzle Generator

Goal: Generate valid puzzles with a unique solution.

Primary Developer Tasks:

* Design and refine the puzzle generation method (remove-from-solution approach).

Team Tasks:

* Generate a fully solved Sudoku board (use `solve_smart` on an empty grid).
* Remove values while ensuring uniqueness:

  * Remove a value (set to 0).
  * Use `count_solutions` to ensure exactly one solution remains.
  * Continue until 40–50 values are removed.
* Write tests to confirm that multiple generated puzzles each have exactly one solution.

### Week 4: Benchmarking, Integration, and Polish

Goal: Validate performance improvements and finalize the project.

Primary Developer Tasks:

* Add instrumentation to solvers to return:

  * Time taken
  * Recursion step count
* Benchmark script:

  * Load puzzle set or generate new puzzles.
  * Run both solvers and record metrics.
  * Print comparison results.

Team Tasks:

* Build a simple CLI app (`main.py`) for user interaction:

  * Option to solve an existing puzzle or generate a new one.
  * Display the puzzle and allow solver selection.
  * Show solved result, time, and step count.
* Perform code cleanup and documentation improvements.
