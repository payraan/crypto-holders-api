FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# استفاده از پورت 8082 به جای 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
