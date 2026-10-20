FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc portaudio19-dev python3-pyaudio --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000
CMD ["python", "-m", "nexus_core.main"]
