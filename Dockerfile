FROM python:latest

WORKDIR /src
# COPY requirements.txt requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . /src
# CMD ["flask", "run"]
# CMD ["flask", "run"]

CMD [ "python", "./src/app.py" ]