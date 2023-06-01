# Equal Prototype - Cloud Function API Endpoint
## Usage
When deployed to Google Cloud, this function is available via a POST request with a JSON payload:

    // POST JSON payload
    {
        "user_id": <String>,
        "exercise_id": <String>,
	    "operation": <String>, // e.g. "3 * x = 3",
	    "step": <String>, // e.g. "x = 3 / 3",
        "step_number": <Number>,// e.g. 1
        "task": "expand", // optional
    }
    // Response payload
    {
        "solution": "9*x*y"
        "is_correct": true,
        "is_last": true,
    }


## Deploy
### Requirements
- google cloud CLI ([installation instructions](https://cloud.google.com/sdk/docs/install))
### Instructions
Clone the repository, then run the following command :

    scripts/deploy.sh

## Develop
### Requirements
- python 3.10
- google cloud CLI ([installation instructions](https://cloud.google.com/sdk/docs/install))
- firebase CLI ([installation instructions](https://firebase.google.com/docs/cli#setup_update_cli))
- Java OpenJDK 11 (debian : package `openjdk-11-jdk` ; other OS -> [instructions](https://openjdk.org/install/))
- Node JS

### Run the calculate function only

    scripts/run_calculate.sh <arguments to the calculate function>

### Serve the HTTP function on localhost

    scripts/serve_local.sh

Running this command will make the Python function available on localhost:8080 via HTTP.

It will also emulate the Firestore database locally on localhost:8081 (the DB can be monitored at http://127.0.0.1:4000/firestore).

The function can be triggered with `scripts/trigger.sh`

    ./scripts/trigger.sh '{"operation": "x = 1", "step": "x = 1", "user_id": "user-1", "exercise_id": "exercise-1"}'

Or directly with curl

    curl -v localhost:8080 \
    -H 'Content-Type: application/json' \
    -d '{"operation": "x = 1", "step": "x = 1", "user_id": "user-1", "exercise_id": "exercise-1"}'

### Env and adding Python dependencies

To run `pip install` and other python commands correctly, first run the following command from the repository root

  source .venv/bin/activate

If you add a dependency to the python source code, add it to `requirements.txt` (you can use `python freeze` to get the exact version)

### Run & add tests

    ./scripts/run_tests.sh

If you add a dependency to the tests, add it to `test_requirements.txt`
