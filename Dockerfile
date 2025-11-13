FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y build-essential     && pip install --upgrade pip && pip install -r requirements.txt     && apt-get remove -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
