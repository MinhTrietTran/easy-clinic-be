# Chọn Python version giống local hoặc mới hơn
FROM python:3.11-slim

# Cài các gói hệ thống cần thiết (quan trọng cho psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục app
WORKDIR /app

# Copy file requirements.txt trước để build cache tốt hơn
COPY requirements.txt .

# Cài dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn Django vào container
COPY . .

# (Optional) Copy .env nếu dùng
# COPY .env .  

# Mặc định Django chạy trên cổng 5000
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:5000"]
