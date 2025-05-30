FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN echo "🔥 requirements.txt 내용 확인" && cat requirements.txt
RUN echo "📦 pip install 시작" 
RUN pip install --no-cache-dir -r requirements.txt
RUN echo "📦 설치된 패키지 목록:" && pip list


COPY . .

CMD ["python", "app.py"]
