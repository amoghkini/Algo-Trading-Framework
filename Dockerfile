FROM python:3.8
WORKDIR /app
COPY . /app

RUN apt update -y && apt install awscli -y

RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app/src

CMD ["python3", "main.py"]  