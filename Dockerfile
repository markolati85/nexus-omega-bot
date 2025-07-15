FROM python:3.12-slim

# Install system deps for TA-Lib with retry
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends build-essential libta-lib0 libta-lib-dev || (sleep 5 && apt-get update && apt-get install -y build-essential libta-lib0 libta-lib-dev) && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run app
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "nexus_omega_bot:app"]
