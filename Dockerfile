FROM python:3.8

# set current env
ENV HOME /app
WORKDIR /app
COPY . /app

# set app config option
ENV FLASK_DEBUG=1

# set argument vars in docker-run command
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

ENV AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION

RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app/src

#CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app", "--workers=5"]
CMD ["python3", "main.py"]