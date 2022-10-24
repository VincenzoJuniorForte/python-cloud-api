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

        response = session.post(
            base_url,
            json={'operation': '3 * x + 1 - y = 4', 'step': '3 * x + 1 - y = 4'}
        )
        assert response.status_code == 200
        assert response.json() == {
            "solution": "[{x: y/3 + 1}]",
            "is_correct": True,
            "is_last": False
        }
    finally:
        process.kill()
        process.wait()
