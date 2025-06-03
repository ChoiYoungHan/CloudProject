FROM python:3.10-bullseye

WORKDIR /app

# requirements.txt 먼저 복사 (캐시 활용)
COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# 나머지 앱 파일 복사
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
