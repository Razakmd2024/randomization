FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# Set environment variable for dynamic port
ENV PORT=10000

# Start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "300", "--workers", "1", "--threads", "4", "app:app"]
