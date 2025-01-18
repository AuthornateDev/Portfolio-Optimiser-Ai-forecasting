FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN mkdir -p /app/static && chmod 777 /app/static

RUN apt-get update \
    && apt-get upgrade -y 

RUN pip3 install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "mkdir -p /app/static && python src/PortfolioOptimizer/pipeline/pipeline.py && python main.py"]