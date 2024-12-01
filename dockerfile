# Use a lightweight Python image as the base
FROM python:3.12-slim

# Set environment variables to reduce output size and improve performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies, including CMake, curl, Rust, and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    cmake \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

# Set the path for Rust (this is needed after Rustup installation)
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements file first (to take advantage of Docker layer caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501
EXPOSE 8888

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run FastAPI and Streamlit
CMD ["bash", "-c", "uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py"]
