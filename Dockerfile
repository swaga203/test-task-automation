FROM python:3.11-slim

# Устанавливаем Apache, mod_wsgi, а также системные python3-psycopg2 и python3-flask
RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3-psycopg2 \
    python3-flask \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt


RUN mkdir -p /app/uploads && \
    chown -R www-data:www-data /app && \
    chmod -R 777 /app/uploads

COPY . /app/
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

RUN a2enmod wsgi

EXPOSE 80


CMD ["sh", "-c", "mkdir -p /app/uploads && chown -R www-data:www-data /app/uploads && chmod -R 777 /app/uploads && apache2ctl -D FOREGROUND"]