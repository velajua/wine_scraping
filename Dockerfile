# Start from a base image
FROM python:3.9-slim-buster

# Set environment variables
ENV CHROME_BIN="/usr/bin/google-chrome-stable"
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get update && \
    apt-get install -y wget gnupg2 && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set display variable
ENV DISPLAY=:99

# Start Chrome and execute the command
CMD ["sh", "-c", "\
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & \
    && sleep 3 \
    && google-chrome-stable --no-sandbox --disable-dev-shm-usage --disable-gpu --headless --remote-debugging-port=9222 http://localhost:8080 & \
    && sleep 3 \
    && streamlit run --server.port 8501 wine_analysis.py"]
