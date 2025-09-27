# BookIt API

A production-ready REST API for a simple bookings platform called BookIt. Users can browse services, make bookings, and leave reviews. Admins manage users, services, and bookings.

## Architecture Decisions

### Database Choice: PostgreSQL

We chose PostgreSQL over MongoDB for the following reasons:

- **ACID Compliance**: Booking systems require strong consistency to prevent double-booking
- **Complex Queries**: Time-based conflict detection and filtering require sophisticated SQL
- **Relational Data**: User bookings, services, and reviews have clear relationships
- **Exclusion Constraints**: PostgreSQL's exclusion constraints provide database-level conflict prevention
- **Mature Ecosystem**: Better tooling for migrations, monitoring, and backup

## Features

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Service Management**: CRUD operations for services (admin only)
- **Booking System**: Conflict detection and resolution with database constraints
- **Review System**: One review per completed booking
- **RESTful API**: Auto-generated OpenAPI documentation
- **Database Migrations**: Alembic for schema management
- **Comprehensive Testing**: pytest with async support
- **Production Ready**: Structured logging, environment configuration, Docker support

## Project Structure

```
bookit/
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── db/             # Database configuration and migrations
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic layer
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic schemas
│   └── main.py         # FastAPI application
├── tests/              # Test suite
├── docker-compose.yml  # Docker configuration
├── pyproject.toml      # Project dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Poetry (for dependency management)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd BookIt
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Activate the virtual environment:

```bash
poetry shell
```

4. Copy environment variables:

```bash
cp .env.example .env
```

5. Update `.env` with your database credentials and other settings.

6. Start PostgreSQL and create the database:

```bash
# Using Docker
docker-compose up -d db

# Or manually
createdb bookit_db
```

7. Run database migrations:

```bash
alembic upgrade head
```

8. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Environment Variables

| Variable                       | Description             | Default     | Required |
| ------------------------------ | ----------------------- | ----------- | -------- |
| `APP_ENV`                      | Application environment | `dev`       | No       |
| `APP_DEBUG`                    | Debug mode              | `true`      | No       |
| `JWT_SECRET`                   | JWT signing secret      | `change-me` | **Yes**  |
| `JWT_ALG`                      | JWT algorithm           | `HS256`     | No       |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Access token expiry     | `15`        | No       |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token expiry    | `43200`     | No       |
| `BCRYPT_ROUNDS`                | Password hashing rounds | `12`        | No       |
| `DATABASE_URL`                 | Async database URL      | -           | **Yes**  |
| `SYNC_DATABASE_URL`            | Sync database URL       | -           | **Yes**  |
| `REDIS_URL`                    | Redis URL (optional)    | -           | No       |

### Using Docker

1. Start the services:

```bash
docker-compose up -d
```

2. Run migrations:

```bash
docker-compose exec app alembic upgrade head
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (stateless)

### Users

- `GET /me` - Get current user profile
- `PATCH /me` - Update current user profile

### Services

- `GET /services` - List services (with filters)
- `GET /services/{id}` - Get service details
- `POST /services` - Create service (admin only)
- `PATCH /services/{id}` - Update service (admin only)
- `DELETE /services/{id}` - Delete service (admin only)

### Bookings

- `POST /bookings` - Create booking
- `GET /bookings` - List bookings (user: own, admin: all)
- `GET /bookings/{id}` - Get booking details
- `PATCH /bookings/{id}` - Update booking (reschedule/cancel)
- `PATCH /bookings/{id}/status` - Update booking status (admin only)
- `DELETE /bookings/{id}` - Delete booking

### Reviews

- `POST /reviews` - Create review (completed bookings only)
- `GET /reviews/services/{service_id}` - Get service reviews
- `PATCH /reviews/{id}` - Update review (owner only)
- `DELETE /reviews/{id}` - Delete review (owner or admin)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Code Formatting

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .
```

### Type Checking

```bash
mypy app/
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show migration history
alembic history
```

## Testing

The test suite includes:

- **Authentication Tests**: Registration, login, token refresh, logout
- **Permission Tests**: Role-based access control, unauthorized access
- **Booking Conflict Tests**: Overlap detection, time validation
- **Integration Tests**: End-to-end API workflows

### Test Database Setup

Tests use a separate test database (`bookit_test`) to avoid affecting development data.

## Deployment

### Using Docker

1. Build and start all services:

```bash
docker-compose up -d
```

2. Run migrations:

```bash
docker-compose exec app alembic upgrade head
```

### Production Deployment

1. Set production environment variables
2. Use a production PostgreSQL instance
3. Configure proper JWT secrets
4. Set up reverse proxy (nginx)
5. Enable HTTPS
6. Configure monitoring and logging

## API Documentation

Once the application is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## License

This project is licensed under the MIT License.
