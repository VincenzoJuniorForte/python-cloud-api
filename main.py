import datetime
import uuid
import traceback

from sympy import *
from next_step import *
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

    try:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }

            return '', 204, headers
        headers = {
            'Access-Control-Allow-Origin': '*'
        }

        if request.method != 'POST':
            return {'error': 'Bad method. Allowed methods: [POST]'}, 405, headers

        request_json = request.get_json()
        params = request_json

        if not params or not all(
                key in params for key in ('operation', 'step', 'step_number', 'user_id', 'exercise_id', 'last_correct')):
            return {'error': 'Missing params'}, 400, headers

        raw_solution, is_correct, is_last = calculate(params['operation'], params['step'], params.get('task', None))
        formatted_solution = str(raw_solution)
        raw_new_step, new_step = next_step(params['last_correct'])
        track_event(params, formatted_solution, is_correct, is_last, new_step)

        return {
                   'solution': formatted_solution,
                   'is_correct': is_correct,
                   'is_last': is_last,
                   'new_step': new_step
               }, 200, headers
    except Exception as e:
        report_exception(error_reporting_client, e)
        abort(500)


def track_event(params, formatted_solution, is_correct, is_last, new_step):
    try:
        batch = firestore_client.batch()
        user = firestore_client.collection('users').document(params['user_id'])
        exercise = user.collection('exercises').document(params['exercise_id'])
        event = exercise.collection('events').document()
        data = {
            'input': {
                'operation': params['operation'],
                'step': params['step'],
                'task': params.get('task', None),
                'step_number': params['step_number'],
                'last_correct' :params['last_correct']
            },
            'output': {
                'solution': formatted_solution,
                'is_correct': is_correct,
                'is_last': is_last,
                'new_step': new_step,
            },
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
        }
        batch.set(user, {'id': params['user_id'], 'updated_at': firestore.SERVER_TIMESTAMP})
        batch.set(exercise, {'id': params['exercise_id'], 'updated_at': firestore.SERVER_TIMESTAMP})
        batch.set(event, data)
        batch.commit()
    except Exception as e:
        report_exception(error_reporting_client, e)


def report_exception(client, exception):
    if client:
        client.report_exception()
    traceback.print_exc()

def next_step(step):
    step_solver = AdvanceEq(step)
    new_step, string_eq = step_solver.eq_do_step(1)
    return new_step, string_eq

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
        op = parse_expr(op, transformations='all', evaluate=False)
        step = parse_expr(step, transformations='all', evaluate=False)
        
        if task == 'expand':
            last = expand(op)

        else:
            last = factor(op)

        is_correct = simplify(op - step) == 0
        is_last = step == last

        return last, is_correct, is_last

    def solve_equation(eq, step):
        is_last = False

        eq_cmp = eq.split("=")
        lhs = parse_expr(eq_cmp[0], transformations='all')
        rhs = parse_expr(eq_cmp[1], transformations='all')
        solution = solve(lhs - rhs)

        step_cmp = step.split("=")
        lhs_step = parse_expr(step_cmp[0], transformations='all', evaluate=False)
        rhs_step = parse_expr(step_cmp[1], transformations='all')
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

