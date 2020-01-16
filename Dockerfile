# Basic docker image for MADevice
# Usage:
#   docker build -t madevice .
#   docker run -d -ti --name=madevice --restart=unless-stopped madevice

FROM python:3.7

# Working directory for the application
WORKDIR /usr/src/app

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python", "./main.py"]

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt


# Copy everything to the working directory (Python files, templates, config) in one go.
COPY . /usr/src/app/
