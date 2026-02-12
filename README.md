# Event-Driven Analytics & Audit API

A production-ready FastAPI application for high-throughput event ingestion, real-time analytics, and comprehensive audit logging.

## Features

### Core Functionality
- **API Key-based Authentication**: Per-client API key management with secure hashing
- **Sliding-Window Rate Limiting**: Configurable per-client rate limits
- **Async Event Ingestion**: High-throughput event processing with FastAPI async support
- **Event Validation & Idempotency**: Payload validation and duplicate prevention
- **Redis Queue System**: Event queuing for reliable processing
- **Background Workers**: Celery workers for async event processing
- **PostgreSQL Storage**: Time-series optimized database schema
- **Bulk Inserts**: Batch processing for improved performance
- **Optimized Indexing**: Strategic indexes for fast queries

### Analytics
- **Event Count by Type**: Group and aggregate events
- **Time Range Filtering**: Query events within date ranges
- **Client & Type Grouping**: Multi-dimensional analytics
- **Processing Metrics**: Latency statistics (P50, P95, P99)
- **Real-time Dashboard**: WebSocket live metrics

### Audit & Monitoring
- **API Call Audit Logs**: Complete audit trail
- **Request/Response Logging**: Full request context
- **Processing Latency Tracking**: Performance metrics
- **Failed Event Tracking**: Retry management and DLQ
- **Health Check Endpoint**: System status monitoring

### Advanced Features
- **Automatic Data Retention**: Configurable data cleanup
- **WebSocket Live Metrics**: Real-time event updates
- **Docker Compose Setup**: Complete containerized environment
- **Celery Beat Scheduler**: Periodic tasks and cleanup
- **Flower Monitoring**: Celery task visualization
- **Comprehensive Error Handling**: Proper HTTP status codes

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
├─────────────────┤
│ Authentication  │
│ Rate Limiting   │
│ Event Ingestion │
└────────┬────────┘
         │
    ┌────┴──────────┬──────────────┐
    │               │              │
┌───▼────┐    ┌────▼───┐    ┌────▼────┐
│PostgreSQL   │ Redis  │    │RabbitMQ │
└───┬────┘    └────┬───┘    └────┬────┘
    │              │             │
┌───▼──────────────▼─────────────▼────┐
│     Celery Workers/Beat Schedule    │
│  - Event Processing                 │
│  - Enrichment                       │
│  - Cleanup & Retention              │
│  - Retry Management                 │
└─────────────────────────────────────┘
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone repository
cd Task3

# Copy environment file
cp .env.example .env

# Build and start services
docker-compose up -d

# Create initial API key
docker-compose exec api python scripts/create_api_key.py

# View logs
docker-compose logs -f api
```

Access the API:
- **FastAPI Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Flower (Celery)**: http://localhost:5555

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Initialize database
python -c "from app.db.database import init_db; init_db()"

# Start Redis (required)
redis-server

# Start FastAPI (in terminal 1)
uvicorn main:app --reload

# Start Celery worker (in terminal 2)
celery -A app.workers.celery worker --loglevel=info

# Start Celery Beat (in terminal 3)
celery -A app.workers.celery beat --loglevel=info

# Create API key
python scripts/create_api_key.py
```

## API Usage

### 1. Create API Key

```bash
curl -X POST http://localhost:8000/api/v1/keys/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "my-client",
    "name": "My Client API Key",
    "rate_limit": 100
  }'
```

### 2. Ingest Single Event

```bash
curl -X POST http://localhost:8000/api/v1/events/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-12345",
    "event_type": "user_action",
    "payload": {
      "action": "login",
      "user_id": "user-123",
      "data": {"ip": "192.168.1.1"}
    }
  }'
```

### 3. Batch Event Ingestion

```bash
curl -X POST http://localhost:8000/api/v1/events/batch \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "event_id": "evt-001",
        "event_type": "user_action",
        "payload": {"action": "login", "user_id": "user-1"}
      },
      {
        "event_id": "evt-002",
        "event_type": "system_event",
        "payload": {"action": "backup", "status": "completed"}
      }
    ]
  }'
```

### 4. Get Event

```bash
curl -X GET http://localhost:8000/api/v1/events/EVENT_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 5. Analytics - Event Count by Type

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/events-by-type" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 6. Analytics - Processing Metrics

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/processing-metrics?days=7" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 7. Get Audit Logs

```bash
curl -X GET "http://localhost:8000/api/v1/audit/logs?limit=50" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 8. Health Check

```bash
curl -X GET http://localhost:8000/api/v1/health
```

### 9. WebSocket Live Metrics

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/metrics');

ws.onopen = (event) => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    client_id: 'my-client'
  }));
};

ws.onmessage = (event) => {
  console.log('Metrics:', JSON.parse(event.data));
};
```

## Management CLI

```bash
# Create API key
python scripts/manage.py create-key --client-id=my-app --name="My App" --rate-limit=100

# List all API keys
python scripts/manage.py list-keys

# Delete API key
python scripts/manage.py delete-key --client-id=my-app

# Toggle API key (enable/disable)
python scripts/manage.py toggle-key --client-id=my-app
```

## Database Schema

### Tables

**api_keys**
- Stores client credentials and rate limits
- Indexes: client_id, is_active

**events**
- Time-series optimized event storage
- Indexes:
  - (client_id, created_at)
  - (event_type, created_at)
  - (status, created_at)
  - (client_id, event_id) - unique for idempotency

**audit_logs**
- Complete API call audit trail
- Indexes:
  - (client_id, created_at)
  - (endpoint, created_at)

**failed_events**
- Dead letter queue for failed events
- Tracks retry attempts and scheduling

## Configuration

Edit `.env` file to customize:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_WINDOW_SECONDS=60

# Event Processing
EVENT_BATCH_SIZE=100
EVENT_RETENTION_DAYS=90

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Performance Tuning

### Database Optimization
- Indexes on frequently queried columns
- Partitioning by date for large tables
- Connection pooling for multi-worker environments

### Redis Optimization
- Sliding window rate limiting in Redis
- Event queue in Redis for low-latency access
- Cache layer for frequently accessed data

### Worker Optimization
- Configurable batch sizes
- Parallel task processing
- Automatic retry with exponential backoff

## Monitoring

### Flower Dashboard
Access Celery task monitoring at http://localhost:5555

### Metrics to Monitor
- Queue size and processing rate
- Event processing latency
- Failed event count
- API response times
- Database connection pool

## Rate Limiting

Implements sliding-window rate limiting using Redis sorted sets:
- Per-client rate limits
- Requests tracked with timestamps
- Automatic window cleanup
- Configurable per API key

## Data Retention

Automatic cleanup tasks:
- **Daily at 2 AM**: Delete events older than retention period
- **Daily at 3 AM**: Delete audit logs older than retention period
- **Every 10 minutes**: Retry failed events

Customize retention period in `.env`:
```env
EVENT_RETENTION_DAYS=90
```

## Production Deployment

### Docker Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### Kubernetes Deployment
See `k8s/` directory for Kubernetes manifests.

### Environment Variables for Production
```env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@db-host:5432/db
REDIS_URL=redis://redis-host:6379/0
```

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_events.py::test_ingest_event -v
```

## Troubleshooting

### Events stuck in queue
```bash
# Check queue status
curl http://localhost:8000/api/v1/analytics/queue-status

# View failed events
curl http://localhost:8000/api/v1/audit/logs?endpoint=failed
```

### Database connection issues
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres
```

### Worker not processing events
```bash
# Check Celery worker
docker-compose exec celery_worker celery -A app.workers.celery inspect active

# View worker logs
docker-compose logs celery_worker
```

## License

MIT

## Support

For issues and questions, please create an issue in the repository.
