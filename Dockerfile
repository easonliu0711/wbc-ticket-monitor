# 使用 Python 3.10 映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# --- 核心修正：安裝 Git 與 C++ 編譯工具集 ---
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
# ---------------------------------------

# 複製依賴清單
COPY requirements.txt .

# 執行安裝 (這次有編譯器了)
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 啟動指令
CMD ["python", "main.py"]