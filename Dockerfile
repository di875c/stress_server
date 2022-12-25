# образ на основе которого создаём контейнер
FROM python:3.8.10-alpine
# рабочая директория внутри проекта
WORKDIR /usr/src/stress_server

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Устанавливаем зависимости для Postgres
RUN apk update \
#    && apk add --no-cache --update \
    && apk add \
      python3-dev gcc g++ subversion postgresql-dev gfortran musl-dev

# устанавливаем зависимости
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
#RUN pip3 install numpy==1.23.5
RUN pip3 install -r requirements.txt

# копируем содержимое текущей папки в контейнер
COPY . .
