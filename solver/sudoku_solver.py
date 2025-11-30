import os
import json

class SudokuSolver:
    def __init__(self, puzzle_string=None, config=None, use_mvc=None, use_lookahead=None, use_color=None):
        print("\n[DEBUG] INIT: Starting initialization...")
        if config is None:
            config = self.load_config()
        self.config = config

        # Initialize core configuration attributes
        self.domain_size = config.get("domain_size", 9)
        self.unassigned_cell = config.get("unassigned_cell", 0)
        self.max_attempts = config.get("max_attempts", 10)
        self.use_max_attempts = config.get("use_max_attempts", False)
        
        self.cell_size = config.get("cell_size", self.domain_size)
        self.subgrid_size = config.get("subgrid_size", self.domain_size)
        self.subgrid_width = config.get("subgrid_width", int(self.domain_size ** 0.5))
        self.subgrid_height = config.get("subgrid_height", int(self.domain_size ** 0.5))

        print(f"[DEBUG] CONFIG: Domain Size: {self.domain_size}")
        print(f"[DEBUG] CONFIG: Subgrid WxH: {self.subgrid_width}x{self.subgrid_height}")

        # Determine strategy flags
        self.use_mvc = use_mvc if use_mvc is not None else config.get("use_mvc", False)
        self.use_lookahead = use_lookahead if use_lookahead is not None else config.get("use_lookahead", False)
        self.use_color = use_color if use_color is not None else config.get("use_vizualization", False)

        if puzzle_string is None:
            print("[DEBUG] INIT: No puzzle string provided, loading from file...")
            loaded_puzzle_string, _, _, _ = self.load_puzzle_from_file(config)
            puzzle_string = loaded_puzzle_string
        else:
            # FIXED: Parse input string to strip solution/underscore if present
            print(f"[DEBUG] INIT: Processing provided puzzle string...")
            cleaned_puzzle, _, _, _ = self.get_puzzle_parts(puzzle_string, config)
            puzzle_string = cleaned_puzzle

        print(f"[DEBUG] INIT: Final puzzle string length: {len(puzzle_string)}")
        print(f"[DEBUG] INIT: First 50 chars: {puzzle_string[:50]}...")

        self.grid = [[self.unassigned_cell] * self.domain_size for _ in range(self.domain_size)]
        self.original_clues = [[False] * self.domain_size for _ in range(self.domain_size)]
        
        # New: Tracking for Visualization
        self.backtrack_counter = 0
        self.history = [] 
        self.current_depth = 0

        print(f"[DEBUG] INIT: About to initialize grid with puzzle_string of length {len(puzzle_string)}")
        self.initialize_grid(puzzle_string)
        print("[DEBUG] INIT: Initialization complete.\n")

    def load_config(self, path="config/config_solver.json"):
        if not os.path.exists(path):
            print(f"[DEBUG] ERROR: Config file '{path}' not found. Returning empty dict.")
            return {}
        with open(path, "r") as config_file:
            return json.load(config_file)

    def initialize_grid(self, puzzle_string):
        print(f"[DEBUG] GRID: Initializing grid with string length: {len(puzzle_string)}")
        if len(puzzle_string) != self.domain_size ** 2:
            raise ValueError(f"Invalid puzzle length ({len(puzzle_string)}). Must be {self.domain_size ** 2} characters.")
        
        for i in range(self.domain_size ** 2):
            row = i // self.domain_size
            col = i % self.domain_size
            value = int(puzzle_string[i])
            self.grid[row][col] = value
            self.original_clues[row][col] = value != self.unassigned_cell
        
        print(f"[DEBUG] GRID: Grid populated successfully.")

    def load_puzzle_from_config(self, config, puzzle_name="test_puzzle"):
        print(f"[DEBUG] LOAD_CONFIG: Loading puzzle '{puzzle_name}' from config...")
        puzzles = config.get("puzzles", {})
        puzzle = puzzles.get(puzzle_name)
        if not puzzle:
            print(f"[DEBUG] ERROR: Puzzle '{puzzle_name}' not found in config.")
            return "0"*81, False, False, False
        print(f"[DEBUG] LOAD_CONFIG: Raw puzzle string: {puzzle[:50]}...")
        return self.get_puzzle_parts(puzzle, config)

    def load_puzzle_from_file(self, config):
        print("[DEBUG] LOAD_FILE: Attempting to load puzzle from file...")
        puzzle_file = config.get("puzzle_file")
        if not puzzle_file:
            puzzle_dir = config.get("puzzle_dir", "puzzles")
            puzzle_name = config.get("puzzle_name", "test_puzzle")
            puzzle_file = os.path.join(puzzle_dir, f"{puzzle_name}.txt")
        
        print(f"[DEBUG] LOAD_FILE: Looking for file: {puzzle_file}")

        if not os.path.exists(puzzle_file):
            print(f"[DEBUG] LOAD_FILE: File {puzzle_file} not found, trying config...")
            return self.load_puzzle_from_config(config)

        print(f"[DEBUG] LOAD_FILE: File found, reading contents...")
        with open(puzzle_file, "r") as f:
            puzzle_string = f.read().strip()
        
        print(f"[DEBUG] LOAD_FILE: File contents read. Length: {len(puzzle_string)}")
        return self.get_puzzle_parts(puzzle_string, config)

    def get_puzzle_parts(self, puzzle_string, config=None):
        print(f"[DEBUG] GET_PARTS: Parsing puzzle string (length: {len(puzzle_string)})...")
        parts = puzzle_string.split("_")
        print(f"[DEBUG] GET_PARTS: Split into {len(parts)} parts")
        
        if len(parts) != 2:
            print(f"[DEBUG] WARNING: Puzzle string format unexpected (missing '_'). Using raw string.")
            return puzzle_string, False, False, False

        puzzle = parts[0]
        print(f"[DEBUG] GET_PARTS: Puzzle portion length: {len(puzzle)}")
        print(f"[DEBUG] GET_PARTS: Solution portion length: {len(parts[1])}")
        
        use_mvc = config.get("use_mvc", False) if config else False
        use_lookahead = config.get("use_lookahead", False) if config else False
        use_color = config.get("use_vizualization", False) if config else False
        
        print(f"[DEBUG] GET_PARTS: Flags -> MVC: {use_mvc}, Lookahead: {use_lookahead}, Color: {use_color}")

        return puzzle, use_mvc, use_lookahead, use_color

    def get_subgrids(self, grid, block_size=3):
        print(f"\n[DEBUG] GET_SUBGRIDS: Called with block_size={block_size}")
        print(f"[DEBUG] GET_SUBGRIDS: Grid Dimensions: {len(grid)}x{len(grid[0])}")
        
        subgrids = []
        
        max_x = self.domain_size
        max_y = self.domain_size
        print(f"[DEBUG] GET_SUBGRIDS: Loop Limits -> max_y (rows): {max_y}, max_x (cols): {max_x}")

        for r in range(0, max_y, block_size):
            for c in range(0, max_x, block_size):
                print(f"[DEBUG] LOOP: Slicing at Row {r}, Col {c}...")
                
                block = [row[c: c + block_size] for row in grid[r:r + block_size]]
                
                print(f"[DEBUG] LOOP: Block extracted. Block has {len(block)} rows.")
                if len(block) > 0:
                     print(f"[DEBUG] LOOP: First row of block has {len(block[0])} cols.")

                print(f"[DEBUG] LOOP: Validating block dimensions...")
                
                if len(block) == block_size and len(block[0]) == block_size:
                    subgrids.append(block)
                    print(f"[DEBUG] LOOP: Block appended. Total subgrids: {len(subgrids)}")
                else:
                    print(f"[DEBUG] LOOP: Block rejected (wrong size).")

        print(f"[DEBUG] GET_SUBGRIDS: Final list contains {len(subgrids)} subgrids")
        return subgrids

    def is_safe(self, row, col, number):
        # print(f"[DEBUG] IS_SAFE: Checking ({row},{col}) for number {number}")
        
        for i in range(self.domain_size):
            if self.grid[row][i] == number:
                # print(f"[DEBUG] IS_SAFE: Conflict in row {row} at column {i}")
                return False
            if self.grid[i][col] == number:
                # print(f"[DEBUG] IS_SAFE: Conflict in column {col} at row {i}")
                return False

        box_size = int(self.domain_size ** 0.5)
        start_row = (row // box_size) * box_size
        start_col = (col // box_size) * box_size
        # print(f"[DEBUG] IS_SAFE: Checking box starting at ({start_row},{start_col})")
        
        for r in range(start_row, start_row + box_size):
            for c in range(start_col, start_col + box_size):
                if self.grid[r][c] == number:
                    # print(f"[DEBUG] IS_SAFE: Conflict in box at ({r},{c})")
                    return False
        
        # print(f"[DEBUG] IS_SAFE: Number {number} is safe at ({row},{col})")
        return True

    def find_empty_cell(self):
        # print("[DEBUG] FIND_EMPTY: Searching for empty cell...")
        if not self.use_mvc:
            # print("[DEBUG] FIND_EMPTY: Using standard left-to-right search")
            for row in range(self.domain_size):
                for col in range(self.domain_size):
                    if self.grid[row][col] == self.unassigned_cell:
                        # print(f"[DEBUG] FIND_EMPTY: Found empty cell at ({row},{col})")
                        return row, col
        else:
            # print("[DEBUG] FIND_EMPTY: Using MVC (Minimum Values Constraint) heuristic")
            min_options = self.domain_size + 1
            best_cell = None
            for row in range(self.domain_size):
                for col in range(self.domain_size):
                    if self.grid[row][col] == self.unassigned_cell:
                        options = sum(1 for num in range(1, self.domain_size + 1) if self.is_safe(row, col, num))
                        # print(f"[DEBUG] FIND_EMPTY: Cell ({row},{col}) has {options} options")
                        if options < min_options:
                            min_options = options
                            best_cell = (row, col)
            # if best_cell:
            #     print(f"[DEBUG] FIND_EMPTY: Best cell is {best_cell} with {min_options} options")
            return best_cell
        # print("[DEBUG] FIND_EMPTY: No empty cells found")
        return None

    def check_lookahead(self, row, col):
        # print(f"[DEBUG] LOOKAHEAD: Checking if assignment at ({row},{col}) creates conflicts...")
        for r in range(self.domain_size):
            for c in range(self.domain_size):
                if self.grid[r][c] == self.unassigned_cell:
                    if not any(self.is_safe(r, c, num) for num in range(1, self.domain_size + 1)):
                        # print(f"[DEBUG] LOOKAHEAD: Cell ({r},{c}) has no valid options - conflict detected!")
                        return True
        # print(f"[DEBUG] LOOKAHEAD: No conflicts detected")
        return False

    def solve(self):
        # print(f"[DEBUG] SOLVE: Starting solve iteration (backtracks so far: {self.backtrack_counter})")
        
        if self.use_max_attempts and self.backtrack_counter >= self.max_attempts:
            # print(f"[DEBUG] SOLVE: Max attempts reached ({self.max_attempts})")
            return False

        next_cell = self.find_empty_cell()
        if not next_cell:
            # print("[DEBUG] SOLVE: No empty cells remaining - PUZZLE SOLVED!")
            return True

        row, col = next_cell
        # print(f"[DEBUG] SOLVE: Trying to fill cell ({row},{col})")
        self.current_depth += 1
        
        # Calculate domain for visualization BEFORE we pick
        current_domain = [n for n in range(1, self.domain_size + 1) if self.is_safe(row, col, n)]

        for number in range(1, self.domain_size + 1):
            # print(f"[DEBUG] SOLVE: Attempting number {number} at ({row},{col})")
            
            if self.is_safe(row, col, number):
                # print(f"[DEBUG] SOLVE: Placing {number} at ({row},{col})")
                self.grid[row][col] = number
                
                # --- VIZ LOGGING ---
                self.history.append({
                    "type": "attempt",
                    "depth": self.current_depth,
                    "cell": (row, col),
                    "val": number,
                    "domain": current_domain.copy(),
                    "status": "trying"
                })
                # -------------------

                if self.use_lookahead and self.check_lookahead(row, col):
                    # print(f"[DEBUG] SOLVE: Lookahead failed - removing {number}")
                    self.grid[row][col] = self.unassigned_cell
                    self.backtrack_counter += 1
                    
                    # --- VIZ LOGGING ---
                    self.history.append({"type": "lookahead_fail", "depth": self.current_depth, "cell": (row, col), "val": number})
                    # -------------------
                    continue

                if self.solve():
                    return True

                # print(f"[DEBUG] SOLVE: Backtracking from ({row},{col}), removing {number}")
                self.grid[row][col] = self.unassigned_cell
                self.backtrack_counter += 1
                
                # --- VIZ LOGGING ---
                self.history.append({"type": "backtrack", "depth": self.current_depth, "cell": (row, col), "val": number})
                # -------------------

        # print(f"[DEBUG] SOLVE: No valid numbers for ({row},{col}) - returning False")
        self.current_depth -= 1
        return False