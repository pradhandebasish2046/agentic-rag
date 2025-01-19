FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app
COPY chainlit.md chainlit.md
RUN pip install -r requirements.txt

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]