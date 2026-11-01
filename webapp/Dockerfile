FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# gunicorn sirve la app Flask (objeto 'app' en app.py).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
