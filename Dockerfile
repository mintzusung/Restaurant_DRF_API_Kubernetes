FROM python:3.9-slim

WORKDIR /APIsProject

# 安裝系統套件：gcc、MySQL client dev、pkg-config
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 安裝 pipenv
RUN pip install pipenv

# 複製 Pipfile & Pipfile.lock
COPY Pipfile Pipfile.lock ./

# 安裝 Python 套件
RUN pipenv install --system --deploy

# 複製 Django 專案
COPY . /APIsProject/

EXPOSE 8000

CMD ["gunicorn", "APIsProject.wsgi:application", "--bind", "0.0.0.0:8000"]
