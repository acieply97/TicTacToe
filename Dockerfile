FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY game_logic/static /app/game_logic/static
COPY game_logic/templates /app/game_logic/templates
COPY game_logic/*.py /app/game_logic
COPY *.py /app

EXPOSE 5000

CMD [ "python", "run.py" ]