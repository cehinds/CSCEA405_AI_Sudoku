import json
import os
import sys

# [AI Fix] Add current directory to path so we can import sudoku_solver from the same folder
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from sudoku_solver import SudokuSolver
except ImportError:
    print("\n[ERROR] Could not import 'SudokuSolver'.")
    print("Ensure 'sudoku_solver.py' is in the same folder as this script.\n")
    sys.exit(1)

class SudokuVisualizer:
    def __init__(self, config_filename="config_solver.json", viz_config_filename="config_visualization.json"):
        # [AI Fix] Use dynamic path finding to locate configs in Root OR config/ folders
        self.config_path = self._find_config(config_filename)
        self.viz_config_path = self._find_config(viz_config_filename)

        self.config = self._load_json(self.config_path)
        self.viz_config = self._load_json(self.viz_config_path)

        # [AI Fix] Prevent KeyError by checking if config actually loaded
        if not self.viz_config:
            print(f"\n[CRITICAL ERROR] Could not find or load '{viz_config_filename}'.")
            print(f"Searched in: Project Root, 'config' folder, and '{current_dir}'")
            sys.exit(1)
            
        # [AI Fix] Type hint added to prevent VS Code static analysis error.
        # Pylance sees 'None' and flags .solve() as missing, even though it's assigned later.
        self.solver: SudokuSolver | None = None
        
        # Safely access tree_settings
        tree_settings = self.viz_config.get("tree_settings", {})
        self.colors = tree_settings.get("colors", {
            "info": "", "reset": "", "value_choice": "", "backtrack": "", "node_id": ""
        })

    def _find_config(self, filename):
        """Searches for config file in likely locations relative to the script."""
        script_dir = os.path.dirname(os.path.abspath(__file__)) # .../solver/
        project_root = os.path.dirname(script_dir)              # .../Project_Root/
        
        # Check these locations in order:
        possible_paths = [
            os.path.join(project_root, filename),               # 1. Project Root
            os.path.join(script_dir, filename),                 # 2. Solver folder
            os.path.join(project_root, "config", filename),     # 3. Root/config/
            os.path.join(script_dir, "config", filename),       # 4. Solver/config/
            filename                                            # 5. Current Working Dir
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Print warning if not found (helpful for CI/CD debugging)
        print(f"[WARN] Config file '{filename}' not found in search paths.")
        return None

    def _load_json(self, path):
        if path is None or not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read {path}: {e}")
            return {}

    def select_puzzle_interface(self):
        """Interactive prompt to select a puzzle."""
        # Check for interface settings safely
        interface = self.viz_config.get("interface", {})
        welcome = interface.get("welcome_message", "Sudoku Visualizer")
        
        print(welcome)
        print("\nAvailable Puzzles from Config:")
        
        puzzles = self.config.get("puzzles", {})
        puzzle_keys = list(puzzles.keys())
        
        # Filter out comments
        filtered_keys = [k for k in puzzle_keys if not k.startswith("//")]
        
        for i, key in enumerate(filtered_keys):
            comment_key = f"//_comment_{key.split('_')[-1]}"
            comment = puzzles.get(comment_key, "")
            label = f"{i+1}. {key}"
            if comment:
                label += f" ({comment})"
            print(label)
            
        print(f"{len(filtered_keys)+1}. Custom Input String")
        
        prompt = interface.get("prompt_symbol", ">>> ")
        
        # Handle case where input is piped in CI/CD (prevent EOFError)
        try:
            choice = input(f"\nSelect a puzzle (1-{len(filtered_keys)+1}): {prompt}")
        except EOFError:
            print("\n[INFO] No input provided (CI/CD mode). Exiting selection.")
            return False

        selected_puzzle = None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(filtered_keys):
                key = filtered_keys[idx]
                selected_puzzle = puzzles[key]
                print(f"\nSelected: {key}")
            elif idx == len(filtered_keys):
                selected_puzzle = input("Enter Sudoku String (81 chars): ")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
            
        if selected_puzzle:
            self.solver = SudokuSolver(puzzle_string=selected_puzzle, config=self.config)
            return True
        return False

    def display_solution_path(self):
        if not self.solver or not self.solver.history:
            print("No history available. Run solve() first.")
            return

        print("\n--- Solution Tree Traversal ---")
        history = self.solver.history
        self.print_tree_step(history)

    def print_tree_step(self, history):
        settings = self.viz_config.get("tree_settings", {})
        limit = settings.get("max_display_depth", 100)
        
        row_labels = settings.get("labels", {}).get("subgrid_rows", ["A","B","C"])
        col_labels = settings.get("labels", {}).get("subgrid_cols", ["X","Y","Z"])
        
        indent_char = settings.get("indent_char", "  ")
        branch_char = settings.get("branch_char", "|- ")

        print(f"{self.colors['info']}[Root]{self.colors['reset']}")
        
        for i, step in enumerate(history):
            if i > limit:
                print(f"{indent_char}... (Tree truncated, too large)")
                break

            depth = step.get("depth", 0)
            indent = indent_char * depth
            
            r, c = step['cell']
            
            # Safe subgrid calculation
            try:
                sg_r = row_labels[r // 3] if (r//3) < len(row_labels) else "?"
                sg_c = col_labels[c // 3] if (c//3) < len(col_labels) else "?"
            except:
                sg_r, sg_c = "?", "?"
                
            subgrid_label = f"{sg_r}{sg_c}"

            type_ = step.get('type', '')
            if type_ == 'attempt':
                val = step.get('val', '?')
                domain_str = str(step.get('domain', []))
                print(f"{indent}{branch_char}Cell: ({r},{c}) [{subgrid_label}] | Value: {self.colors['value_choice']}{val}{self.colors['reset']} | Domain: {domain_str}")
            elif type_ == 'backtrack':
                print(f"{indent}{branch_char}{self.colors['backtrack']}Backtrack{self.colors['reset']} from ({r},{c})")
            elif type_ == 'lookahead_fail':
                 val = step.get('val', '?')
                 print(f"{indent}{branch_char}{self.colors['backtrack']}Lookahead Fail{self.colors['reset']} on ({r},{c}) with {val}")

    # [AI Fix] Added for CI/CD Pipeline compatibility
    # This is required because your YAML calls 'viz.run_visualizations()'
    def run_visualizations(self, puzzle_key):
        """Runs the visualizer non-interactively for a specific puzzle key."""
        puzzles = self.config.get("puzzles", {})
        
        # Validate puzzle key
        if puzzle_key not in puzzles:
            print(f"[ERROR] Puzzle '{puzzle_key}' not found in config.")
            return

        print(f"Loading puzzle: {puzzle_key}")
        puzzle_string = puzzles[puzzle_key]
        
        # Initialize solver with the specific puzzle
        self.solver = SudokuSolver(puzzle_string=puzzle_string, config=self.config)
        
        # Run Solve
        print("Solving...")
        success = self.solver.solve()
        
        if success:
            print(f"\n{self.colors['info']}Puzzle Solved!{self.colors['reset']}")
            self.display_solution_path()
        else:
            print(f"\n{self.colors['backtrack']}No solution found.{self.colors['reset']}")
            self.display_solution_path()

    def run(self):
        # [AI Fix] Added 'and self.solver' to satisfy static analysis
        # This confirms to Pylance that self.solver is not None
        if self.select_puzzle_interface() and self.solver:
            print("\nSolving...")
            success = self.solver.solve()
            
            if success:
                print(f"\n{self.colors['info']}Puzzle Solved!{self.colors['reset']}")
                self.display_solution_path()
            else:
                print(f"\n{self.colors['backtrack']}No solution found.{self.colors['reset']}")
                # Still show history to see where it failed
                self.display_solution_path()

if __name__ == "__main__":
    viz = SudokuVisualizer()
    viz.run()