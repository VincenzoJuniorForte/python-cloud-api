import datetime
import uuid

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import functions_framework
from google.cloud import error_reporting
from google.auth.exceptions import DefaultCredentialsError
from flask import abort
import firebase_admin
from firebase_admin import firestore

try:
    error_reporting_client = error_reporting.Client()
except DefaultCredentialsError:
    error_reporting_client = None

try:
    app = firebase_admin.initialize_app()
    firestore_client = firebase_admin.firestore.client(app)
except DefaultCredentialsError:
    app = None
    firestore_client = None


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

    if not params or not all(key in params for key in ('operation', 'step', 'user_id', 'exercise_id')):
        return 'Missing params', 400

    try:
        raw_solution, is_correct, is_last = calculate(params['operation'], params['step'], params.get('task', None))
        formatted_solution = str(raw_solution)

        try:
            now = datetime.datetime.utcnow()
            document = firestore_client.document('users',
                                                 params['user_id'],
                                                 'exercises',
                                                 params['exercise_id'],
                                                 'events',
                                                 str(uuid.uuid4()))
            data = {
                'input_operation': params['operation'],
                'input_step': params['step'],
                'input_task': params.get('task', None),
                'output_solution': formatted_solution,
                'output_is_correct': is_correct,
                'output_is_last': is_last,
                'created_at': now,
                'updated_at': now,
            }
            document.create(data)
        except Exception as e:
            report_exception(error_reporting_client, e)

        return {
            'solution': formatted_solution,
            'is_correct': is_correct,
            'is_last': is_last
        }
    except Exception as e:
        report_exception(error_reporting_client, e)
        abort(500)


def report_exception(client, exception):
    if client:
        client.report_exception()
    print(repr(exception))


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
