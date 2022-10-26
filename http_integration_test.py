import os
import subprocess
import uuid

import requests
from requests.packages.urllib3.util.retry import Retry
import firebase_admin
from firebase_admin import firestore


# Adapted from https://cloud.google.com/functions/docs/testing/test-http#integration_tests
def test():
    port = os.getenv('PORT', 8080)
    process = subprocess.Popen(
        [
            'functions-framework',
            '--target', 'http_handler',
            '--port', str(port)
        ],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE
    )

    base_url = f'http://localhost:{port}'
    session = requests.Session()
    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
        max_retries=retry_policy)
    session.mount(base_url, retry_adapter)

    try:
        response = session.get(base_url)
        assert response.status_code == 405

        response = session.post(base_url)
        assert response.status_code == 400

        base_payload = {
            'user_id': 'test-user-1',
            'exercise_id': 'test-exercise-1',
        }

        response = session.post(
            base_url,
            json=base_payload | {'operation': '3 * x + 1 - y = 4', 'step': '3 * x + 1 - y = 4'}
        )
        assert response.status_code == 200
        assert response.json() == {
            "solution": "[{x: y/3 + 1}]",
            "is_correct": True,
            "is_last": False
        }

        response = session.post(
            base_url,
            json=base_payload | {'operation': '(3 * x) * (3 * y)', 'step': '(3 * x) * (3 * y)', 'task': 'factor'}
        )
        assert response.status_code == 200
        assert response.json() == response.json() | {'solution': '9*x*y'}

        app = firebase_admin.initialize_app()
        firestore_client = firebase_admin.firestore.client(app)
        documents = firestore_client.collection('users',
                                                'test-user-1',
                                                'exercises',
                                                'test-exercise-1',
                                                'events').recursive().get()
        
    finally:
        process.kill()
        process.wait()
