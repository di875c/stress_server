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
      postgresql-dev 
	  #gfortran musl-dev g++ subversion python3-dev gcc 

# устанавливаем зависимости
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# копируем содержимое текущей папки в контейнер
COPY . .

# производим предварительную настройку

ENTRYPOINT ["/usr/src/stress_server/entrypoint.sh"]