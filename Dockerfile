# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Setup llama-cpp-python
RUN apk add --no-cache --virtual .build-deps build-base cmake ninja-build && \
    apk add --no-cache curl openblas-dev runit tzdata && \
    rm -rf /var/lib/apt/lists/* && \
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip \
        anyio \
        pytest \
        scikit-build \
        setuptools \
        fastapi \
        uvicorn \
        sse-starlette \
        pydantic-settings \
        starlette-context && \
    LLAMA_OPENBLAS=1 && \
    CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX=OFF -DLLAMA_AVX2=OFF -DLLAMA_F16C=OFF -DLLAMA_FMA=OFF" && \
    /venv/bin/pip install --no-cache-dir llama-cpp-python

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "/app/app.py"]
