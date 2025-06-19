## 向右打结一次：压在上面的绳子尾端水平向右
## 向左打结一次：压在上面的绳子尾端水平向左

def generate_knot_methods(start_state, composition_color):
    """
    生成编绳结的方式，使得绳子颜色排列符合 composition_color，
    且最终绳子物理排列顺序与 start_state 相同。
    每次确定打结方式并输出后，输出使用该种打结方式之后的更新的state。
    最后一次打结方式确定后需计算end_state即结束状态并输出。

    Args:
        start_state (list): 初始多股绳子的颜色排列顺序，例如 ['R', 'B', 'G', 'Y']。
        composition_color (list of list): 目标绳结颜色排列方式，例如
                                        [['R', 'G'], ['B', 'Y']]。

    Returns:
        list of list: 与 composition_color 对应的打结方式 (compositon_method)，
                      如果找不到则返回 None。
                      打结方式为 'RR', 'LL', 'RL', 'LR'。
                      'RR' 代表右右, 'LL' 代表左左, 'RL' 代表右左, 'LR' 代表左右。
    """
    n_strings = len(start_state)
    if n_strings % 2 != 0:
        raise ValueError("start_state 的长度必须是偶数。")

    n_lines = len(composition_color)
    n_knots_per_odd_line = n_strings // 2
    n_knots_per_even_line = (n_strings // 2) - 1

    knot_rules = {
        'RR': {'knot_color_idx': 0, 'new_order': [1, 0]},
        'LL': {'knot_color_idx': 1, 'new_order': [1, 0]},
        'RL': {'knot_color_idx': 0, 'new_order': [0, 1]},
        'LR': {'knot_color_idx': 1, 'new_order': [0, 1]},
    }
    
    knot_mapping_symbols = {
        'RR': '右右',
        'LL': '左左',
        'RL': '右左',
        'LR': '左右',
    }

    final_composition_method = []
    # step_by_step_states 现在只在找到解之后构建，或者用于临时路径记录
    
    calculated_end_state = None
    
    # 修改 backtrack 函数，让它返回找到的完整路径（包括方法和状态）
    def backtrack(current_line_idx, current_state, current_method_path):
        nonlocal final_composition_method, calculated_end_state

        if current_line_idx == n_lines:
            if current_state == start_state:
                final_composition_method = [list(row) for row in current_method_path]
                calculated_end_state = list(current_state)
                # 成功找到路径，返回 True
                return True, [list(start_state)] # 返回 True 和一个包含初始状态的列表，后续状态将在此基础上添加
            return False, [] # 未找到有效结束状态

        is_odd_line = (current_line_idx % 2 == 0)
        target_knot_colors = composition_color[current_line_idx]

        if is_odd_line:
            num_knots_in_line = n_knots_per_odd_line
            start_idx = 0
        else:
            num_knots_in_line = n_knots_per_even_line
            start_idx = 1
        
        if len(target_knot_colors) != num_knots_in_line:
            return False, []

        temp_method_row = [''] * num_knots_in_line
        
        # 这个内部函数需要返回是否找到当前行的解，以及当前行结束后的状态
        def find_knots_for_current_line(knot_idx, current_line_state_snapshot):
            nonlocal temp_method_row

            if knot_idx == num_knots_in_line:
                next_state = []
                new_parent_strings_after_knots = []
                
                for i in range(num_knots_in_line):
                    parent_string_start_idx = start_idx + 2 * i
                    if parent_string_start_idx + 1 >= len(current_line_state_snapshot):
                        return False, []

                    parent_string = [current_line_state_snapshot[parent_string_start_idx],
                                     current_line_state_snapshot[parent_string_start_idx + 1]]
                    
                    knot_type_str = temp_method_row[i]
                    rule = knot_rules[knot_type_str]
                    
                    new_order_indices = rule['new_order']
                    new_parent = [parent_string[new_order_indices[0]], parent_string[new_order_indices[1]]]
                    new_parent_strings_after_knots.append(new_parent)
                
                if is_odd_line:
                    for i in range(num_knots_in_line):
                        next_state.extend(new_parent_strings_after_knots[i])
                else: 
                    next_state.append(current_line_state_snapshot[0]) 
                    for i in range(num_knots_in_line):
                        next_state.extend(new_parent_strings_after_knots[i])
                    if n_strings > (start_idx + 2 * num_knots_in_line): 
                         next_state.append(current_line_state_snapshot[-1])
                    if len(next_state) != n_strings:
                        return False, []

                # 递归调用 backtrack
                # current_method_path 会在递归调用中构建
                # 我们传递 current_method_path 的一个新副本加上当前行的打结方式
                found_solution, states_path = backtrack(current_line_idx + 1, next_state, current_method_path + [list(temp_method_row)])
                
                if found_solution:
                    # 如果找到了解决方案，将当前行的下一个状态添加到路径中
                    return True, [list(next_state)] + states_path
                return False, []
            
            parent_string_start_idx = start_idx + 2 * knot_idx
            
            if parent_string_start_idx + 1 >= len(current_line_state_snapshot):
                return False, []

            parent_string = [current_line_state_snapshot[parent_string_start_idx],
                             current_line_state_snapshot[parent_string_start_idx + 1]]
            
            for knot_type, rule in knot_rules.items():
                knot_color_index = rule['knot_color_idx']
                
                if parent_string[knot_color_index] == target_knot_colors[knot_idx]:
                    temp_method_row[knot_idx] = knot_type
                    # 递归调用以处理下一个绳结
                    found_solution, states_path = find_knots_for_current_line(knot_idx + 1, current_line_state_snapshot)
                    if found_solution:
                        return True, states_path
            return False, []

        return find_knots_for_current_line(0, current_state)

    print("\n--- 绳结生成过程 ---")
    
    # 调用 backtrack，并接收返回的 states_path
    found_solution, step_by_step_states = backtrack(0, list(start_state), []) 

    if found_solution: 
        # 确保 final_composition_method 已经被正确设置 (在 backtrack 内部)
        for r_idx, row in enumerate(final_composition_method):
            for c_idx, knot_type_abbr in enumerate(row):
                final_composition_method[r_idx][c_idx] = knot_mapping_symbols[knot_type_abbr]
        
        print(f"初始状态: {step_by_step_states[0]}")
        for i in range(len(final_composition_method)):
            print(f"第 {i+1} 行打结方式: {final_composition_method[i]}")
            # 这里的 i+1 是因为 step_by_step_states[0] 是初始状态
            # final_composition_method[i] 对应的是第 i+1 次打结后的状态 (step_by_step_states[i+1])
            print(f"更新后状态: {step_by_step_states[i+1]}") 
        
        print(f"结束状态 (end_state): {calculated_end_state}")
        print(f"与初始状态一致: {calculated_end_state == start_state}")
        print("---------------------\n")

        return final_composition_method
    else:
        print("未能找到符合条件的打结方式。")
        print("---------------------\n")
        return None


# 示例 1: 简单的例子
start_state_1 = ['R', 'B', 'G', 'Y']
composition_color_1 = [['R', 'G'], ['B']] 

print(f"Start State 1: {start_state_1}")
print(f"Composition Color 1: {composition_color_1}")
composition_method_1 = generate_knot_methods(start_state_1, composition_color_1)

if composition_method_1:
    print(f"最终 Composition Method 1:\n {composition_method_1}")
else:
    print("未能找到符合条件的打结方式。")

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
print(f"Start State 2: {start_state_2}")
print(f"Composition Color 2: {composition_color_2}")
composition_method_2 = generate_knot_methods(start_state_2, composition_color_2)

if composition_method_2:
    print(f"最终 Composition Method 2:\n {composition_method_2}")
else:
    print("未能找到符合条件的打结方式。")

# 示例2 结果：
# --- 绳结生成过程 ---
# 初始状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 1 行打结方式: ['右右', '右右', '右右']
# 更新后状态: ['R', 'W', 'R', 'W', 'R', 'R']
# 第 2 行打结方式: ['右右', '左右']
# 更新后状态: ['R', 'W', 'R', 'W', 'R', 'R']
# 第 3 行打结方式: ['右左', '左右', '右右']
# 更新后状态: ['R', 'R', 'W', 'R', 'W', 'R']
# 第 4 行打结方式: ['右右', '右右']
# 更新后状态: ['R', 'R', 'W', 'R', 'W', 'R']
# 第 5 行打结方式: ['右右', '右左', '左右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 第 6 行打结方式: ['右左', '右右']
# 更新后状态: ['R', 'R', 'W', 'W', 'R', 'R']
# 结束状态 (end_state): ['R', 'R', 'W', 'W', 'R', 'R']
# 与初始状态一致: True




