FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY consumer.py ./
RUN mkdir -p ./database
CMD ["python", "consumer.py"]
