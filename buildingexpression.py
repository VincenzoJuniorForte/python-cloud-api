from sympy import *

def extract_parts(expr, idd=1):
    parts = []
    for arg in expr.args:
        if isinstance(arg, (Symbol, Integer)):
            parts.append(arg)
        elif hasattr(arg, 'args'):
            sub_expr = extract_parts(arg, (idd + 1))
            parts.append(sub_expr)
    return {expr.func.__name__: parts, 'idd': idd}

def build_expression(tree):
    #if isinstance(tree, Integer):
    items = list(tree.items())[0]
    func_name = items[0]
    func = eval(func_name)
    args = items[1]
    parts = []
    for arg in args:
        #print(arg)
        if isinstance(arg, dict):
            parts.append(build_expression(arg))
        else:
            parts.append(arg)
    return func(*parts, evaluate=False)

def get_highest_idd(tree):
    highest_idd = tree['idd']
    if 'idd' in tree:
        highest_idd = max(highest_idd, tree['idd'])
    for key, value in tree.items():
        if type(value) == list:
            for sub_tree in value:
                if type(sub_tree) == dict:
                    highest_idd = max(highest_idd, get_highest_idd(sub_tree))
    return highest_idd

def evaluate_expression(expression, idd):
    results = []
    if idd == 0:
        return 
    if isinstance(expression, dict):
        if expression['idd'] == idd:
            operation = list(expression.keys())[0]
            values = expression[operation]
            results = []
            for value in values:
                if isinstance(value, dict):
                    value = build_expression(value)
                    results.append(simplify(value))
                else:
                    results.append(value)
            return {operation: results}
        else:
            new_expression = {}
            for key, sub_expr in expression.items():
                if isinstance(sub_expr, list):
                    new_sub_expr = []
                    for value in sub_expr:
                        if type(value) == dict:
                            evaluated_value = evaluate_expression(value, idd)
                            if evaluated_value:
                                new_sub_expr.append(evaluated_value)
                        else:
                            new_sub_expr.append(value)
                    if new_sub_expr:
                        new_expression[key] = new_sub_expr
                else:
                    new_expression[key] = sub_expr
            return new_expression
    return expression
x = Symbol('x')
ex = "(2*x + 3*x - 4*x) * (- 4 + 3*x)"
#{'Mul': [{'Add': [{'Mul': [2, x], 'idd': 3}, {'Mul': [3, x], 'idd': 3}, {'Mul': [-1, {'Mul': [4, x], 'idd': 4}], 'idd': 3}], 'idd': 2},
#{'Add': [-4, {'Mul': [3, x], 'idd': 3}], 'idd': 2}], 'idd': 1}
expr = parse_expr(ex, evaluate=False)
#print(expr)
tree = extract_parts(expr, 1)
print(tree)
max_idd = get_highest_idd(tree)
new_tree = evaluate_expression(tree, 1)
#print(new_tree)
new_expr = build_expression(new_tree)
if new_expr == expr:
    new_tree == evaluate_expression(tree, max_idd - 1)
    new_expr = build_expression(new_tree)
    print("ciao")
print(new_expr)
#print(expand(new_expr))
