FROM dnl01/ffmpeg-service:python-3.12.7-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--log-level", "debug", "--host", "0.0.0.0", "--port", "8000"]