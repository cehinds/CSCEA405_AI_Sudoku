import math
# CLASS SudokuAgent:
class SudokuAgent:
    
    # -------------------------------------------------------------------------
    # AGENT CORE: Initialization & State
    # -------------------------------------------------------------------------
    
    def __init__(self, puzzle_string=None, use_mvc=False, use_lookahead=False, domain_size = 9, hidden_char = 0):
        print(f"DEBUG: Initializing SudokuAgent")
        self.unassigned_char = hidden_char
        
        self.puzzle = puzzle_string
        self.action_use_mvc = use_mvc
        self.action_use_lookahead = use_lookahead
        self.agent_domain_size = domain_size
        self.agent_backtrack_count = 0
        self.agent_failed_assignments = []
        
        # ENVIRONMENT functions called here:
        self.environment = self.environment_build_environment(puzzle_string)
        self.environment_grid = self.environment[0]
        print(f"DEBUG: initialized environment grid {self.environment_grid}")
        
        # Calculate box width
        self.box_width = int(math.sqrt(self.agent_domain_size)) 
        
        # PERCEIVER function called here:
        self.environment_unassigned = self.percept_get_unassigned()
        print(f"DEBUG: initialized environment unassigned {self.environment_unassigned}") 
        self.environment_puzzle_string = self.environment[1]
        print(f"DEBUG: initialized environment puzzle {self.environment_puzzle_string}")
        if (self.environment[2] is not None):
            self.environment_solution_string = self.environment[2]
            print(f"DEBUG: initialized environment solution {self.environment_solution_string}")
            
        
        # ENVIRONMENT helper functions called here:
        self.environment_constraints = self.environment_get_rows_columns()
        self.environment_rows = self.environment_constraints[0]
        print(f"DEBUG: initialized environment constraint rows (coords) {self.environment_rows}")
        self.environment_columns = self.environment_constraints[1]
        print(f"DEBUG: initialized environment constraint columns (coords) {self.environment_columns}")
        self.environment_subgrids = self.environment_get_boxes()
        print(f"DEBUG: initialized environment constraint subgrids (coords) {self.environment_subgrids}")
        print(f"DEBUG: Initilized Environment")
    
    
    # -------------------------------------------------------------------------
    # ENVIRONMENT FUNCTIONS: Building and Parsing
    # -------------------------------------------------------------------------
    
    def environment_build_environment(self, puzzle = None, puzzle_name = 'puzzle.txt'):
        if (puzzle is None):
            puzzle_string = self.environment_get_file(puzzle_name).strip()
        else:
            puzzle_string = puzzle
        return self.environment_parse_input(puzzle_string)
            
    
    def environment_parse_input(self, input_string):
        puzzle_solution = self.environment_get_file(input_string).split("_")
        puzzle_string = puzzle_solution[0]
        solution_string = puzzle_solution[1] 
        d = self.agent_domain_size
        grid = []
        for i in range(self.agent_domain_size): 
            row_start = i*d
            row_end = (i+1)*d
            
            row_string = puzzle_string[row_start:row_end]
            row_list = [int(col) for col in row_string ]
            grid.append(row_list)
        return grid, puzzle_string, solution_string
            
    
    def environment_get_file(self, filename = "puzzle.txt"):
        try:
            with open(filename,'r') as file_handler:
                raw_content = file_handler.read()
                return raw_content
            
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found. Returning a sample string.")
            return '530070000600195000098000060800060003400803001700020006060000280000419005000080079_530070000600195000098000060800060003400803001700020006060000280000419005000080079\n'
        

    def percept_get_unassigned(self, hiddenchar = 0):
        """(PERCEIVER) Builds and returns a list of (row, col) coordinates for all cells with value 0."""
        unassigned = []
        d = self.agent_domain_size
        for r in range(d):
            for c in range(d):
                if self.environment_grid[r][c] == hiddenchar:
                    unassigned.append((r,c))
        return unassigned
    
    
    def environment_get_rows_columns(self):
        """(ENVIRONMENT) Generates two lists of lists containing (r, c) coordinates for each row and column."""
        # Initialize 9 lists for rows and 9 for columns
        rows_coords = [[] for _ in range(self.agent_domain_size)]
        columns_coords = [[] for _ in range(self.agent_domain_size)]
        d = self.agent_domain_size
        
        # Iterate over all 81 cells
        for r in range(d):
            for c in range(d):
                # For Row r, append (r, c) to the list at index r
                rows_coords[r].append((r, c))
                # For Column c, append (r, c) to the list at index c
                columns_coords[c].append((r, c))
        
        return rows_coords, columns_coords


    def environment_get_boxes(self):
        """(ENVIRONMENT) Organizes the 81 cell coordinates into 9 lists representing the 3x3 boxes."""
        # Initialize 9 lists for box coordinates
        boxes_coords = [[] for _ in range(self.agent_domain_size)]
        d = self.agent_domain_size
        
        for r in range(d):
            for c in range(d):
                # Calculate the box index (b)
                b = self.box_width * (r // self.box_width) + (c // self.box_width)
                
                # Append the coordinate tuple (r, c)
                boxes_coords[b].append((r, c))
        return boxes_coords

    # -------------------------------------------------------------------------
    # PERCEIVER FUNCTIONS: Constraint & Goal Checks
    # -------------------------------------------------------------------------

    def percept_is_safe(self, r, c, value):
        """(PERCEIVER) Checks if placing 'value' at (r, c) is valid according to Sudoku rules."""

        # 1. Check Row Constraint:
        if value in self.environment_grid[r]:
            return False 

        # 2. Check Column Constraint:
        for coord_r, coord_c in self.environment_columns[c]:
            if self.environment_grid[coord_r][coord_c] == value:
                return False 

        # 3. Check Box Constraint:
        b = self.box_width * (r // self.box_width) + (c // self.box_width)

        for coord_r, coord_c in self.environment_subgrids[b]:
            if self.environment_grid[coord_r][coord_c] == value:
                return False 
        
        # The placement is safe!
        return True 


    def percept_is_complete(self):
        """(PERCEIVER) checks if the sudoku grid is fully solved"""
        return len(self.environment_unassigned) == 0

    # -------------------------------------------------------------------------
    # ACTUATOR FUNCTIONS: State Change
    # -------------------------------------------------------------------------

    def actuator_assign(self, r, c, value):
        """(ACTUATOR) Assigns 'value' to the cell (r, c) by updating the grid (Source of Truth)."""
        self.environment_grid[r][c] = value
        

    def actuator_unassign(self, r, c):
        """(ACTUATOR) Removes the value from the cell (r, c) for backtracking."""
        self.environment_grid[r][c] = self.unassigned_char
        
        
    # -------------------------------------------------------------------------
    # ACTION FUNCTIONS: Variable and Value Ordering
    # -------------------------------------------------------------------------

    def action_select_unassigned_variable(self):
        """(ACTION) Standard variable selection: returns the first unassigned cell (r,c)."""
        if self.environment_unassigned:
            return self.environment_unassigned[0]
            
        return (None,None)
    
    def action_get_ordered_domain_values(self, r, c):
        """(ACTION) Standard value ordering: returns the domain of possible values (1 to domain_size) in order."""
        return list(range(1, self.agent_domain_size +1))
    
    
    # -------------------------------------------------------------------------
    # AGENT FUNCTION: Core Solver (Backtracking Search)
    # -------------------------------------------------------------------------

    def recursive_backtrack(self):        
        # 1. Goal Test
        if self.percept_is_complete():
            print(f"DEBUG: *** GOAL REACHED! ***")
            return self.environment_grid
        
        # 2. Variable Selection
        (r, c) = self.action_select_unassigned_variable()
        print(f"DEBUG: Selected variable ({r}, {c})")
        
        # 3. Action Selection (Value Ordering) and Constraint Check
        for value in self.action_get_ordered_domain_values(r, c):
            
            # A. Check if the value is safe to place at (r, c)
            if self.percept_is_safe(r, c, value):
                
                # B. Apply Action (Actuator)
                self.actuator_assign(r, c, value)
                # Remove the coordinate (r, c) from the list since it's now assigned
                self.environment_unassigned.remove((r, c)) 
                print(f"DEBUG: Assigned {value} to ({r}, {c}). Remaining unassigned: {len(self.environment_unassigned)}")
                
                # C. Recursive Step
                
                # Call recursive_backtrack() 
                result = self.recursive_backtrack()
                
                # and check the result                
                if result is not None:
                    return result
                                
                # D. Backtrack (If recursion fails)
                print(f"DEBUG: Backtracking from ({r}, {c}) = {value}.")
                
                # 1. Revert the grid (Actuator)
                self.actuator_unassign(r, c)
                
                # 2. Re-insert the coordinate to be processed later
                self.environment_unassigned.append((r, c))
                
                # 3. Update Metrics
                self.agent_backtrack_count += 1 
                # Log failed assignment for unit testing (optional, but good practice)
                self.agent_failed_assignments.append(((r, c), value))
                
        # 4. Failure: If no value works, return failure
        return None 
    
    def action_solve(self):
        """(ACTION) start bactracking search and returns the result"""
        
        return self.recursive_backtrack()
    
    def solve(self, puzzle: None):
        if puzzle is not None:
            self.enviment
            

def main():
    # Example puzzle (First empty cell is at (0, 2))
    TEST_PUZZLE = '530070000600195000098000060800060003400803001700020006060000280000419005000080079'
    solver = SudokuAgent(puzzle_string=TEST_PUZZLE)
    
    # --- Start the Solver and Capture the Result ---
    print("\n--- Starting Backtracking Solver ---")
    solution_grid = solver.action_solve()

    # --- Final Results ---
    if solution_grid is not None:
        print("\n*** SOLUTION FOUND! *** ")
        print("Final Grid:")
        for row in solution_grid:
            print(row)
    else:
        print("\n*** PUZZLE UNSOLVABLE *** ")

    # --- Performance Metrics ---
    print(f"\n--- Performance Metrics --- 📊")
    print(f"Total Backtracks: {solver.agent_backtrack_count}")
    print(f"Failed Assignments Logged: {len(solver.agent_failed_assignments)}")

if __name__ == "__main__":
    main()