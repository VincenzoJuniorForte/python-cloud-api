# Equal Prototype - Cloud Function API Endpoint
## Usage
When deployed to Google Cloud, this function is available via a POST request with a JSON body with the following fields :


    {
	    "operation": "3 * x = 3",
	    "step": "3 * x = 3",
        "task": "expand", // optional
    }

## Requirements
  - python 3.10
  - google cloud CLI ([installation instructions](https://cloud.google.com/sdk/docs/install))

## Deploying
Clone the repository, make sure the google cloud CLI is installed and initialized with the correct account and project, the run the following command

    ./scripts/deploy.sh

## Dependencies
The following command will read dependencies from `requirements.txt` and install them. If you add a dependency to the source code of the function, add it to `requirements.txt` (you can use `python freeze` to get the exact version)

    ./scripts/init.sh

## Serving the endpoint on localhost

    ./scripts/serve.sh

Running this command will make the function available on localhost:8080 via HTTP

## Running the tests

    ./scripts/run_tests.sh

