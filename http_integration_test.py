import os
import subprocess
import uuid

import requests
from requests.packages.urllib3.util.retry import Retry


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

    BASE_URL = f'http://localhost:{port}'
    session = requests.Session()
    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
        max_retries=retry_policy)
    session.mount(BASE_URL, retry_adapter)

    try:
        response = session.get(
            BASE_URL,
        )
        assert response.status_code == 400

        response = session.get(
            BASE_URL,
            json={'operation': '3x + 1 = 4', 'step': '3x = 4 - 1'}
        )
        assert response.status_code == 200
        assert response.json() == { 'fake': 'json' }
    finally:
        process.kill()
        process.wait()
