FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt update && apt install -y wget \
    && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN chmod +x /app/start.sh
CMD ["sh", "/app/start.sh"]
