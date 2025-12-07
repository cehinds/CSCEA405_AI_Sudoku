
# CLASS SudokuAgent:
class SudokuAgent:
    
#     // INTELLIGENT AGENT COMPONENTS
#     // -------------------------------------------------------------------------
#     // PERCEIVER: The agent "sees" the entire board (Full Observability).
#     // In code, this is accessing the grid state directly.
#     // -------------------------------------------------------------------------

    def __init__(self, puzzle_string=None, use_mvc=False, use_lookahead=False, domain_size = 9):
        self.puzzle = puzzle_string
        self.action_use_mvc = use_mvc
        self.action_use_lookahead = use_lookahead
        self.agent_domain_size = domain_size
        self.environment = self.build_environment(puzzle_string)
        self.environment_grid = self.environment[0]
        self.environment_puzzle_string = self.environment[1]
        self.environment_solution_string = self.environment[2]
        print(f"DEBUG: Initializing SudokuAgent")
    
    def build_environment(self, puzzle = None, puzzle_name = 'puzzle.txt'):
        if (puzzle is None):
            puzzle_string = self.get_file(puzzle_name).strip()
        else:
            puzzle_string = puzzle
        return self.parse_input(puzzle_string)
            
    
    def parse_input(self, input_string):
        puzzle_solution = self.get_file(input_string).split("_")
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
            
            
    
    def get_file(self, filename = "puzzle.txt"):
        try:
            with open(filename,'r') as file_handler:
                raw_content = file_handler.read()
                return raw_content
            
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found. Returning a sample string.")
            return '530070000600195000098000060800060003400803001700020006060000280000419005000080079_530070000600195000098000060800060003400803001700020006060000280000419005000080079\n'
        
        
#     FUNCTION perceiver(environment):
#         RETURN environment.get_current_grid_state()

#     // ACTUATOR: The mechanism to change the environment.
#     // In code, this is the assignment of a value to a cell.
#     // -------------------------------------------------------------------------
#     FUNCTION actuator(state, cell, value):
#         state[cell.row][cell.col] = value
#         RETURN state

#     // STATE REPRESENTATION
#     // Internal belief state matches the actual environment state (Perfect Information).
#     VAR grid_state
#     VAR backtrack_count = 0
#     VAR nodes_explored = 0

#     // INITIALIZATION
#     FUNCTION init(puzzle_string):
#         grid_state = read_puzzle(puzzle_string)

#     // -------------------------------------------------------------------------
#     // CORE SOLVER (Backtracking Search)
#     // -------------------------------------------------------------------------
#     FUNCTION solve():
#         // Validates input and starts the recursive search
#         start_time = GET_TIME()
        
#         result = recursive_backtrack(grid_state)
        
#         // Output details for Unit Testing
#         output_details(result, GET_TIME() - start_time)
#         RETURN result

#     FUNCTION recursive_backtrack(current_state):
#         nodes_explored = nodes_explored + 1
        
#         // GOAL TEST: Check if the state is a complete solution
#         IF is_complete(current_state):
#             RETURN current_state

#         // SELECT VARIABLE: Choose which empty cell to fill next
#         // Options: Standard (next empty) or MRV (Minimum Remaining Values)
#         VAR cell = select_unassigned_variable(current_state)

#         // ACTIONS: Retrieve legal moves for this state
#         // Domain = {1, 2, ..., 9}
#         FOR EACH value IN action_get_ordered_domain_values(current_state, cell):
            
#             // TRANSITION MODEL Check: Is this action valid?
#             IF is_consistent(value, cell, current_state):
                
#                 // LOOKAHEAD (Optional): Forward Checking
#                 // Prunes domain of neighbors before committing
#                 IF use_lookahead AND NOT lookahead_pruning_check(current_state, cell, value):
#                     CONTINUE // Skip if lookahead detects inevitable failure
                
#                 // APPLY ACTION (Transition Function)
#                 // trans_result returns a NEW state with the value applied
#                 VAR next_state = trans_result(current_state, cell, value)
                
#                 // RECURSIVE STEP
#                 result = recursive_backtrack(next_state)
                
#                 // CHECK RESULT
#                 IF result IS NOT failure:
#                     RETURN result
                
#                 // BACKTRACK
#                 // "Reversing" the actuator: reset cell to empty (0)
#                 // This indicates the previous action did not lead to a solution
#                 backtrack_count = backtrack_count + 1
#                 remove_assignment(current_state, cell)

#         RETURN failure

#     // -------------------------------------------------------------------------
#     // HELPER METHODS (Aligned with Lecture Terminology)
#     // -------------------------------------------------------------------------

#     // ACTIONS Function: Returns the set of valid moves for a state
#     FUNCTION action_get_ordered_domain_values(state, cell):
#         // Standard: Return 1-9
#         // LCV (Least Constraining Value) heuristic could be applied here
#         RETURN [1, 2, 3, 4, 5, 6, 7, 8, 9]

#     // TRANSITION FUNCTION: (S, A) -> S'
#     // Returns the result of applying action A to state S
#     FUNCTION trans_result(state, cell, value):
#         // Utilizing the Actuator to modify the internal state representation
#         RETURN actuator(state, cell, value)

#     // PERCEPTION / INPUT
#     FUNCTION read_puzzle(puzzle_string):
#         // Parses the 81-char string into a 9x9 matrix
#         VAR new_grid = 9x9 Matrix
#         FOR i from 0 to 80:
#             row = i / 9
#             col = i % 9
#             new_grid[row][col] = INT(puzzle_string[i])
#         RETURN new_grid

#     // HEURISTIC: Minimum Remaining Values (MRV)
#     // Selects the variable (cell) that is most constrained (fewest legal values)
#     FUNCTION select_minimum_constraint(state):
#         min_options = INFINITY
#         best_cell = NULL
        
#         FOR EACH empty_cell IN state:
#             num_options = count_legal_values(state, empty_cell)
#             IF num_options < min_options:
#                 min_options = num_options
#                 best_cell = empty_cell
        
#         RETURN best_cell

#     // INFERENCE: Lookahead / Forward Checking
#     FUNCTION lookahead_pruning_check(state, cell, proposed_value):
#         // Simulate assignment
#         temp_state = copy(state)
#         actuator(temp_state, cell, proposed_value)
        
#         // Check all neighbors (peers) of the cell
#         FOR EACH neighbor IN get_peers(cell):
#             IF neighbor IS empty:
#                 // If a neighbor has NO legal moves left, prune this branch
#                 IF count_legal_values(temp_state, neighbor) == 0:
#                     RETURN FALSE // Failure detected
#         RETURN TRUE

#     // UNIT TEST OUTPUT
#     FUNCTION output_details(final_state, duration):
#         PRINT "--- Solver Report ---"
#         PRINT "Nodes Explored: " + nodes_explored
#         PRINT "Backtracks: " + backtrack_count
#         PRINT "Time Elapsed: " + duration
        
#         IF final_state IS failure:
#             PRINT "Result: Failed to find solution"
#         ELSE:
#             PRINT "Result: Solution Found"
#             // Convert grid back to string for verification
#             PRINT "Solution String: " + grid_to_string(final_state)

def main():
    solver = SudokuAgent()
    
    
if __name__ == "__main__":
    main()