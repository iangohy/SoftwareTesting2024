## Software Testing

# 50.053 Software Testing and Verification

## Running (Docker)
```
# Django
docker build -t sudifuzz .
## Unix
docker run -v ./logs/:/sudifuzz/logs sudifuzz sudifuzz_config_django_example.ini
## Windows
docker run -v "$(PWD)/logs:/sudifuzz/logs" sudifuzz sudifuzz_config_django_example.ini

# CoAP
docker build -t sudifuzz .
## Unix
docker run -v ./logs/:/sudifuzz/logs sudifuzz sudifuzz_config_coap_example.ini
## Windows
docker run -v "$(PWD)/logs:/sudifuzz/logs" sudifuzz sudifuzz_config_coap_example.ini

# BLE
docker build -t sudifuzz_ubuntu -f Dockerfile_ubuntu .
## Unix
docker run -v ./logs/:/sudifuzz/logs sudifuzz_ubuntu sudifuzz_config_bt_example.ini
## Windows
docker run -v "$(PWD)/logs:/sudifuzz/logs" sudifuzz_ubuntu sudifuzz_config_bt_example.ini
```

## Running (without Docker)
```
python sudifuzz.py --config sudifuzz_config_<target_app>_example.ini
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

## Test Drivers
### For Coap

- open terminal1
    - sudo gdb -ex run -ex backtrace --args python2 coapserver.py -i 127.0.0.1 -p 5683 
- open terminal2
    - python3 CoapTestDriver.py
- troubleshoot
    - lsof -i:8080 
    - sudo lsof -t -i :8080   
    - sudo kill -9 [PID]


### For Django

Original:
- open terminal1
    - python3 manage.py runserver  
- open terminal2
    - python3 DjangoTestDriver.py

With Coverage:
- run `python3 DjangoTestDriver.py`
- Read more in `testdriver/README.md`

### For Bluetooth (run testdriver first)

- open terminal1
    - python3 BluetoothTestDriver.py tcp-server:127.0.0.1:9000
- open terminal2
    - GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ./zephyr.exe --bt-dev=127.0.0.1:9000 
- coverage
    - lcov --capture --directory ./ --output-file lcov.info -q --rc lcov_branch_coverage=1
    - lcov --rc lcov_branch_coverage=1 --summary lcov.info


### Change File permission
- chmod u+rx myscript.sh
- chmod +x zephyr.exe