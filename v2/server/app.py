from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import math

# 添加Python算法文件路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

app = Flask(__name__)
CORS(app)

def generate_knot_methods(start_state, composition_color):
    """
    生成编绳结的方式，使得绳子颜色排列符合 composition_color，
    且最终绳子物理排列顺序与 start_state 相同。
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

    all_found_solutions = []

    def backtrack(current_line_idx, current_state, current_method_path, current_states_path):
        nonlocal all_found_solutions

        # Base case: All lines processed
        if current_line_idx == n_lines:
            if current_state == start_state:
                # Found a valid solution path
                all_found_solutions.append({
                    'method': [list(row) for row in current_method_path],
                    'states_path': [list(s) for s in current_states_path + [list(current_state)]],
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
                        return

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
                    if len(next_state) != n_strings:
                        return 

                # Recursive call to backtrack for the next line
                backtrack(current_line_idx + 1, next_state, 
                          current_method_path + [list(temp_method_row)], 
                          current_states_path + [list(next_state)])

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

    # Initiate the backtracking process
    backtrack(0, list(start_state), [], [list(start_state)]) 

    if not all_found_solutions:
        return None, []

    # Convert internal knot type abbreviations to symbols for display
    for solution in all_found_solutions:
        for r_idx, row in enumerate(solution['method']):
            for c_idx, knot_type_abbr in enumerate(row):
                solution['method'][r_idx][c_idx] = knot_mapping_symbols[knot_type_abbr]

    # Find the most concise method
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
                score += 1
        return score

    # Find the best solution
    best_solution_obj = None
    min_score = math.inf

    for solution in all_found_solutions:
        score = calculate_conciseness_score(solution)
        if score < min_score:
            min_score = score
            best_solution_obj = solution
        # You could add tie-breaking rules here if needed, e.g., if scores are equal,
        # choose the one with fewer total knot changes, or a specific visual pattern preference.

    print("\n--- 最简洁的编绳方法 ---")
    if best_solution_obj:
        print(f"总简洁度分数: {min_score}")
        print(f"最简洁的打结方式:\n {best_solution_obj['method']}")
        print(f"该方法对应的完整状态路径:")
        print(f"初始状态: {best_solution_obj['states_path'][0]}")
        for i in range(len(best_solution_obj['method'])):
            print(f"第 {i+1} 行打结方式: {best_solution_obj['method'][i]}")
            print(f"更新后状态: {best_solution_obj['states_path'][i+1]}")
        print(f"结束状态 (end_state): {best_solution_obj['end_state']}")
        print(f"与初始状态一致: {best_solution_obj['end_state'] == start_state}")
    else:
        print("未能找到最简洁的方法（此情况不应发生，如果 all_found_solutions 不为空）。")
    print("---------------------\n")

    return best_solution_obj, all_found_solutions

@app.route('/api/generate-knot', methods=['POST'])
def generate_knot():
    try:
        data = request.get_json()
        start_state = data.get('startState')
        composition_color = data.get('targetPattern')
        
        if not start_state or not composition_color:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 调用绳结算法
        best_solution_obj, all_solutions = generate_knot_methods(start_state, composition_color)
        
        if best_solution_obj is None:
            return jsonify({'error': '未找到符合条件的打结方式'}), 404
        
        result = {
            'startState': start_state,
            'targetPattern': composition_color,
            'bestSolution': best_solution_obj['method'],
            'statesPath': best_solution_obj['states_path'],
            'totalSolutions': len(all_solutions)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 