import argparse
import numpy as np

from sympy.abc import *
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
# import functions_framework

parser = argparse.ArgumentParser()
parser.add_argument('-op', '--operation', type=str, help='initial operation')
parser.add_argument('-step', '--step', type=str, help='last input from user')
parser.add_argument('-task', '--task', default='expand', type=str, help='extra input from exercise instructions')
args = parser.parse_args()

operation = args.operation
step = args.step
task = args.task

#@functions_framework.http
def calculate(operation, step, task='expand'):
    """
    Function to evaluate single step of mathematical expressions or equations

    Input:
        - initial operation
        - current step
        - task (for expressions only): expand, factor, ... (more to come)

    Returns:
        - final solution
        - is_correct
        - is_last
    """
    
    def solve_expression(op, step):
        op = parse_expr(op)
        step = parse_expr(step)
        
        if task == 'expand':
            last = expand(op)

        elif task == 'factor':
            last = factor(op)

        is_correct = simplify(op - step) == 0
        is_last = step == last

        return last, is_correct, is_last
    
    def solve_equation(eq, step):
        is_last = False
        
        eq_cmp = eq.split("=")
        lhs = parse_expr(eq_cmp[0])
        rhs = parse_expr(eq_cmp[1])
        solution = solve(lhs-rhs)
        
        step_cmp = step.split("=")
        lhs_step = parse_expr(step_cmp[0])
        rhs_step = parse_expr(step_cmp[1])
        solution_step = solve(lhs_step-rhs_step)
        
        is_correct = solution == solution_step 
        if is_correct:
            if isinstance(lhs_step, Symbol) and not rhs_step.free_symbols:
                is_last = True
            
        return solution, correct, is_last

    
    if '=' in operation:
        return solve_equation(operation, step)
    else:
        return solve_expression(operation,step)
