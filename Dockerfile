FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    TELEGRAM_CE_DATA_DIR=/app/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# dedicated unprivileged user; owns /app/data so the session volume stays writable
RUN useradd --create-home tguser \
    && mkdir -p /app/data \
    && chown -R tguser:tguser /app/data
USER tguser

CMD ["python", "-m", "app"]
