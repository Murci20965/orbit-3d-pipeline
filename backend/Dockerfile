# 1. Start with a lightweight Linux + Python 3.11 base
FROM python:3.11-slim

# 2. Install the heavy Linux graphics libraries Blender needs to run Headless
RUN apt-get update && apt-get install -y \
    libgl1 libxi6 libxrender1 libxxf86vm1 libxfixes3 \
    libxkbcommon0 libsm6 libglib2.0-0 \
    xz-utils wget \
    && rm -rf /var/lib/apt/lists/*

# 3. Download and Install the Official Blender 4.0 Engine
RUN wget https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz \
    && tar -xvf blender-4.0.2-linux-x64.tar.xz --strip-components=1 -C /usr/local/bin \
    && rm blender-4.0.2-linux-x64.tar.xz

# 4. Create the workspace inside the container
WORKDIR /app

# 5. Copy python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all the code (main.py, tripo.py, optimize.py) into the container
COPY . .

# 7. Expose port 7860 for the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]