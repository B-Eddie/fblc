FROM python:3.10-slim

# Set working directory
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5050

CMD ["python", "app.py"]
