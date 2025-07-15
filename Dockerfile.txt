Python 3.13.4 (v3.13.4:8a526ec7cbe, Jun  3 2025, 21:14:54) [Clang 16.0.0 (clang-1600.0.26.6)] on darwin
Enter "help" below or click "Help" above for more information.
>>> FROM python:3.12-slim
... 
... # Install system deps for TA-Lib
... RUN apt-get update && apt-get install -y build-essential libta-lib0 libta-lib-dev && rm -rf /var/lib/apt/lists/*
... 
... # Copy and install requirements
... COPY requirements.txt .
... RUN pip install --no-cache-dir -r requirements.txt
... 
... # Copy code
... COPY . .
... 
... # Run app (Render uses $PORT env var)
