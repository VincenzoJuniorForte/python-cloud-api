import sympy as sp
from sympy import *

def extract_parts(expr, idd=1):
    """
    Creates a dictionary "tree" from a sympy parsed expression

    Args:
        expr: parsed sympy expression
        idd (optional): Depth identifier(starts from idd and goes deeper). Defaults to 1.

    Returns:
        tree: a dictionary with operation and depth as keys and operators as values
    """
    parts = []
    for arg in expr.args:
        if isinstance(arg, (Symbol, Integer)):
            parts.append(arg)
        elif hasattr(arg, 'args'):
            sub_expr = extract_parts(arg, (idd + 1))
            parts.append(sub_expr)
    return {expr.func.__name__: parts, 'idd': idd}

def build_expression(tree):
    """
    Rebuilds from a "tree" dictionary to a sympy parsed expression

    Args:
        tree: dictionary "tree"

    Returns:
        expr: sympy parsed expression
    """
    items = list(tree.items())[0]
    func_name = items[0]
    func = eval(func_name)
    args = items[1]
    parts = []
    for arg in args:
        if isinstance(arg, dict):
            parts.append(build_expression(arg))
        else:
            parts.append(arg)
    return func(*parts, evaluate=False)

def get_highest_idd(tree):
    """
    Finds the highest depth of the dict tree

    Args:
        tree: dictionary "tree"

    Returns:
        idd: highest 'idd'(depth) in the tree
    """
    highest_idd = tree['idd']
    if 'idd' in tree:
        highest_idd = max(highest_idd, tree['idd'])
    for key, value in tree.items():
        if type(value) == list:
            for sub_tree in value:
                if type(sub_tree) == dict:
                    highest_idd = max(highest_idd, get_highest_idd(sub_tree))
    return highest_idd

def check_step(expr, new_expr, tree, idd):
    """
    wip. checks if the math step made has been useful

    Args:
        expr: the expression before the step
        new_expr: the new expression
        tree: dictionary "tree" (of older expression)
        idd: max depth of tree (cant be 0)
    
    Returns:
        new_expr: new sympy parsed expression with the first useful step made
    """
    s_exp = sorted(str(expr))
    s_new_exp = sorted(str(new_expr))
    ex = expand(expr)
    new_ex = expand(new_expr)
    while (s_exp == s_new_exp) and (ex == new_ex):
        idd -= 1
        s_new_exp = sorted(str(new_expr))
        if idd == 0:
            return(expand(new_expr))
        new_tree = evaluate_expression(tree, idd)
        new_expr = build_expression(new_tree)
    return(new_expr)

def evaluate_expression(expression, idd):
    """
    evaluates "tree" at depth idd

    Args:
        expression: dictionary "tree" of the expression to evaluate
        idd: depth at which you want to evaluate

    Returns:
        expression: dictionary "tree" of the new expression
    """
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

def expr_do_step(expr):
    """
    function to evaluate the next step of a mathematical expression

    Args:
        expr: sympy parsed expression

    Returns:
        new_expr: new expression with next useful step done
    """
    tree = extract_parts(expr, 1)
    mxid = get_highest_idd(tree)
    ntree = evaluate_expression(tree, 1)
    new_expr = build_expression(ntree)
    new_expr = check_step(expr, new_expr, tree, mxid)
    return (new_expr)

x = Symbol('x')
ex = "(2*x + 3*x - 4*x**2 + 2*x**2) * (3*x -4)"
expr = parse_expr(ex, evaluate=False)
print(expr)
new_expr = expr_do_step(expr)
print(new_expr)
new_expr = expr_do_step(new_expr)
print(new_expr)