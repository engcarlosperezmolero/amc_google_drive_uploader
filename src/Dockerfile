# Use an x86_64 compatible base image
FROM --platform=linux/amd64 python:3.12

# Set up your environment and install dependencies
WORKDIR /src
COPY /src /src
RUN pip install -r requirements.txt