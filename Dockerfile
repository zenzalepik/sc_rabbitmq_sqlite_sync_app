FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set timezone
ENV TZ=Asia/Jakarta

# Default command (will be overridden by docker-compose)
CMD ["python", "sync_chatting_app.py"]
