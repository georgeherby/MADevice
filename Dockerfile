# Basic docker image for RocketMap
# Usage:
#   docker build -t rocketmap .
#   docker run -d -P rocketmap -a ptc -u YOURUSERNAME -p YOURPASSWORD -l "Seattle, WA" -st 10 --gmaps-key CHECKTHEWIKI

FROM python:3.6

# Working directory for the application
WORKDIR /usr/src/app

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python", "./main.py"]

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt


# Copy everything to the working directory (Python files, templates, config) in one go.
COPY . /usr/src/app/
