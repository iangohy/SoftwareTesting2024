## Software Testing
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

- open terminal1
    - python3 manage.py runserver  
- open terminal2
    - python3 DjangoTestDriver.py

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