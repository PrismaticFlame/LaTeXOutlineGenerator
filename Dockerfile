FROM python:3.15-rc-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY outline.py .
COPY examples/ ./examples/

RUN mkdir -p input output

# Download the model on build (optional - can be done at runtime instead)
# Uncomment the next line to pre-download the model (increases image size by ~2GB)
# RUN ollama serve & sleep 5 && ollama pull llama3.2:3b && pkill ollama

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entryopint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

