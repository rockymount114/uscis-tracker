FROM python:3.11-slim

WORKDIR /app

# Install basic system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app:create_app()
ENV FLASK_ENV=production

# Run database upgrade and start the application
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:5000 'app:create_app()'"]
