FROM --platform=amd64 python:3.12.2-bullseye

# Install required packages
RUN apt update
RUN apt install -y python2 gdb
RUN rm -rf /var/lib/apt/lists/*
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" && python get-pip.py && rm get-pip.py

# Django
RUN curl -o django.tar.gz -L "https://www.dropbox.com/scl/fi/tza2fawtt89a17qv2mrop/DjangoWebApplication.tar.gz?rlkey=38bmjle1992nge8d01acgw9sd&dl=1"
RUN tar -xzvf django.tar.gz && rm django.tar.gz
WORKDIR /DjangoWebApplication
RUN pip3 install -r requirements.txt

# CoAP
WORKDIR /
RUN curl -o coap.zip -L "https://www.dropbox.com/scl/fi/oscwf7knoo6ev8azh1y79/CoAPthon.zip?rlkey=4jbijamzeu80d4fq360e3d359&dl=1"
RUN unzip coap.zip && rm coap.zip
WORKDIR /CoAPthon
RUN python2 setup.py sdist
RUN pip install dist/CoAPthon-4.0.2.tar.gz -r requirements.txt

# Sudifuzz
WORKDIR /sudifuzz
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

ENTRYPOINT ["python3", "sudifuzz.py", "--config"]
CMD ["sudifuzz_config_example.ini"]