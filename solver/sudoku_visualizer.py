import json
import os
from sudoku_solver import SudokuSolver

class SudokuVisualizer:
    def __init__(self, config_path="config/config_solver.json", viz_config_path="config/config_visualization.json"):
        self.config = self._load_json(config_path)
        self.viz_config = self._load_json(viz_config_path)
        self.solver = None
        self.colors = self.viz_config["tree_settings"]["colors"]
        
    def _load_json(self, path):
        if not os.path.exists(path):
            print(f"Error: Config file {path} not found.")
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def select_puzzle_interface(self):
        """Interactive prompt to select a puzzle."""
        print(self.viz_config["interface"]["welcome_message"])
        print("\nAvailable Puzzles from Config:")
        
        puzzles = self.config.get("puzzles", {})
        puzzle_keys = list(puzzles.keys())
        
        filtered_keys = [k for k in puzzle_keys if not k.startswith("//")]
        
        for i, key in enumerate(filtered_keys):
            comment = puzzles.get(f"//_comment_{key.split('_')[-1]}", "") # Try to find associated comment
            if not comment:
                # Try finding standard comment keys based on index or naming convention if simple
                pass
            print(f"{i + 1}. {key} {self.colors['info']}{comment}{self.colors['reset']}")
            
        print(f"{len(filtered_keys) + 1}. [Import from File]")
        
        choice = input(f"\n{self.viz_config['interface']['prompt_symbol']}Select a number: ")
        
        selected_puzzle_string = ""
        puzzle_name = "Custom"

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(filtered_keys):
                puzzle_name = filtered_keys[choice_idx]
                selected_puzzle_string = puzzles[puzzle_name]
            elif choice_idx == len(filtered_keys):
                path = input("Enter file path: ")
                if os.path.exists(path):
                    with open(path, "r") as f:
                        selected_puzzle_string = f.read().strip()
                    puzzle_name = os.path.basename(path)
                else:
                    print("File not found.")
                    return
        except ValueError:
            print("Invalid input.")
            return

        # Initialize Solver
        self.solver = SudokuSolver(puzzle_string=selected_puzzle_string, config=self.config)
        self.run_visualizations(puzzle_name)

    def run_visualizations(self, puzzle_name):
        viz_flags = self.config.get("visualizations", {})
        
        if viz_flags.get("unsolved_puzzle", True):
            print(f"\n--- Unsolved: {puzzle_name} ---")
            self.print_grid(self.solver.grid, solved=False)

        print(f"\n{self.config['strings']['solving_started'].format(puzzle_name)}")
        success = self.solver.solve()
        
        if success:
            print(self.config['strings']['solved_success'].format(puzzle_name))
            if viz_flags.get("solved_puzzle", True):
                print(f"\n--- Solved: {puzzle_name} ---")
                self.print_grid(self.solver.grid, solved=True)
        else:
            print(self.config['strings']['solved_failure'].format(puzzle_name))

        if viz_flags.get("node_tree", False):
            print("\n--- Decision Node Tree ---")
            self.print_node_tree(self.solver.history)

    def print_grid(self, grid, solved=False):
        """Prints the grid with ASCII borders and colors."""
        c = self.viz_config["grid_settings"]
        color = self.colors["value_choice"] if solved else c["clue_color"]
        reset = self.colors["reset"]
        
        # Simple ASCII representation
        print("╔" + "═══╤" * 8 + "═══╗")
        for r, row in enumerate(grid):
            line = "║"
            for col_val in row:
                val_str = str(col_val) if col_val != 0 else " "
                # If solved, highlight checks could go here, for now using global color
                line += f" {color}{val_str}{reset} │"
            print(line[:-1] + "║")
            if r < 8:
                if (r + 1) % 3 == 0:
                    print("╠" + "═══╪" * 8 + "═══╣")
                else:
                    print("╟" + "───┼" * 8 + "───╢")
        print("╚" + "═══╧" * 8 + "═══╝")

    def print_node_tree(self, history):
        """Generates a text-based tree from solver history."""
        settings = self.viz_config["tree_settings"]
        limit = settings["max_display_depth"]
        
        row_labels = settings["labels"]["subgrid_rows"]
        col_labels = settings["labels"]["subgrid_cols"]

        print(f"{self.colors['info']}[Root]{self.colors['reset']}")
        
        for i, step in enumerate(history):
            if i > limit:
                print(f"{settings['indent_char']}... (Tree truncated, too large)")
                break

            depth = step.get("depth", 0)
            indent = settings["indent_char"] * depth
            branch = settings["branch_char"]

            r, c = step['cell']
            # Calculate Subgrid Label (e.g., A-X)
            sg_r = row_labels[r // 3]
            sg_c = col_labels[c // 3]
            subgrid_label = f"{sg_r}{sg_c}"

            if step['type'] == 'attempt':
                val = step['val']
                domain_str = str(step['domain'])
                print(f"{indent}{branch}Cell: ({r},{c}) [{subgrid_label}] | Value: {self.colors['value_choice']}{val}{self.colors['reset']} | Domain: {domain_str}")
            elif step['type'] == 'backtrack':
                print(f"{indent}{branch}{self.colors['backtrack']}Backtrack{self.colors['reset']} from ({r},{c})")
            elif step['type'] == 'lookahead_fail':
                print(f"{indent}{branch}{self.colors['backtrack']}Lookahead Prune{self.colors['reset']} at ({r},{c})")

if __name__ == "__main__":
    viz = SudokuVisualizer()
    viz.select_puzzle_interface()