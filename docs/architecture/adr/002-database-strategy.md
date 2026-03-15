# Architecture Decision Record: Database Strategy

## Context and Problem Statement
The SkyMind system needs to handle highly relational data (airlines, routes, airports, flights), time-series data (telemetry, weather events), and perform complex analytics. A single monolithic database will not perform optimally.

## Considered Options
* Monolithic PostgreSQL
* MongoDB (NoSQL)
* Splitting into: PostgreSQL (Operational), ClickHouse (Analytics), InfluxDB (Time-series)

## Decision Outcome
* **PostgreSQL:** For all transactional and relational operational data (Flights, Airports, Users, Roles).
* **ClickHouse / BigQuery:** (Future Phase) For heavy analytics and delay trend aggregations.
* **Redis:** For caching real-time flight statuses, rate-limiting, and managing active WebSocket connections.

## Consequences
* High data integrity and referential safety for operational data.
* Redis ensures the frontend commands (like Map updates) are snappy and don't overwhelm the main DB.
* Requires managing multiple database systems in Docker for local development.
