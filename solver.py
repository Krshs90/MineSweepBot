import itertools
import math
from collections import defaultdict

class CSPSolver:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.directions = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),           (0, 1),
                           (1, -1),  (1, 0),  (1, 1)]

    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in self.directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def solve(self, board, total_mines=99):
        """
        Returns:
            perfect_safe: list of (row, col)
            perfect_mines: list of (row, col)
            best_guess: (row, col) or None
        """
        self.rows, self.cols = board.shape
        perfect_safe = set()
        perfect_mines = set()
        
        # 1. Simple Deterministic Pass
        for r in range(self.rows):
            for c in range(self.cols):
                val = board[r, c]
                if val > 0: # 1-8
                    unrevealed = []
                    flagged = 0
                    for nr, nc in self.get_neighbors(r, c):
                        n_val = board[nr, nc]
                        if n_val == -1:
                            unrevealed.append((nr, nc))
                        elif n_val == -3:
                            flagged += 1
                            
                    if flagged == val:
                        perfect_safe.update(unrevealed)
                    elif len(unrevealed) == val - flagged:
                        perfect_mines.update(unrevealed)

        if perfect_safe or perfect_mines:
            return list(perfect_safe), list(perfect_mines), None

        # 2. Advanced Global Probability DP logic
        frontier_constraints = [] 
        unknown_cells = set()
        flagged_total = 0
        unrevealed_total = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                val = board[r, c]
                if val == -3:
                    flagged_total += 1
                elif val == -1:
                    unrevealed_total += 1
                elif val > 0:
                    unrevealed = []
                    flagged = 0
                    for nr, nc in self.get_neighbors(r, c):
                        n_val = board[nr, nc]
                        if n_val == -1:
                            unrevealed.append((nr, nc))
                        elif n_val == -3:
                            flagged += 1
                    
                    if unrevealed:
                        frontier_constraints.append((val - flagged, unrevealed))
                        unknown_cells.update(unrevealed)
                        
        unknown_cells = list(unknown_cells)
        ocean_cells = unrevealed_total - len(unknown_cells)
        mines_left = total_mines - flagged_total
        
        # Blind guessing subroutine
        def get_blind_guess():
            all_unknowns = [(r, c) for r in range(self.rows) for c in range(self.cols) if board[r, c] == -1]
            if not all_unknowns: return None
            corners = [(0,0), (0, self.cols-1), (self.rows-1, 0), (self.rows-1, self.cols-1)]
            for corn in corners:
                if corn in all_unknowns: return corn
            for (r,c) in all_unknowns:
                if r == 0 or r == self.rows-1 or c == 0 or c == self.cols-1: return (r,c)
            return all_unknowns[0]
            
        # Fast local probability heuristic for when exact DP is too expensive
        def get_heuristic_guess():
            best_p = 1.0
            best_cell = None
            cell_p = {}
            for rm, cells in frontier_constraints:
                p = rm / len(cells) if len(cells) > 0 else 1.0
                for c in cells:
                    cell_p[c] = max(cell_p.get(c, 0.0), p)
            
            for c, p in cell_p.items():
                if p < best_p:
                    best_p = p
                    best_cell = c
                    
            ocean_p = mines_left / ocean_cells if ocean_cells > 0 else 1.0
            if ocean_cells > 0 and ocean_p < best_p:
                for r in range(self.rows):
                    for c in range(self.cols):
                        if board[r, c] == -1 and (r, c) not in unknown_cells:
                            if r == 0 or r == self.rows-1 or c == 0 or c == self.cols-1:
                                return (r, c)
                for r in range(self.rows):
                    for c in range(self.cols):
                        if board[r, c] == -1 and (r, c) not in unknown_cells:
                            return (r, c)
            
            if best_cell: return best_cell
            return get_blind_guess()
            
        if not unknown_cells or mines_left < 0:
            return [], [], get_blind_guess()

        # Group constraints into disjoint independent Islands
        adj_matrix = defaultdict(list)
        for _, cells in frontier_constraints:
            for i in range(len(cells)):
                for j in range(i + 1, len(cells)):
                    adj_matrix[cells[i]].append(cells[j])
                    adj_matrix[cells[j]].append(cells[i])

        visited = set()
        islands = []
        for cell in unknown_cells:
            if cell not in visited:
                island = []
                stack = [cell]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        island.append(curr)
                        for neighbor in adj_matrix[curr]:
                            stack.append(neighbor)
                islands.append(island)

        # Precompute possible mine distributions for each island
        island_configs = [] 
        island_cell_configs = [] 
        
        valid_overall = True
        
        for island in islands:
            island_set = set(island)
            local_constraints = []
            for remaining_mines, cells in frontier_constraints:
                if any(c in island_set for c in cells):
                    c_tuple = (remaining_mines, tuple(cells))
                    if c_tuple not in local_constraints:
                        local_constraints.append(c_tuple)
            
            valid_configs = []
            iter_count = [0]
            aborted = [False]
            MAX_ITER = 30000
            
            def backtrack(idx, current_config):
                if aborted[0]: return
                iter_count[0] += 1
                if iter_count[0] > MAX_ITER:
                    aborted[0] = True
                    return
                
                if idx == len(island):
                    for req_mines, cells in local_constraints:
                        mines_placed = sum(current_config[island.index(c)] for c in cells)
                        if mines_placed != req_mines: return
                    valid_configs.append(list(current_config))
                    return

                # Check safe (0) path
                current_config.append(0)
                possible = True
                for req_mines, cells in local_constraints:
                    placed = sum(current_config[island.index(c)] for c in cells if c in island[:idx+1])
                    unassigned = sum(1 for c in cells if c not in island[:idx+1])
                    if placed + unassigned < req_mines:
                        possible = False
                        break
                if possible: backtrack(idx + 1, current_config)
                current_config.pop()

                # Check mine (1) path
                current_config.append(1)
                possible = True
                for req_mines, cells in local_constraints:
                    placed = sum(current_config[island.index(c)] for c in cells if c in island[:idx+1])
                    if placed > req_mines:
                        possible = False
                        break
                if possible: backtrack(idx + 1, current_config)
                current_config.pop()

            backtrack(0, [])
            
            if aborted[0] or not valid_configs:
                valid_overall = False
                break
                
            w_i = defaultdict(int)
            w_ic = defaultdict(lambda: defaultdict(int))
            for config in valid_configs:
                m = sum(config)
                w_i[m] += 1
                for cell_idx, is_mine in enumerate(config):
                    if is_mine: w_ic[island[cell_idx]][m] += 1
                        
            island_configs.append(w_i)
            island_cell_configs.append(w_ic)

        if not valid_overall:
            return [], [], get_heuristic_guess()

        # Build Dynamic Programming Polynomial Arrays 
        def multiply_polynomials(p1, p2):
            res = defaultdict(int)
            for m1, c1 in p1.items():
                for m2, c2 in p2.items():
                    if m1 + m2 <= mines_left:
                        res[m1 + m2] += c1 * c2
            return res

        prefix_dp = [{0: 1}]
        for w_i in island_configs:
            prefix_dp.append(multiply_polynomials(prefix_dp[-1], w_i))
            
        TOTAL_BOARDS = 0
        final_dp = prefix_dp[-1]
        for m, count in final_dp.items():
            rem_m = mines_left - m
            if 0 <= rem_m <= ocean_cells:
                TOTAL_BOARDS += count * math.comb(ocean_cells, rem_m)
                
        if TOTAL_BOARDS == 0:
            return [], [], get_blind_guess()

        # Find absolute lowest probability cell globally
        best_mine_prob = 1.0
        best_guess = None
        global_safe = []
        global_mines = []
        
        # Calculate exactly the safety of an ocean cell
        ocean_safe_prob = -1.0 # Invalid baseline
        ocean_mine_prob = 1.0
        if ocean_cells > 0:
            expected_ocean_mines = 0.0
            for m, count in final_dp.items():
                rem_m = mines_left - m
                if 0 <= rem_m <= ocean_cells:
                    weight = count * math.comb(ocean_cells, rem_m)
                    expected_ocean_mines += weight * (rem_m / ocean_cells)
            ocean_mine_prob = expected_ocean_mines / TOTAL_BOARDS
            ocean_safe_prob = 1.0 - ocean_mine_prob

        # Calculate exact fractional percentages for frontier cells
        suffix_dp = [{0: 1}] * (len(islands) + 1)
        suffix_dp[len(islands)] = {0: 1}
        for i in range(len(islands) - 1, -1, -1):
            suffix_dp[i] = multiply_polynomials(suffix_dp[i+1], island_configs[i])
            
        for i, island in enumerate(islands):
            dp_others = multiply_polynomials(prefix_dp[i], suffix_dp[i+1])
            w_ic = island_cell_configs[i]
            
            for cell in island:
                mine_cases = 0
                for m_others, count_others in dp_others.items():
                    for m_island, count_mine_here in w_ic[cell].items():
                        m_total = m_others + m_island
                        rem_m = mines_left - m_total
                        if 0 <= rem_m <= ocean_cells:
                            mine_cases += count_others * count_mine_here * math.comb(ocean_cells, rem_m)
                            
                mine_prob = mine_cases / TOTAL_BOARDS
                
                # Check for 100% Guaranteed global limits
                if mine_prob == 0.0:
                    global_safe.append(cell)
                elif mine_prob == 1.0:
                    global_mines.append(cell)
                else:
                    if mine_prob < best_mine_prob:
                        best_mine_prob = mine_prob
                        best_guess = cell

        if global_safe or global_mines:
            return global_safe, global_mines, None
            
        # Compare best frontier guess with best ocean guess
        if ocean_cells > 0 and ocean_mine_prob < best_mine_prob:
            # Safest to dive into the ocean blindness
            for r in range(self.rows):
                for c in range(self.cols):
                    if board[r, c] == -1 and (r, c) not in unknown_cells:
                        if r == 0 or r == self.rows-1 or c == 0 or c == self.cols-1:
                            return [], [], (r, c)
            # Pick any ocean if no edges
            for r in range(self.rows):
                for c in range(self.cols):
                    if board[r, c] == -1 and (r, c) not in unknown_cells:
                        return [], [], (r, c)
                        
        return [], [], best_guess
