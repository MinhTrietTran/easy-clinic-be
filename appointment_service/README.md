# Easy Clinic - Appointment Service

This is a microservice responsible for handling medical appointment logic in the Easy Clinic system.

## Technologies

* Django + Django REST Framework
* PostgreSQL
* Docker + Docker Compose
* Consul for service discovery

## Features

* Create and manage medical appointments
* Automatically assign available doctors based on department and time
* Update appointment status through defined workflows
* Reschedule existing appointments
* Retrieve patient and doctor information from the user service

## How to Run (Docker Compose)

### Folder Structure

```
project-root/
├── docker-compose.yml
├── appointment_service/
│   ├── Dockerfile
│   ├── manage.py
│   └── ...
```

### Steps

1. Make sure Docker and Docker Compose are installed
2. Run:

```bash
docker-compose up --build
```

The service will be available on port `5002` by default.

### API Documentation

Swagger UI is available at:

```
http://localhost:5002/swagger/
```

## Seed Mock Data (Optional)

To quickly test with sample data:

```bash
# If using service name from docker-compose
docker compose exec appointment_service python seed_mock_data.py

# Or using container name directly
docker exec -it appointment_service_app python seed_mock_data.py
```

Then try hitting this endpoint:

```
GET /api/appointments/
```

You should see 3 mock appointments returned.

## API Endpoints

| Method | Endpoint                       | Description                                                |
| ------ | ------------------------------ | ---------------------------------------------------------- |
| GET    | /appointments/                 | List all appointments                                      |
| POST   | /appointments/                 | Create a new appointment                                   |
| POST   | /appointments/auto-assign/     | Automatically assign a doctor based on department and time |
| GET    | /appointments/{id}/with-info/  | Get appointment with doctor and patient info               |
| POST   | /appointments/{id}/status/     | Update appointment status                                  |
| POST   | /appointments/{id}/reschedule/ | Reschedule an appointment                                  |
| GET    | /schedules/                    | List all available schedules                               |
| GET    | /shifts/                       | List all available shifts                                  |

## Integration with User Service

The appointment service connects with the user service to:

* Get doctor information by department
* Get details of doctor and patient by UUID

If the user service is unavailable, fallback mock data is used.

Ensure the following variable is set in the environment or settings:

```python
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service_app:5000")
```

## Postman Collection

A ready-to-use Postman collection file is provided:

```
appointment_postman_collection.json
```

You can import this file into Postman to test all API endpoints.

## Notes

* All business logic is implemented in the `services.py` file
* Views only handle HTTP routing and serialization
* This service can later integrate with the notification service (email/SMS)

## Team

* Backend Developer
* UI Design: Sang
* Infrastructure and Consul: Triết
* Business Analysis: Phát Trương, Phát Tiêu
