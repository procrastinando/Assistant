# Assistant
A telegram bot with multiple functions

Build the container (name: assistant):

```
FROM python:3.9-slim

WORKDIR /app

RUN python -m venv /translator
RUN /translator/bin/pip install --upgrade pip
RUN /translator/bin/pip install argostranslate

RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    gcc \
    g++ \
    curl \
    software-properties-common \
    git \
    ffmpeg\
    tesseract-ocr\
    && rm -rf /var/lib/apt/lists/*\
    && /usr/local/bin/python -m pip install --upgrade pip

RUN git clone https://github.com/procrastinando/Assistant.git .

RUN if [ -x "$(command -v nvidia-smi)" ]; then \
        pip3 install torch torchvision torchaudio; \
    else \
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    fi

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

RUN chmod +x /app/start.sh

ENTRYPOINT ["./start.sh"]
```

```
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    gcc \
    g++ \
    curl \
    software-properties-common \
    git \
    ffmpeg\
    tesseract-ocr\
    && rm -rf /var/lib/apt/lists/*\
    && /usr/local/bin/python -m pip install --upgrade pip

RUN git clone https://github.com/procrastinando/Assistant.git .

RUN if [ -x "$(command -v nvidia-smi)" ]; then \
        pip3 install torch torchvision torchaudio; \
    else \
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    fi

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

RUN chmod +x /app/start.sh

ENTRYPOINT ["./start.sh"]
```

Docker compose:

```
version: '3'
services:
  app:
    image: assistant
    ports:
      - "85:8501"
    restart: unless-stopped
```
To do:
* Show statistics of activity (user and members)
* Create a priority scale
* Create a user agree and welcome message
* Create a news distribution function
* Register with discord?
