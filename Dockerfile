FROM python:3.10-slim

WORKDIR /

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 34661

CMD ["python", "app.py"]
