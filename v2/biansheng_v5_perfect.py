## 向右打结一次：压在上面的绳子尾端水平向右
## 向左打结一次：压在上面的绳子尾端水平向左

import math

def generate_knot_methods(start_state, composition_color):
    """
    生成编绳结的方式，使得绳子颜色排列符合 composition_color，
    且最终绳子物理排列顺序与 start_state 相同。
    每次确定打结方式并输出后，输出使用该种打结方式之后的更新的state。
    最后一次打结方式确定后需计算end_state即结束状态并输出。
    同时，列出所有可能的编绳方法，并挑选出最简洁的方法。

    Args:
        start_state (list): 初始多股绳子的颜色排列顺序，例如 ['R', 'B', 'G', 'Y']。
        composition_color (list of list): 目标绳结颜色排列方式，例如
                                        [['R', 'G'], ['B', 'Y']]。

    Returns:
        tuple: (list of list: 最简洁的打结方式 (compositon_method),
                list of dict: 所有找到的解决方案及其详细信息)
               如果找不到任何方法，则返回 (None, [])。
    """
    n_strings = len(start_state)
    if n_strings % 2 != 0:
        raise ValueError("start_state 的长度必须是偶数。")

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

    all_found_solutions = [] # Stores all valid {method, states_path, end_state}

    def backtrack(current_line_idx, current_state, current_method_path, current_states_path):
        nonlocal all_found_solutions

        # Base case: All lines processed
        if current_line_idx == n_lines:
            if current_state == start_state:
                # Found a valid solution path
                all_found_solutions.append({
                    'method': [list(row) for row in current_method_path], # Deep copy
                    'states_path': [list(s) for s in current_states_path + [list(current_state)]], # Add final state
                    'end_state': list(current_state)
                })
            return # Don't return True/False, just return to explore other paths

        is_odd_line = (current_line_idx % 2 == 0)
        target_knot_colors = composition_color[current_line_idx]

        if is_odd_line:
            num_knots_in_line = n_knots_per_odd_line
            start_idx = 0
        else:
            num_knots_in_line = n_knots_per_even_line
            start_idx = 1
        
        if len(target_knot_colors) != num_knots_in_line:
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
                        return # Invalid state, prune branch

                    parent_string = [state_snapshot_for_line[parent_string_start_idx],
                                     state_snapshot_for_line[parent_string_start_idx + 1]]
                    
                    knot_type_str = temp_method_row[i]
                    rule = knot_rules[knot_type_str]
                    
                    new_order_indices = rule['new_order']
                    new_parent = [parent_string[new_order_indices[0]], parent_string[new_order_indices[1]]]
                    new_parent_strings_after_knots.append(new_parent)
                
                if is_odd_line:
                    for i in range(num_knots_in_line):
                        next_state.extend(new_parent_strings_after_knots[i])
                else: 
                    next_state.append(state_snapshot_for_line[0]) 
                    for i in range(num_knots_in_line):
                        next_state.extend(new_parent_strings_after_knots[i])
                    if n_strings > (start_idx + 2 * num_knots_in_line): 
                         next_state.append(state_snapshot_for_line[-1])
                    if len(next_state) != n_strings: # Important check for logical errors in state transformation
                        return 

                # Recursive call to backtrack for the next line
                backtrack(current_line_idx + 1, next_state, 
                          current_method_path + [list(temp_method_row)], 
                          current_states_path + [list(next_state)]) # Add this line's resulting state

                return # Continue exploring other knot combinations for this line
            
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


    # Initiate the backtracking process
    # The initial state is added to current_states_path for the first call
    backtrack(0, list(start_state), [], [list(start_state)]) 
    
    print("\n--- 绳结生成过程 ---")

    if not all_found_solutions:
        print("未能找到符合条件的打结方式。")
        print("---------------------\n")
        return None, []

    # --- Step 1: Format and print all found solutions ---
    print(f"找到 {len(all_found_solutions)} 种可能的编绳方法。\n")
    
    # Convert internal knot type abbreviations to symbols for display
    for solution in all_found_solutions:
        for r_idx, row in enumerate(solution['method']):
            for c_idx, knot_type_abbr in enumerate(row):
                solution['method'][r_idx][c_idx] = knot_mapping_symbols[knot_type_abbr]

    # # 打印所有可能的打结方法
    # for sol_idx, solution in enumerate(all_found_solutions):
    #     print(f"--- 方法 {sol_idx + 1} ---")
    #     print(f"初始状态: {solution['states_path'][0]}")
    #     for i in range(len(solution['method'])):
    #         print(f"第 {i+1} 行打结方式: {solution['method'][i]}")
    #         print(f"更新后状态: {solution['states_path'][i+1]}")
    #     print(f"结束状态 (end_state): {solution['end_state']}")
    #     print(f"与初始状态一致: {solution['end_state'] == start_state}")
    #     print("-" * 20)
    # print("---------------------\n")

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

    for solution in all_found_solutions:
        score = calculate_conciseness_score(solution)
        if score < min_score:
            min_score = score
            best_solution = solution
        # You could add tie-breaking rules here if needed, e.g., if scores are equal,
        # choose the one with fewer total knot changes, or a specific visual pattern preference.

    print("\n--- 最简洁的编绳方法 ---")
    if best_solution:
        print(f"总简洁度分数: {min_score}")
        print(f"最简洁的打结方式:\n {best_solution['method']}")
        print(f"该方法对应的完整状态路径:")
        print(f"初始状态: {best_solution['states_path'][0]}")
        for i in range(len(best_solution['method'])):
            print(f"第 {i+1} 行打结方式: {best_solution['method'][i]}")
            print(f"更新后状态: {best_solution['states_path'][i+1]}")
        print(f"结束状态 (end_state): {best_solution['end_state']}")
        print(f"与初始状态一致: {best_solution['end_state'] == start_state}")
    else:
        print("未能找到最简洁的方法（此情况不应发生，如果 all_found_solutions 不为空）。")
    print("---------------------\n")

    return best_solution['method'] if best_solution else None, all_found_solutions

# 示例 1: 简单的例子
start_state_1 = ['R', 'B', 'G', 'Y']
composition_color_1 = [['R', 'G'], ['B']] # This might have multiple ways to achieve it

most_concise_method_1, all_methods_1 = generate_knot_methods(start_state_1, composition_color_1)


print("-" * 30)

# 示例 2：复杂例子
# 在复杂例子中虽然生成的不是最优解（最方便记忆的传统解），但是是正确的
# 生成最优解的代码等待进一步更新
start_state_2 = ['R','R','W','W','R','R'] 
composition_color_2 = [
    ['R', 'W', 'R'], 
    ['R','R'],     
    ['R', 'W', 'R'],
    ['W','W'],
    ['R', 'W', 'R'],
    ['R','R']
]
most_concise_method_2, all_methods_2 = generate_knot_methods(start_state_2, composition_color_2)


# # 示例2 结果：
# --- 绳结生成过程 ---
# 找到 331776 种可能的编绳方法。
# --- 最简洁的编绳方法 ---
# 总简洁度分数: 9
# 最简洁的打结方式:
#  [['右右', '右右', '右右'], ['右左', '左右'], ['右右', '右右', '右右'], ['左右', '右左'], ['右 右', '右右', '右右'], ['右左', '左右']]
# 该方法对应的完整状态路径:
# 初始状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 1 行打结方式: ['右右', '右右', '右右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 2 行打结方式: ['右左', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 3 行打结方式: ['右右', '右右', '右右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 4 行打结方式: ['左右', '右左']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 5 行打结方式: ['右右', '右右', '右右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 6 行打结方式: ['右左', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 结束状态 (end_state): ['R', 'R', 'W', 'W', 'R', 'R']
# 与初始状态一致: True
# ---------------------





