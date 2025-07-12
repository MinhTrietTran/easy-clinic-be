# Easy Clinic Backend

Hệ thống backend microservices cho ứng dụng Easy Clinic, sử dụng Docker Compose để quản lý các service: User Service, Appointment Service, Medical Record Service, Notification Service, Resolver Service, Consul và PostgreSQL.

## 🏗️ Kiến trúc hệ thống

```
Easy Clinic Backend (Microservices)
├── User Service (Django) - Port 5001
├── Appointment Service (Django) - Port 5002  
├── Medical Record Service (Django) - Port 5003
├── Notification Service (Django) - Port 5004
├── Resolver Service (Flask) - Port 7070
├── Consul (Service Discovery) - Port 8500
├── RabbitMQ (Message Queue) - Port 5672, 15672
└── PostgreSQL Databases (Ports 5432-5435)
```

## 📁 Cấu trúc thư mục

```
easy-clinic-be/
├── docker-compose.yml
├── user_service/                 # Django REST API
│   ├── users/
│   │   ├── models/
│   │   │   ├── user.py          # Custom User Model
│   │   │   ├── doctor.py        # Doctor Profile
│   │   │   └── patient.py       # Patient Profile
│   │   └── v1/
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── serializers.py
│   │       └── services.py
│   ├── consul_register.py       # Consul Registration
│   ├── requirements.txt
│   └── Dockerfile
├── appointment_service/          # Django REST API
│   ├── appointment/
│   │   ├── models.py           # Appointment, Schedule, Shift
│   │   └── v1/
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── serializers.py
│   │       └── services.py
│   ├── consul_register.py
│   ├── requirements.txt
│   └── Dockerfile
├── medical_record_service/       # Django REST API
│   ├── medical_records/
│   │   ├── models.py           # Medical Records, Tests, Prescriptions
│   │   └── v1/
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── serializers.py
│   │       └── services.py
│   ├── consul_register.py
│   ├── requirements.txt
│   └── Dockerfile
├── notification_service/         # Django + Celery
│   ├── notifications/
│   │   ├── models.py           # Notification Models
│   │   ├── tasks.py            # Celery Tasks
│   │   └── v1/
│   ├── consul_register.py
│   ├── requirements.txt
│   └── Dockerfile
├── resolver_service/            # Flask API
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## 🚀 Các service chính

### User Service (Port 5001)
- **Framework**: Django 5.x + Django REST Framework
- **Database**: PostgreSQL (Port 5432)
- **Chức năng**: 
  - Quản lý người dùng (Authentication/Authorization)
  - Profile bác sĩ và bệnh nhân
  - JWT Token authentication
- **Endpoints**: `/api/v1/users/`, `/api/v1/doctors/`, `/api/v1/patients/`

### Appointment Service (Port 5002)
- **Framework**: Django REST Framework
- **Database**: PostgreSQL (Port 5433)
- **Chức năng**:
  - Quản lý lịch hẹn khám bệnh
  - Lịch làm việc của bác sĩ
  - Thống kê appointments
- **Endpoints**: `/api/v1/appointments/`, `/api/v1/schedules/`, `/api/v1/statistics/`

### Medical Record Service (Port 5003)
- **Framework**: Django REST Framework  
- **Database**: PostgreSQL (Port 5434)
- **Chức năng**:
  - Quản lý hồ sơ bệnh án
  - Kết quả xét nghiệm
  - Đơn thuốc điện tử
- **Endpoints**: `/api/v1/records/`, `/api/v1/tests/`, `/api/v1/prescriptions/`

### Notification Service (Port 5004)
- **Framework**: Django + Celery + RabbitMQ
- **Database**: PostgreSQL (Port 5435)
- **Chức năng**:
  - Gửi thông báo real-time
  - Email notifications
  - Push notifications
- **Endpoints**: `/api/v1/notifications/`

### Resolver Service (Port 7070)
- **Framework**: Flask
- **Chức năng**: Service discovery cho local development
- **Endpoint**: `/resolve?service=user_service`

### Consul (Port 8500)
- **Chức năng**: Service discovery và health checking
- **UI**: http://localhost:8500

### RabbitMQ (Ports 5672, 15672)
- **Chức năng**: Message queue cho Celery tasks
- **Management UI**: http://localhost:15672 (guest/guest)

## 🔧 Khởi động hệ thống

### Yêu cầu
- Docker & Docker Compose
- Python 3.11+ (cho local development)

### Khởi động tất cả services
```bash
# Clone repository
git clone <repository-url>
cd easy-clinic-be

# Khởi động tất cả services
docker compose up --build -d

# Hoặc khởi động từng service
docker compose up user_service -d
docker compose up appointment_service -d
docker compose up medical_record_service -d
docker compose up notification_service -d
```

### Kiểm tra services đang chạy
```bash
# Xem status tất cả containers
docker compose ps

# Xem logs của service cụ thể
docker compose logs user_service
docker compose logs appointment_service -f
```

## 🌐 Service Endpoints

| Service | External Port | Internal Port | Health Check | API Documentation |
|---------|---------------|---------------|--------------|-------------------|
| User Service | 5001 | 5000 | `/api/v1/health/` | `/api/v1/users/` |
| Appointment Service | 5002 | 5000 | `/api/v1/health/` | `/api/v1/appointments/` |
| Medical Record Service | 5003 | 5000 | `/api/v1/health/` | `/api/v1/records/` |
| Notification Service | 5004 | 5000 | `/api/v1/health/` | `/api/v1/notifications/` |
| Resolver Service | 7070 | 7000 | `/health` | `/resolve?service=<name>` |
| Consul UI | 8500 | 8500 | `/ui/` | Service Discovery |
| RabbitMQ Management | 15672 | 15672 | `/` | Queue Management |

## 📊 Database Ports

| Database | External Port | Service |
|----------|---------------|---------|
| user_service_db | 5432 | User Service |
| appointment_service_db | 5433 | Appointment Service |
| medical_record_service_db | 5434 | Medical Record Service |
| notification_service_db | 5435 | Notification Service |

## 🛠️ Quản lý Database

### Migrate databases
```bash
# User Service
docker compose exec user_service_app python manage.py migrate

# Appointment Service
docker compose exec appointment_service_app python manage.py migrate

# Medical Record Service
docker compose exec medical_record_service_app python manage.py migrate

# Notification Service
docker compose exec notification_service_app python manage.py migrate
```

### Tạo tài khoản admin
```bash
# User Service (chính)
docker compose exec user_service_app python manage.py createsuperuser

# Các service khác
docker compose exec appointment_service_app python manage.py createsuperuser
```

### Connect trực tiếp vào database
```bash
# User Service Database
docker exec -it user_service_db psql -U user_service_user -d user_service_db

# Appointment Service Database
docker exec -it appointment_service_db psql -U appointment_user -d appointment_service_db

# Medical Record Service Database
docker exec -it medical_record_service_db psql -U medical_record_user -d medical_record_db
```

## 🔐 Authentication & Authorization

### JWT Token Flow
1. **Login**: `POST /api/v1/login/` → Nhận access_token & refresh_token
2. **Access APIs**: Header `Authorization: Bearer <access_token>`
3. **Refresh Token**: `POST /api/v1/token/refresh/` với refresh_token

### User Roles
- **Patient**: Bệnh nhân
- **Doctor**: Bác sĩ
- **Admin**: Quản trị viên

## 📡 API Examples

### User Service APIs
```bash
# Đăng ký
curl -X POST "http://localhost:5001/api/v1/register/" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123", "role": "patient"}'

# Đăng nhập
curl -X POST "http://localhost:5001/api/v1/login/" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'

# Lấy thông tin user
curl -X GET "http://localhost:5001/api/v1/me/" \
     -H "Authorization: Bearer <access_token>"
```

### Appointment Service APIs
```bash
# Tạo appointment
curl -X POST "http://localhost:5002/api/v1/appointments/" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": "123", "doctor_id": "456", "time_start": "2024-01-15T10:00:00Z"}'

# Lấy appointments của doctor
curl -X GET "http://localhost:5002/api/v1/doctors/456/appointments/" \
     -H "Authorization: Bearer <access_token>"
```

### Medical Record Service APIs
```bash
# Tạo medical record
curl -X POST "http://localhost:5003/api/v1/records/" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"patient_id": "123", "doctor_id": "456", "diagnosis": "Headache"}'

# Lấy lịch sử khám bệnh
curl -X GET "http://localhost:5003/api/v1/patients/123/history/" \
     -H "Authorization: Bearer <access_token>"
```

## 🔍 Monitoring & Debug

### Health Checks
```bash
# Check tất cả services
curl http://localhost:5001/api/v1/health/  # User Service
curl http://localhost:5002/api/v1/health/  # Appointment Service  
curl http://localhost:5003/api/v1/health/  # Medical Record Service
curl http://localhost:5004/api/v1/health/  # Notification Service
curl http://localhost:7070/health          # Resolver Service
```

### Consul Service Discovery
```bash
# Xem services đã đăng ký
curl http://localhost:8500/v1/catalog/services

# Xem health của services
curl http://localhost:8500/v1/health/checks
```

### Logs Monitoring
```bash
# Real-time logs tất cả services
docker compose logs -f

# Logs của service cụ thể
docker compose logs -f user_service
docker compose logs -f appointment_service
docker compose logs -f medical_record_service
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**
```bash
# Kiểm tra ports đang sử dụng
docker compose ps
lsof -i :5001

# Stop conflicting containers
docker compose down --remove-orphans
```

2. **Database connection issues**
```bash
# Check database containers
docker compose ps | grep _db

# Restart database
docker compose restart user_service_db
```

3. **Service không đăng ký vào Consul**
```bash
# Check consul logs
docker compose logs consul

# Manual registration
docker compose exec user_service_app python consul_register.py
```

### Reset toàn bộ hệ thống
```bash
# Dừng và xóa tất cả
docker compose down --volumes --remove-orphans

# Rebuild và start lại
docker compose up --build -d
```

## 📚 Development

### Local Development Setup
```bash
# Install Python dependencies
cd user_service && pip install -r requirements.txt
cd ../appointment_service && pip install -r requirements.txt
# ... for other services

# Run service locally (với database trong Docker)
python manage.py runserver 5001
```

### Database Schema Updates
```bash
# Tạo migrations
docker compose exec user_service_app python manage.py makemigrations

# Apply migrations
docker compose exec user_service_app python manage.py migrate

# Create superuser
docker compose exec user_service_app python manage.py createsuperuser
```

## 📋 TODO / Roadmap

- [ ] API Gateway với rate limiting
- [ ] Distributed tracing với Jaeger
- [ ] Monitoring với Prometheus + Grafana
- [ ] CI/CD pipeline
- [ ] Integration tests
- [ ] API documentation với Swagger
- [ ] File upload service
- [ ] Payment service integration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**🏥 Easy Clinic Backend - Microservices Architecture for Healthcare Management System**






