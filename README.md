## Software Testing

# 50.053 Software Testing and Verification

## Running
```
python sudifuzz.py --config sudifuzz_config_example.ini
```

## Development Notes
### Testing individual modules
To run code from `if __name__ == "__main__"` in each individual module, run as module from root directory instead of python file directly.
For example, to run the file `oracle.py` found in directory `oracle` (ie `oracle/oracle.py`), run from project root directory (`SoftwareTesting2024/`)
```
python3 -m oracle.oracle
```

### Logging
Please use the python logger instead of `print` statements in code. Basic logging code to add to each file:
```
import logging

logger = logging.getLogger(__name__)
```