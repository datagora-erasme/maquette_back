FROM python:3.8-slim
ENV TZ=Europe/Paris
RUN mkdir -p /var/www
RUN apt update
RUN apt install ffmpeg libglu1-mesa libsm6 libxext6 libxmu6 -y && rm -rf /var/lib/apt/lists/*
COPY . /var/www/back/
WORKDIR /var/www/back/
RUN pip3 install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "run.py", "-e", "contact@exo-dev.fr", "-p", "Dev"]