# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg\
    tesseract-ocr\
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/streamlit/streamlit-example.git .

RUN pip3 install -r requirements.txt

EXPOSE 85

HEALTHCHECK CMD curl --fail http://localhost:85/_stcore/health

ENTRYPOINT ["python", "run_engines.py", "streamlit", "run", "Home.py", "--server.port=85", "--server.maxUploadSize=25", "--server.address=0.0.0.0"]