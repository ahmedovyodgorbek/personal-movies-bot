FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY r.txt .
RUN pip install --upgrade pip && pip install -r r.txt

COPY deployments/compose/django/start /start
RUN sed -i 's/\r$//g' /start && \
    chmod +x /start

# Copy project files
COPY . /

# By default, run the Django dev server
CMD ["docker-entrypoint.sh"]
