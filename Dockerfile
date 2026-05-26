FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    REBUILD_VECTOR="false"

WORKDIR /app

# 替换 apt 源为阿里云
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    wget \
    curl \
    && apt-get clean

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-chi-sim \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt，过滤掉 Windows 专用包，配置 pip 镜像，安装依赖
COPY requirements.txt .
RUN grep -v -E 'pywin32|pyreadline' requirements.txt > requirements_linux.txt && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir -r requirements_linux.txt

# 复制程序文件
COPY financial_assistant.py .
COPY assistant_cli.py .

# 创建必要目录
RUN mkdir -p /app/my_pdfs /app/my_chroma_db /app/processed

VOLUME ["/app/my_pdfs", "/app/my_chroma_db", "/app/processed"]

ENTRYPOINT ["python", "assistant_cli.py"]