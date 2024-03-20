# Test Drivers with Coverage

## CoAP
### Pre-requisites
As our target runs on Python 2, ensure you have `coverage` version 5.5 installed. This can be done by running `python2 -m pip install coverage`. You should be able to run the `coverage2` command in your terminal and confirm the version number by running `coverage2 --version`.

### Implementation
To be added.

## Django
### Pre-requisites
As our target runs on Python 3, ensure you have `coverage` version 7.x installed. This can be done by running `python3 -m pip install coverage`. You should be able to run the `coverage3` command in your terminal and confirm the version number by running `coverage3 --version`.

### Implementation
Within `DjangoTestDriver.py` you may find a `send_request_2` function that is built to perform coverage.

Before running the Driver it is helpful to ensure the configuration constants are correct and that their directories exist if applicable:
- `DJANGO_DIRECTORY`: The directory to the Django Application
- `TEST_TEMPLATE_FILE`: The template Python file that the test driver will apply variables for Django Testing.
- `TEST_OUTPUT_FILE`: An output from a template file that will be used for Django Testing.
- `COVERAGE_JSON_FILE`: An output file which `coverage` will report on various line and branch executions.
- `MISSING_BRANCHES_FILE`: A store of missing branches left to cover for the current run of coverage tests that will be used to determine whether an input is considered interesting and will be saved.

The `send_request_2` function takes in the following:
- `endpoint: str`: A valid endpoint. Running Django testing allows us to forgo prefixing a hostname.
- `input_data: Any`: This is the body input that will be used for the endpoint.
- `method: str`: The HTTP Request method. This can take the form of `post | get | put | delete | patch`.
- `coverage: bool`: Whether coverage will be performed.