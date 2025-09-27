# BookIt API

A production-ready REST API for a simple bookings platform called BookIt. Users can browse services, make bookings, and leave reviews. Admins manage users, services, and bookings.

## Architecture Decisions

### Database Choice: PostgreSQL vs MongoDB

**I chose PostgreSQL over MongoDB** for the following critical reasons:

#### Why PostgreSQL?

1. **ACID Compliance & Data Integrity**

   - Booking systems require strong consistency to prevent double-booking scenarios
   - ACID transactions ensure that booking operations are atomic and consistent
   - Critical for financial and time-sensitive operations

2. **Advanced Query Capabilities**

   - Complex time-based conflict detection using SQL window functions and range queries
   - Sophisticated filtering and aggregation for reporting and analytics
   - Full-text search capabilities for service discovery

3. **Relational Data Model**

   - Clear relationships between users, services, bookings, and reviews
   - Foreign key constraints ensure referential integrity
   - Normalized data structure reduces redundancy and maintains consistency

4. **Exclusion Constraints**

   - PostgreSQL's `tstzrange` exclusion constraints prevent overlapping bookings at the database level
   - Provides database-enforced conflict prevention without application-level race conditions
   - Critical for preventing double-booking in concurrent scenarios

5. **Mature Ecosystem & Tooling**

   - Excellent migration tools (Alembic integration)
   - Comprehensive monitoring and backup solutions
   - Strong community support and documentation
   - Proven performance at scale

6. **JSON Support When Needed**
   - PostgreSQL's native JSON/JSONB support provides flexibility for semi-structured data
   - Can store complex service metadata or user preferences as JSON when appropriate
   - Best of both worlds: relational structure with document flexibility

#### Why Not MongoDB?

- **Consistency Concerns**: Eventual consistency model unsuitable for booking conflicts
- **Complex Queries**: Time-based range queries and joins are more complex in MongoDB
- **Data Integrity**: No foreign key constraints or exclusion constraints
- **Transaction Limitations**: Limited multi-document transaction support (though improved in recent versions)
- **Schema Evolution**: While flexible, can lead to data inconsistency without careful management

### Database Schema & Constraints

Our PostgreSQL schema leverages several advanced features that would be difficult or impossible to implement with MongoDB:

**Key Constraints:**

- **Exclusion Constraints**: Prevent overlapping bookings using `tstzrange` and `EXCLUDE` clauses
- **Foreign Key Constraints**: Ensure referential integrity between users, services, and bookings
- **Unique Constraints**: Prevent duplicate reviews per booking
- **Check Constraints**: Validate booking times and status transitions

**Advanced Features:**

- **Time Zone Support**: Native `timestamptz` for global booking systems
- **Range Types**: Efficient storage and querying of time ranges
- **Indexes**: Optimized for time-based queries and user lookups
- **Triggers**: Automatic timestamp updates and data validation

**Example Exclusion Constraint:**

```sql
-- Prevents overlapping bookings for the same service
ALTER TABLE bookings ADD CONSTRAINT no_overlapping_bookings
EXCLUDE USING gist (
  service_id WITH =,
  tstzrange(start_time, end_time) WITH &&
);
```

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

- **Python 3.11+** (3.12 supported)
- **PostgreSQL 15+** (or use Docker)
- **Poetry** (for dependency management)
- **Docker & Docker Compose** (optional, for containerized setup)

### Quick Start with Docker (Recommended)

1. **Clone the repository:**

```bash
git clone <repository-url>
cd BookIt
```

2. **Start all services:**

```bash
docker-compose up -d
```

3. **Run database migrations:**

```bash
docker-compose exec app alembic upgrade head
```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Manual Setup (Development)

1. **Clone and navigate:**

```bash
git clone <repository-url>
cd BookIt
```

2. **Install Poetry** (if not already installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies:**

```bash
poetry install
```

4. **Activate virtual environment:**

```bash
poetry shell
```

5. **Set up environment variables:**

```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Set up PostgreSQL database:**

**Option A: Using Docker (Recommended)**

```bash
# Start only the database
docker-compose up -d db

# Wait for database to be ready
docker-compose logs -f db
```

**Option B: Local PostgreSQL installation**

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database and user
createdb bookit_db
psql bookit_db -c "CREATE USER bookit_user WITH PASSWORD 'bookit_password';"
psql bookit_db -c "GRANT ALL PRIVILEGES ON DATABASE bookit_db TO bookit_user;"
```

7. **Run database migrations:**

```bash
alembic upgrade head
```

8. **Start the development server:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

9. **Verify installation:**
   - Visit http://localhost:8000/docs
   - Test the health endpoint: http://localhost:8000/health

### Environment Configuration

Copy `.env.example` to `.env` and configure the following variables:

| Variable                       | Description             | Default | Required |
| ------------------------------ | ----------------------- | ------- | -------- |
| `APP_ENV`                      | Application environment | `dev`   | No       |
| `APP_DEBUG`                    | Debug mode              | `true`  | No       |
| `JWT_SECRET`                   | JWT signing secret      | -       | **Yes**  |
| `JWT_ALG`                      | JWT algorithm           | `HS256` | No       |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Access token expiry     | `15`    | No       |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token expiry    | `43200` | No       |
| `BCRYPT_ROUNDS`                | Password hashing rounds | `12`    | No       |
| `DATABASE_URL`                 | Async database URL      | -       | **Yes**  |
| `SYNC_DATABASE_URL`            | Sync database URL       | -       | **Yes**  |
| `REDIS_URL`                    | Redis URL (optional)    | -       | No       |

**Important Security Notes:**

- Change `JWT_SECRET` to a strong, random string in production
- Use different database credentials for production
- Never commit `.env` files to version control

### Troubleshooting

**Common Issues:**

1. **Database Connection Errors:**

   ```bash
   # Check if PostgreSQL is running
   docker-compose ps

   # Check database logs
   docker-compose logs db

   # Test connection manually
   psql -h localhost -U bookit_user -d bookit_db
   ```

2. **Migration Issues:**

   ```bash
   # Reset migrations (development only)
   docker-compose exec app alembic downgrade base
   docker-compose exec app alembic upgrade head
   ```

3. **Port Conflicts:**

   ```bash
   # Check what's using port 8000
   lsof -i :8000

   # Use different port
   uvicorn app.main:app --reload --port 8001
   ```

4. **Permission Issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Docker Deployment

The application includes a complete Docker setup with PostgreSQL and Redis:

**Services:**

- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL 15 database (port 5432)
- **redis**: Redis cache (port 6379)

**Quick Start:**

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

**Production Deployment:**

```bash
# Build production image
docker build -t bookit-api .

# Run with production environment
docker run -d \
  --name bookit-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e JWT_SECRET=your-production-secret \
  bookit-api
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

**Environment Setup:**

1. Set production environment variables
2. Use a production PostgreSQL instance (AWS RDS, Google Cloud SQL, etc.)
3. Configure proper JWT secrets (use strong, random strings)
4. Set up reverse proxy (nginx) with SSL termination
5. Enable HTTPS with valid certificates
6. Configure monitoring and logging (Prometheus, Grafana, ELK stack)

**Database Considerations:**

- Use connection pooling (PgBouncer)
- Set up read replicas for scaling
- Configure automated backups
- Monitor query performance
- Set up database monitoring

**Security Checklist:**

- [ ] Strong JWT secrets (32+ characters)
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection headers

## API Documentation

Once the application is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## License

This project is licensed under the MIT License.
