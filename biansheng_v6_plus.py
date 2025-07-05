import math
import itertools

def generate_knot_methods(composition_color):
    """
    生成编绳结的方式，使得绳子颜色排列符合 composition_color。
    同时，确定一个初始绳子颜色排列顺序 start_state，使得最终绳子物理排列顺序与 start_state 相同。
    每次确定打结方式并输出后，输出使用该种打结方式之后的更新的state。
    最后一次打结方式确定后需计算end_state即结束状态并输出。
    同时，列出所有可能的编绳方法，并挑选出最简洁的方法。

    Args:
        composition_color (list of list): 目标绳结颜色排列方式，例如
                                         [['R', 'G'], ['B', 'Y']]。

    Returns:
        tuple: (list: 最简洁方法的初始状态 (start_state),
                list of list: 最简洁的打结方式 (compositon_method),
                list of dict: 所有找到的解决方案及其详细信息)
                如果找不到任何方法，则返回 (None, None, [])。
    """
    if not composition_color:
        return None, None, []

    # Determine n_strings based on the first line of composition_color
    n_strings_initial_guess = len(composition_color[0]) * 2
    
    # If the first line is odd, then it's a bit more complex,
    # let's assume the first line always dictates the full number of strings for now.
    # We should infer n_strings from the line with the maximum number of knots.
    max_knots_in_any_line = 0
    for line in composition_color:
        max_knots_in_any_line = max(max_knots_in_any_line, len(line))
    
    n_strings = max_knots_in_any_line * 2 if (len(composition_color[0]) == max_knots_in_any_line) else (max_knots_in_any_line + 1) * 2 # Heuristic, might need refinement
    
    if n_strings % 2 != 0:
        # This case should ideally not happen if composition_color is well-formed
        # for a continuous braiding pattern.
        return None, None, []

    n_lines = len(composition_color)
    n_knots_per_odd_line = n_strings // 2
    n_knots_per_even_line = (n_strings // 2) - 1

    knot_rules = {
        'RR': {'knot_color_idx': 0, 'new_order': [1, 0], 'type': 'swapping'},
        'LL': {'knot_color_idx': 1, 'new_order': [1, 0], 'type': 'swapping'},
        'RL': {'knot_color_idx': 0, 'new_order': [0, 1], 'type': 'non-swapping'},
        'LR': {'knot_color_idx': 1, 'new_order': [0, 1], 'type': 'non-swapping'},
    }
    
    knot_mapping_symbols = {
        'RR': '右右',
        'LL': '左左',
        'RL': '右左',
        'LR': '左右',
    }

    all_potential_solutions = [] # Stores all valid {start_state, method, states_path, end_state}

    # Extract all unique colors from composition_color to generate start_state permutations
    unique_colors = set()
    for line in composition_color:
        for color in line:
            unique_colors.add(color)
    unique_colors = sorted(list(unique_colors)) # Sort for consistent permutation generation

    # Generate all permutations of colors for the start_state
    # The number of strings in start_state must match n_strings
    # This might be computationally expensive for many unique colors/large n_strings
    
    # We need to ensure that the number of strings in start_state is consistent
    # with the expected structure of the composition_color (odd/even lines).
    # If the first line of composition_color has 'k' knots, then n_strings = 2k.
    # If the second line has 'k-1' knots, then n_strings = 2(k-1) + 2 = 2k.
    
    # A more robust way to determine n_strings:
    # The number of strings is fixed. The number of knots on an odd line is n_strings / 2.
    # The number of knots on an even line is (n_strings / 2) - 1.
    # We can infer n_strings from the composition_color structure.
    
    # Let's re-evaluate n_strings based on the given composition_color
    inferred_n_strings = 0
    for i, line in enumerate(composition_color):
        if i % 2 == 0: # Odd line (0, 2, ...)
            current_n_strings = len(line) * 2
        else: # Even line (1, 3, ...)
            current_n_strings = (len(line) + 1) * 2 # Each knot involves 2 strings, plus 2 unknotted
        
        if inferred_n_strings == 0:
            inferred_n_strings = current_n_strings
        elif inferred_n_strings != current_n_strings:
            # If the number of strings implied by different lines is inconsistent,
            # it indicates an invalid composition_color structure.
            print(f"Error: Inconsistent number of strings inferred from composition_color. Line {i} implies {current_n_strings} strings, but previous lines imply {inferred_n_strings}.")
            return None, None, []
    
    n_strings = inferred_n_strings
    
    # Now generate permutations for this inferred n_strings
    
    # To reduce permutations, if colors repeat, we should consider multisets.
    # For now, let's just use simple permutations of the unique colors for a fixed length.
    # A better approach might be to count the occurrences of each color in composition_color
    # and use that to generate start_state permutations.
    
    # For simplicity and to allow for repeating colors in start_state,
    # let's assume `start_state` will have the same counts of colors as the
    # *sum* of colors in all composition_color lines, or a more constrained set.
    # A simpler way: just permute all unique colors, and if we need more strings than unique colors,
    # we'd need to consider repetition.
    
    # Let's generate permutations of colors, assuming all colors in composition_color
    # must appear in start_state, and start_state has n_strings elements.
    
    # For a robust solution, we need to know the *exact* required color counts for start_state.
    # This is often derived from the desired 'braid diagram' or by inferring from the `composition_color`.
    # Without this, we would need to try all combinations of colors up to n_strings.
    
    # To simplify, we'll generate initial states from the unique colors.
    # If the number of strings is larger than the number of unique colors, we will
    # pad the unique colors to create an initial candidate string set.
    
    # A more practical approach is to determine the counts of each color if possible.
    # But without more context on the `composition_color` and how it relates to initial counts,
    # we will resort to a common pattern: if start_state has repeated colors, it's often
    # a pattern like R R W W.
    
    # Let's try to generate start_state candidates by permuting the colors from the composition_color
    # repeated to match n_strings. This is a simplification.
    
    # Get the flat list of all colors in the target composition
    all_target_colors = [color for sublist in composition_color for color in sublist]
    
    # Create a frequency map for the colors in the target composition
    target_color_counts = {}
    for color in all_target_colors:
        target_color_counts[color] = target_color_counts.get(color, 0) + 1

    # Heuristic for start_state candidates:
    # If a color appears N times in the composition_color (total sum of knots),
    # it's reasonable to assume it appears roughly N / (number of lines) times in start_state.
    # A simpler approach: try permutations of unique colors up to n_strings, possibly with repetitions.
    
    # Let's generate candidate start_states by trying permutations of the unique colors,
    # up to the total length of n_strings.
    
    # For the `start_state_1 = ['R', 'B', 'G', 'Y']` and `composition_color_1 = [['R', 'G'], ['B']]` case:
    # n_strings = 4. Unique colors = R, B, G, Y. We need permutations of these 4 colors.
    
    # For `start_state_2 = ['R','R','W','W','R','R']` and `composition_color_2`:
    # n_strings = 6. Unique colors = R, W.
    # Permutations of ['R', 'R', 'R', 'R', 'W', 'W'] or similar could be tried.
    
    # To handle repeated colors in start_state, we need `itertools.permutations` on a list
    # that includes repetitions. The most reliable way to get this list of repeated colors
    # for `start_state` is often from the problem definition or by inferring it from `composition_color`.
    # A common inference for simple patterns: if a color appears in `composition_color` multiple times,
    # it likely also appears multiple times in `start_state`.
    
    # Let's refine `unique_colors` to be the actual pool of colors we'd expect in `start_state`.
    # A common pattern is that the `start_state` will have the same *set* of colors as the `composition_color`
    # and the counts might be related.
    # For now, let's simply create a pool of colors from the *unique* colors found, and repeat them
    # to match `n_strings` for initial permutations, but this is a rough approximation.
    
    # A more robust approach for generating start_state candidates would be:
    # 1. Determine the exact counts of each color if possible (e.g., if there's a constraint like "2 red, 2 blue").
    # 2. If not, infer based on total color occurrences or common braiding patterns.
    # Let's try to infer initial color counts for start_state.
    
    # The total number of knots across all lines in composition_color gives some hint.
    # The sum of colors in `start_state` should usually be preserved throughout the braiding.
    
    # Let's try to use the unique colors found in `composition_color` and generate permutations
    # of length `n_strings`, allowing repetitions if `n_strings > len(unique_colors)`.
    # This requires a more complex permutation generation or a direct construction of candidate lists.
    
    # For now, let's generate candidate `start_state` lists by taking permutations
    # of the `unique_colors` list, and repeating elements if `n_strings > len(unique_colors)`.
    
    # This is a critical point: how to generate *meaningful* `start_state` candidates.
    # If the `start_state` colors are a subset of unique_colors from `composition_color` and
    # `len(unique_colors)` is small, permutations work.
    
    # Example: If `composition_color` only has 'R' and 'W', and `n_strings` is 6,
    # then `start_state` could be ['R', 'R', 'R', 'W', 'W', 'W'] or similar.
    # A more direct approach: build a list of all `n_strings` items by repeating unique colors.
    # E.g., if unique_colors is ['R', 'B'] and n_strings is 4, then ['R', 'R', 'B', 'B'] could be a base.
    
    # Let's try a simpler approach for generating start_state candidates:
    # Create a list of colors that is `n_strings` long, filled with unique_colors.
    # Then permute that list. This will handle cases like ['R', 'R', 'W', 'W'].
    
    candidate_color_pool = []
    if len(unique_colors) > 0:
        # Distribute the unique colors as evenly as possible to form the initial pool
        for i in range(n_strings):
            candidate_color_pool.append(unique_colors[i % len(unique_colors)])
    else:
        # No colors in composition_color, this is an invalid input
        return None, None, []

    # Generate all unique permutations of the candidate_color_pool
    start_state_candidates = list(set(itertools.permutations(candidate_color_pool, n_strings)))
    start_state_candidates = [list(s) for s in start_state_candidates] # Convert tuples to lists
    
    # Sort for consistent processing, if desired (not strictly necessary for correctness)
    start_state_candidates.sort() # Sorting helps in debugging and consistent output

    print(f"推断的绳子总数 (n_strings): {n_strings}")
    print(f"生成的初始状态候选数量: {len(start_state_candidates)}\n")

    for current_start_state_candidate in start_state_candidates:
        temp_all_found_solutions_for_candidate = [] # Stores solutions for this specific start_state_candidate
        
        def backtrack(current_line_idx, current_state, current_method_path, current_states_path):
            nonlocal temp_all_found_solutions_for_candidate

            # Base case: All lines processed
            if current_line_idx == n_lines:
                if current_state == current_start_state_candidate: # Check against the current start_state candidate
                    # Found a valid solution path for this start_state_candidate
                    temp_all_found_solutions_for_candidate.append({
                        'start_state': list(current_start_state_candidate), # Record the start_state that worked
                        'method': [list(row) for row in current_method_path], # Deep copy
                        'states_path': [list(s) for s in current_states_path + [list(current_state)]], # Add final state
                        'end_state': list(current_state)
                    })
                return

            is_odd_line = (current_line_idx % 2 == 0)
            target_knot_colors = composition_color[current_line_idx]

            if is_odd_line:
                num_knots_in_line = n_knots_per_odd_line
                start_idx = 0
            else:
                num_knots_in_line = n_knots_per_even_line
                start_idx = 1
            
            if len(target_knot_colors) != num_knots_in_line:
                # This line in composition_color doesn't match the expected number of knots.
                # This indicates an invalid composition_color structure for the inferred n_strings,
                # or a logical error in the inference of num_knots_in_line.
                return

            temp_method_row = [''] * num_knots_in_line
            
            def find_knots_for_current_line(knot_idx, state_snapshot_for_line):
                nonlocal temp_method_row

                if knot_idx == num_knots_in_line:
                    next_state = []
                    new_parent_strings_after_knots = []
                    
                    for i in range(num_knots_in_line):
                        parent_string_start_idx = start_idx + 2 * i
                        if parent_string_start_idx + 1 >= len(state_snapshot_for_line):
                            return # Invalid state, prune branch (shouldn't happen with correct n_strings inference)

                        parent_string = [state_snapshot_for_line[parent_string_start_idx],
                                         state_snapshot_for_line[parent_string_start_idx + 1]]
                        
                        knot_type_str = temp_method_row[i]
                        rule = knot_rules[knot_type_str]
                        
                        new_order_indices = rule['new_order']
                        new_parent = [parent_string[new_order_indices[0]], parent_string[new_order_indices[1]]]
                        new_parent_strings_after_knots.append(new_parent)
                    
                    # Construct next_state based on whether it's an odd or even line
                    if is_odd_line:
                        for i in range(num_knots_in_line):
                            next_state.extend(new_parent_strings_after_knots[i])
                    else: # Even line
                        if start_idx == 1 and n_strings > 0: # Check if there's a first string not knotted
                            next_state.append(state_snapshot_for_line[0]) 
                        for i in range(num_knots_in_line):
                            next_state.extend(new_parent_strings_after_knots[i])
                        if n_strings > (start_idx + 2 * num_knots_in_line) and (start_idx + 2 * num_knots_in_line) < len(state_snapshot_for_line):
                            # Add the last unknotted string if it exists
                            next_state.append(state_snapshot_for_line[-1])
                            
                    if len(next_state) != n_strings: # Important check for logical errors in state transformation
                        return 

                    # Recursive call to backtrack for the next line
                    backtrack(current_line_idx + 1, next_state, 
                              current_method_path + [list(temp_method_row)], 
                              current_states_path + [list(next_state)]) # Add this line's resulting state

                    return
                    
                parent_string_start_idx = start_idx + 2 * knot_idx
                
                if parent_string_start_idx + 1 >= len(state_snapshot_for_line):
                    return

                parent_string = [state_snapshot_for_line[parent_string_start_idx],
                                 state_snapshot_for_line[parent_string_start_idx + 1]]
                
                for knot_type, rule in knot_rules.items():
                    knot_color_index = rule['knot_color_idx']
                    
                    if parent_string[knot_color_index] == target_knot_colors[knot_idx]:
                        temp_method_row[knot_idx] = knot_type
                        # Recursive call to find knots for the next pair in the current line
                        find_knots_for_current_line(knot_idx + 1, state_snapshot_for_line)
                return

            find_knots_for_current_line(0, current_state)

        # Initiate the backtracking process for the current start_state_candidate
        backtrack(0, list(current_start_state_candidate), [], [list(current_start_state_candidate)])
        all_potential_solutions.extend(temp_all_found_solutions_for_candidate)

    print("\n--- 绳结生成过程 ---")

    if not all_potential_solutions:
        print("未能找到符合条件的打结方式。")
        print("---------------------\n")
        return None, None, []

    # --- Step 1: Format and print all found solutions ---
    print(f"找到 {len(all_potential_solutions)} 种可能的编绳方法。\n")
    
    # Convert internal knot type abbreviations to symbols for display
    for solution in all_potential_solutions:
        for r_idx, row in enumerate(solution['method']):
            for c_idx, knot_type_abbr in enumerate(row):
                solution['method'][r_idx][c_idx] = knot_mapping_symbols[knot_type_abbr]

    # --- Step 2: Find the most concise method ---
    def calculate_conciseness_score(method_data):
        score = 0
        for line_knots_abbrev in method_data['method']:
            # Convert back to internal abbreviation for scoring
            line_knots = [next(k for k, v in knot_mapping_symbols.items() if v == sym) for sym in line_knots_abbrev]
            
            # 1. Unique knot types score
            unique_types = set(line_knots)
            score += len(unique_types)

            # 2. Symmetry penalty score
            swapping_types = {'RR', 'LL'}
            non_swapping_types = {'RL', 'LR'}
            
            has_swapping = any(kt in swapping_types for kt in line_knots)
            has_non_swapping = any(kt in non_swapping_types for kt in line_knots)

            if has_swapping and has_non_swapping:
                score += 1 # Penalty for mixing swapping and non-swapping operations
        return score

    # Find the best solution
    best_solution = None
    min_score = math.inf

    for solution in all_potential_solutions:
        score = calculate_conciseness_score(solution)
        if score < min_score:
            min_score = score
            best_solution = solution
        # Tie-breaking: if scores are equal, prioritize methods with more "symmetric" knot types (e.g., all RR or all RL)
        # or fewer overall knot types. The current scoring already implicitly favors fewer unique types.

    print("\n--- 最简洁的编绳方法 ---")
    if best_solution:
        print(f"总简洁度分数: {min_score}")
        print(f"推断的初始状态 (start_state): {best_solution['start_state']}")
        print(f"最简洁的打结方式:\n {best_solution['method']}")
        print(f"该方法对应的完整状态路径:")
        print(f"初始状态: {best_solution['states_path'][0]}")
        for i in range(len(best_solution['method'])):
            print(f"第 {i+1} 行打结方式: {best_solution['method'][i]}")
            print(f"更新后状态: {best_solution['states_path'][i+1]}")
        print(f"结束状态 (end_state): {best_solution['end_state']}")
        print(f"与初始状态一致: {best_solution['end_state'] == best_solution['start_state']}")
    else:
        print("未能找到最简洁的方法（此情况不应发生，如果 all_potential_solutions 不为空）。")
    print("---------------------\n")

    return best_solution['start_state'] if best_solution else None, \
           best_solution['method'] if best_solution else None, \
           all_potential_solutions

# 示例 1: 简单的例子
composition_color_1 = [['R', 'G'], ['B']]
start_state_1_inferred, most_concise_method_1, all_methods_1 = generate_knot_methods(composition_color_1)
print(f"示例 1 推断的初始状态: {start_state_1_inferred}")
print(f"示例 1 最简洁的方法: {most_concise_method_1}")

print("\n" + "=" * 50 + "\n")

# 示例 2：复杂例子
composition_color_2 = [
    ['R', 'W', 'R'], 
    ['R','R'],    
    ['R', 'W', 'R'],
    ['W','W'],
    ['R', 'W', 'R'],
    ['R','R']
]
start_state_2_inferred, most_concise_method_2, all_methods_2 = generate_knot_methods(composition_color_2)
print(f"示例 2 推断的初始状态: {start_state_2_inferred}")
print(f"示例 2 最简洁的方法: {most_concise_method_2}")

###  示例2 输出：
# 推断的绳子总数 (n_strings): 6
# 生成的初始状态候选数量: 20
# --- 绳结生成过程 ---
# 找到 53160 种可能的编绳方法。
# --- 最简洁的编绳方法 ---
# 总简洁度分数: 8
# 推断的初始状态 (start_state): ['R', 'R', 'W', 'W', 'R', 'W']
# 最简洁的打结方式:
#  [['右左', '右左', '右左'], ['右左', '左右'], ['右右', '右右', '右右'], ['左右', '左右'], ['左 左', '左左', '左左'], ['右左', '左右']]
# 该方法对应的完整状态路径:
# 初始状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 第 1 行打结方式: ['右左', '右左', '右左']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 第 2 行打结方式: ['右左', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 第 3 行打结方式: ['右右', '右右', '右右']
# 更新后状态: ['R', 'R', 'W', 'W', 'W', 'R']
# 第 4 行打结方式: ['左右', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'W', 'R']
# 第 5 行打结方式: ['左左', '左左', '左左']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 第 6 行打结方式: ['右左', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 结束状态 (end_state): ['R', 'R', 'W', 'W', 'R', 'W']
# 与初始状态一致: True
# ---------------------
# 示例 2 推断的初始状态: ['R', 'R', 'W', 'W', 'R', 'W']
# 示例 2 最简洁的方法: [['右左', '右左', '右左'], ['右左', '左右'], ['右右', '右右', '右右'], [' 左右', '左右'], ['左左', '左左', '左左'], ['右左', '左右']]

print("\n" + "=" * 50 + "\n")

# 示例 3: 新增示例，测试不同数量的绳子和颜色
composition_color_3 = [['R', 'B', 'R', 'B'], ['R', 'B', 'R']] 
start_state_3_inferred, most_concise_method_3, all_methods_3 = generate_knot_methods(composition_color_3)
print(f"示例 3 推断的初始状态: {start_state_3_inferred}")
print(f"示例 3 最简洁的方法: {most_concise_method_3}")