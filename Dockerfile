FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN apt update -y && apt install -y awscli

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "python src/PortfolioOptimizer/pipeline/pipeline.py && python main.py"]
