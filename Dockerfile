#DOCKERFILE PYTHON+DJANGO

FROM python:3.6
WORKDIR /var/app
#RUN adduser --disabled-password --gecos '' www-data
COPY ./requirements.txt ./


RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    apt-utils \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    python3-pip

RUN wget -qO- https://deb.nodesource.com/setup_16.x | bash -
RUN apt install -y nodejs

RUN pip install --no-cache-dir -r ./requirements.txt 
COPY . .
EXPOSE 8000






