# CSCEA 405 - Artificial Intelligence

## Constraint Satisfaction Problem (Sudoku)

A configurable, Python-based Sudoku solver featuring advanced backtracking algorithms, heuristics (Minimum Remaining Values), and a rich console-based visualization system.

---

## Features

### Smart Solving
Uses recursive backtracking optimized with the Minimum Values Constraint (MVC) heuristic.

### Lookahead Strategy
Optional forward-checking to prune dead-end paths early.

### Visualizer Interface
Interactive console UI to select built-in puzzles or import custom ones.

### Decision Tree Logging
Visualizes the decision path, showing attempts, backtracks, and lookahead prunes.

### Fully Configurable
JSON-based configuration for solver parameters, visualizations, and colors.

### Famous Puzzles Included
Comes with test cases like Project Euler #96, Peter Norvig's hard puzzles, and Arto Inkala's "AI Escargot".

---

## Project Structure

```
Your-Repository-Root/
├── .git/                      # Git version control
├── .github/
│   └── workflows/
│       └── dev_pipeline.yml   # Universal CI Pipeline
├── colab_docs/                # Google Colab documentation
├── config/
│   ├── config_solver.json     # Solver configuration settings
│   └── config_visualization.json  # Visualization settings
├── generator/                 # Puzzle generator (in development)
├── solver/                    # Main solver implementation
│   ├── puzzles/
│   │   └── my_custom_puzzle.txt  # Custom puzzle definitions
│   ├── sudoku_solver.py       # Core solving logic
│   └── sudoku_visualizer.py   # UI and visualization
├── unit_tests/                # Test suite (in development)
├── .gitignore                 # Git ignore rules
├── LICENSE                    # Project license
└── README.md                  # Project documentation
```

---

## Setup and Installation

1. **Prerequisites:** Python 3.9 or higher.
2. **Clone/Download** the repository to a local folder.
3. **Environment:** No external dependencies are required (uses standard libraries: json, os, importlib).

---

## Running the Project

### Whole Project Pipeline
**Status:** Coming Soon

### Puzzle Generator
**Status:** Coming Soon

### Sudoku Solver

To run the interactive solver and visualizer, you must run the script from within the solver directory so it can correctly locate configuration files.

#### Via Command Line

```bash
# Navigate to the solver directory
cd solver

# Run the visualizer entry point
python sudoku_visualizer.py
```

#### Via Visual Studio Code

1. Open the `solver` folder specifically in VS Code (File > Open Folder... > Select `solver`).
2. Open `sudoku_visualizer.py`.
3. Press **F5** (or navigate to Run and Debug > Run Sudoku Visualizer).

### Unit Tests
**Status:** Coming Soon

---

## Usage Guide

When you run the visualizer, you'll see a menu like this:

```
=== SUDOKU VISUALIZER V1.0 ===

Available Puzzles from Config:
1. test_puzzle
2. empty_puzzle
3. project_euler_01
...
6. [Import from File]

>>> Select a number:
```

- Select a number (1-5) to solve one of the pre-configured puzzles.
- Select **[Import from File]** to provide a path to a .txt file containing a raw 81-character puzzle string (e.g., `puzzles/my_puzzle.txt`).

---

## Configuration

### `config/config_solver.json`

Controls the logic and available puzzles.

- **`use_mvc`** (bool): Enable "Most Constrained Variable" heuristic.
- **`use_lookahead`** (bool): Check future implications of a move to prune trees early.
- **`puzzles`**: Add new puzzle strings here (format: 81 chars, optional _ + solution).

### `config/config_visualization.json`

Controls the look and feel.

- **`tree_settings`**: Customize the recursion tree output (colors, indent characters).
- **`grid_settings`**: Change border styles and colors for the Sudoku grid.

---

## Puzzle String Format

The solver accepts strings of 81 characters where `0` represents an empty cell.

**Examples:**

- **Standard:** `530070000600195000098...`
- **With Solution:** `...000_534678...` (The solver automatically strips the solution part before processing).

---

## AI Acknowledgements

Generative AI tools were utilized to assist in the development of the following components of this project:

### Solver Development

- **Debugging:** Analysis of backtracking logic and recursion errors; fixing `initialize_grid` and `load_config` functions; and standardizing debug print statements for consistency.
- **Visualization:** Creation of the `sudoku_visualizer.py` script and its corresponding `config_visualization.json`. `sudoku_solver.py` was updated slightly to account for compatability.
- **Configuration:** Updating structure and content for `config_solver.json`.
- **Code Completion:** Utilization of AI-assisted auto-completion in Google Colab and Visual Studio Code environments. Greatly expanded the solve() function to be more robust.
- **Code Cleanup & Comments:** Automated formatting, structure suggestions for Python files, and generation of explanatory comments for complex sections (including fixing AI-generated annotations).


### DevOps

- **GitHub Pipeline:** Creation of a `.yml` workflow for the dev branch to automate syntax checking and execute smoke tests (running the base solver and visualizer on test puzzles) to ensure stability before merging to test.

### Documentation

- Generation and formatting of this README.md file.
- **Pseudocode:** Refinement of algorithmic pseudocode for consistency and improved readability.

### Unit Testing

_(Pending)_

### Puzzle Generator

_(Pending)_

---

## License

Distributed under the GNU General Public License (GPL). See [LICENSE](LICENSE) for more information.