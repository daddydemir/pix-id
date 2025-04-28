FROM python:3.10-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir --upgrade -r requirements.txt

# ---------------- runtime ------------------

FROM python:3.10-slim as runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas64-0 \
    libopenblas-dev \
    liblapack3 \
    libblas3 \
    libgtk-3-0 \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONPATH="/root/.local/lib/python3.10/site-packages:$PYTHONPATH" \
    LD_LIBRARY_PATH="/usr/local/lib:/usr/lib"

RUN mkdir -p app/static/uploads app/static/detected_faces

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]