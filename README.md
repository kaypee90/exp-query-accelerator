# Query Accelerator

An experimental, asynchronous query service that puts a read-through cache in
front of SQLite or PostgreSQL. Submit a small JSON query over HTTP and receive
database rows as JSON. Repeated, equivalent queries are served from an
in-memory TTL/LRU cache instead of hitting the database.

> **Status:** Experimental. The service is intentionally small and focused on
> read-only query acceleration.

## Highlights

- ASGI application powered by Uvicorn
- SQLite and PostgreSQL backends
- Parameterized values and identifier validation
- 24-hour cache TTL with LRU eviction after 10,000 entries
- Canonical cache keys, so equivalent JSON payloads reuse results
- Health-check endpoint and graceful database shutdown
- JSON serialization for common database values, including dates, decimals,
  UUIDs, and binary data

## Requirements

- Python 3.10+
- A SQLite database file or a running PostgreSQL database
- Docker, only if you want to run the PostgreSQL end-to-end test

## Quick start

```bash
git clone https://github.com/kaypee90/exp-query-accelerator.git
cd exp-query-accelerator

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure SQLite with a `.env` file:

```dotenv
DB_TYPE=sqlite
SQLITE_DB=/absolute/path/to/app.db
```

Start the service:

```bash
make run
```

The server listens on `http://127.0.0.1:8000`.

Check service health:

```bash
curl http://127.0.0.1:8000/
```

```json
{"status": "Healthy"}
```

## Querying

Send a `POST` request with a JSON payload:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H 'content-type: application/json' \
  -d '{
    "table": "products",
    "fields": ["name", "expiry_date"],
    "filters": [
      {"field": "name", "operator": "=", "value": "Bread"}
    ],
    "order_by": "name",
    "order_dir": "asc"
  }'
```

Successful responses contain rows as arrays in database column order:

```json
{
  "data": [
    ["Bread", "2026-12-31"]
  ]
}
```

If `fields` is omitted, the query selects all columns. Filters are joined in
the order provided. Use `&` for `AND` (the default) or `|` for `OR`; filters
are not parenthesized, so normal SQL precedence applies.

### Request fields

| Field | Required | Description |
| --- | --- | --- |
| `table` | Yes | Table name, or `schema.table` |
| `fields` | No | List of columns; omitted means all columns |
| `filters` | No | List of `{field, operator, value, bind}` objects |
| `order_by` | No | Column used for ordering |
| `order_dir` | No | `asc` (default) or `desc` |

Supported operators are `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `LIKE`, and
`NOT LIKE`. Table and column names must be plain identifiers. Values are sent
as bound database parameters and are never interpolated into SQL.

### HTTP responses

| Status | Meaning |
| --- | --- |
| `200` | Query succeeded |
| `400` | Invalid JSON, invalid payload, or database rejected the query |
| `405` | Method is not `GET` or `POST` |
| `413` | Request body exceeds 64 KiB |
| `500` | Unexpected server-side failure |

## PostgreSQL

Set `DB_TYPE=postgres` and provide the connection settings in `.env`:

```dotenv
DB_TYPE=postgres
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=secret
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

The PostgreSQL backend uses an asynchronous connection pool with up to four
connections.

## Development

The Makefile provides the common local workflows:

```bash
make test       # Run the SQLite-focused test suite
make test_pg_e2e # Start PostgreSQL in Docker and run the PostgreSQL tests
make test_all   # Run both suites
make startpg    # Start a local PostgreSQL container on port 5400
make stoppg     # Stop the local PostgreSQL container
```

To run the application with Uvicorn's reload mode:

```bash
make run
```

## Project layout

```text
src/
├── app.py          # ASGI entry point and HTTP method routing
├── handlers.py     # Request parsing and JSON responses
├── dispatcher.py   # Validation, caching, and database dispatch
├── cache.py        # TTL/LRU in-memory cache
├── validator.py    # Query payload validation
└── db/             # SQLite, PostgreSQL, and query-building code
tests/              # Unit, integration, and ASGI-level tests
```

## License

This project is distributed under the license in [LICENSE](LICENSE).
