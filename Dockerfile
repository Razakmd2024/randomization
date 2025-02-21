FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV PORT=10000

# Configure Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "300", "--workers", "1", "--threads", "4", "python","app:app"]