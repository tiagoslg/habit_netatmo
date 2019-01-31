FROM python:3.6

ARG requirements_file

RUN mkdir -p /app
WORKDIR /app
ADD requirements/ .
RUN ls -l
RUN pip install --upgrade pip
RUN pip install -r $requirements_file
