FROM python:3.9.5-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 1234
CMD [ "python", "./WebService.py" ]
