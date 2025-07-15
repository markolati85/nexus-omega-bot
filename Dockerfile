FROM python:3.12-slim

# Install system deps for TA-Lib
RUN apt-get update && apt-get install -y build-essential libta-lib0 libta-lib-dev && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run app (Render uses $PORT env var)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "nexus_omega_bot:app"]
