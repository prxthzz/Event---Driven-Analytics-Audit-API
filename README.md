# Event---Driven-Analytics-Audit-API
Event - Driven Analytics & Audit API using FastAPI. 
The checkpoints included:
* API key–based authentication (per client)
* Rate limiting per API key
* Async event ingestion API (high-throughput)
* Event payload validation & idempotency (no duplicate events)
* Push events to a queue (Redis / RabbitMQ)
* Background workers to process & enrich events
* Store events in PostgreSQL (time-series friendly design)
* Bulk inserts & optimized indexing
* Analytics APIs:
– Event count by type
– Filter by time range
– Group by client / event type
* Audit logs for every API call
* Track processing latency & failed events
* Health check endpoint
* Proper error handling & HTTP status codes
I've also included the options for: 
* Sliding-window rate limiting
* Auto-delete old data (retention policy)
* WebSocket live metrics
* Docker Compose setup
