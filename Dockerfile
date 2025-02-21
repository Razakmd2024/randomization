FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=10000

# Start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "300", "--workers", "1", "--threads", "4", "app:app"]
