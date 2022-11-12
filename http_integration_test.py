# Adapted from https://cloud.google.com/functions/docs/testing/test-http#integration_tests

import os
import subprocess

import pytest
import requests
from requests.packages.urllib3.util.retry import Retry
import firebase_admin
from firebase_admin import firestore


@pytest.fixture(scope='session', autouse=True)
def setup():
    # Will be executed before the first test
    process = subprocess.Popen(
        [
            'functions-framework',
            '--target', 'http_handler',
            '--port', '8082'
        ],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE
    )

    base_url = f'http://localhost:8082'
    http_session = requests.Session()
    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
        max_retries=retry_policy)
    http_session.mount(base_url, retry_adapter)

    yield {'http_session': http_session, 'base_url': base_url}

    # Will be executed after the last test
    process.kill()
    process.wait()


@pytest.fixture
def call_function(setup):
    def _call_function(payload={}):
        return setup['http_session'].post(setup['base_url'], json=payload)

    return _call_function


@pytest.fixture
def default_payload():
    return {
        'user_id': 'test-user-1',
        'exercise_id': 'test-exercise-1',
        'operation': 'x = 1',
        'step': 'x = 1',
        'step_number': 0,
    }


def test_only_post_method(setup):
    response = setup['http_session'].get(setup['base_url'])
    assert response.status_code == 405


def test_wrong_arguments(call_function):
    response = call_function()
    assert response.status_code == 400


def test_equation(call_function, default_payload):
    response = call_function(default_payload | {
        'operation': '3 * x + 1 - y = 4',
        'step': '3 * x + 1 - y = 4'
    })

    assert response.status_code == 200
    assert response.json() == {
        "solution": "[{x: y/3 + 1}]",
        "is_correct": True,
        "is_last": False
    }

def test_input_format(call_function, default_payload):
    response = call_function(default_payload | {
        'operation': '(3x + 1)(3/2y + x) = 4',
        'step': '(3x + 1)(3/2y + x) = 4'
    })

    assert response.status_code == 200
    assert response.json() == {
        "solution": "[{y: 2*(-3*x**2 - x + 4)/(3*(3*x + 1))}]",
        "is_correct": True,
        "is_last": False
    }


def test_factor(call_function, default_payload):
    response = call_function(default_payload | {
        'operation': '(3 * x) * (3 * y)',
        'step': '(3 * x) * (3 * y)',
        'task': 'factor'
    })
    assert response.status_code == 200
    assert response.json() == {
        "solution": "9*x*y",
        "is_correct": True,
        "is_last": True
    }


def test_track_events_firestore(call_function, default_payload):
    app = firebase_admin.initialize_app()
    firestore_client = firebase_admin.firestore.client(app)

    cleanup_firestore(firestore_client)

    call_function(default_payload)
    call_function(default_payload)

    events = firestore_client.collection('users',
                                         'test-user-1',
                                         'exercises',
                                         'test-exercise-1',
                                         'events').recursive().get()

    first_event = events[0].to_dict()
    assert first_event == first_event | {
        'input': {
            'operation': 'x = 1',
            'step': 'x = 1',
            'step_number': 0,
            'task': None,
        },
        'output': {
            'solution': '[1]',
            'is_last': True,
            'is_correct': True,
        }
    }
    assert len(events) == 2


def cleanup_firestore(client):
    def zap_document(document):
        for collection in document.collections():
            zap_collection(collection)
        document.delete()

    def zap_collection(collection):
        for document in collection.list_documents():
            zap_document(document)

    for collection in client.collections():
        zap_collection(collection)
