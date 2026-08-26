FROM python:3.12-slim
WORKDIR /screen
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libgtk-3-0 \
    xvfb x11vnc novnc fluxbox \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium
COPY app.py backboard_llm.py start.sh .
RUN chmod +x start.sh && mkdir -p /screenshots
EXPOSE 8100 6080
CMD ["./start.sh"]
