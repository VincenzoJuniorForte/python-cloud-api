import json

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import functions_framework
from google.cloud import error_reporting
from google.auth.exceptions import DefaultCredentialsError
from flask import abort

try:
    client = error_reporting.Client()
except DefaultCredentialsError:
    client = None


@functions_framework.http
def http_handler(request):
    """ HTTP endpoint deployed on Google Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    if request.method != 'POST':
        return '', 405

    request_json = request.get_json(silent=True)
    params = request_json

    if not params or not all(key in params for key in ('operation', 'step')):
        return 'Missing params', 400

    try:
        solution, is_correct, is_last = calculate(params['operation'], params['step'], params.get('task', None))
        return {
            'solution': str(solution),
            'is_correct': is_correct,
            'is_last': is_last
        }
    except Exception:
        if client:
            client.report_exception()
        abort(500)


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
        solution = solve(lhs - rhs)

        step_cmp = step.split("=")
        lhs_step = parse_expr(step_cmp[0])
        rhs_step = parse_expr(step_cmp[1])
        solution_step = solve(lhs_step - rhs_step)

        is_correct = solution == solution_step
        if is_correct:
            if isinstance(lhs_step, Symbol) and not rhs_step.free_symbols:
                is_last = True

        return solution, is_correct, is_last

    if '=' in operation:
        return solve_equation(operation, step)
    else:
        return solve_expression(operation, step)
