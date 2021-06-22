FROM python:3.9.5-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir intermine
RUN python ./RandomQueryGenerator/HumanMineGetDBSchema.py && mv HumanMinedbSchema.obj ./Data/Schemas/
RUN pip install --no-cache-dir gdown
RUN gdown $GDRIVE_MODEL_URL && mv model-HumanMine-1000000_step_2000.pt ./NLP/Models/

EXPOSE 1234
CMD [ "python", "./WebService.py" ]
