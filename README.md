# Equal Prototype - Cloud Function API Endpoint
## Usage
When deployed to Google Cloud, this function is available via a POST request with a JSON body with the following fields :


    {
        "user_id": <String>,
        "exercise_id": <String>,
	    "operation": <String>, // e.g. "3 * x = 3"
	    "step": <String>, // e.g. "x = 3 / 3",
        "task": "expand", // optional
    }

## Requirements
  - python 3.10
  - google cloud CLI ([installation instructions](https://cloud.google.com/sdk/docs/install))
  - firebase CLI ([installation instructions](https://firebase.google.com/docs/cli#setup_update_cli))

## Deploying
Clone the repository, install the CLI tools and initialize them with a google account with admin rights, then run the following command

    ./scripts/deploy.sh

## Dependencies
The following command will read dependencies from `requirements.txt` and install them. If you add a dependency to the source code of the function, add it to `requirements.txt` (you can use `python freeze` to get the exact version)

    ./scripts/init.sh

## Serving the endpoint on localhost

    ./scripts/serve_local.sh

Running this command will make the function available on localhost:8080 via HTTP

## Running the tests

    ./scripts/run_tests.sh

