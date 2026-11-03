# QueryAccelerator

Experimental Query Accelerator: a DAX-style read-through cache in front of
SQLite or Postgres. `POST` a JSON query; results are served from an in-memory
TTL/LRU cache when possible, otherwise read from the database and cached.
`GET` is a health check.

### Sample Request Payload

```
'{
   "table":"products",
   "fields": ["name", "expiry_date"],
   "filters": [
      {"field":"name", "operator": "=", "value": "Bread"},
      {"field":"name", "operator": "=", "value": "Bread", "bind": "|"}],
   "order_by": "name",
   "order_dir":"asc"
}'
```

### Payload rules

- `table` (required), `fields`, `filters[].field` and `order_by` must be plain
  identifiers (`name` or `schema.name`). Omitting `fields` selects `*`.
- `operator` is one of `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `LIKE`, `NOT LIKE`.
- `value` must be a string, finite number or boolean. Values are always sent
  to the database as bound parameters, never inlined into the SQL.
- `bind` joins a filter to the previous one: `&` (AND, the default) or `|` (OR).
  Filters are joined in order **without parentheses**, so standard SQL
  precedence applies (`a | b & c` means `a OR (b AND c)`).
- `order_dir` is `asc` (default) or `desc`. Unknown keys are rejected.

### Responses

| Status | When |
| ------ | ---- |
| 200 | `{"data": [...rows]}` |
| 400 | Invalid JSON/payload, or the database rejected the query (unknown table/column, bad value) |
| 405 | Method other than GET/POST |
| 413 | Body larger than 64 KB |
| 500 | Unexpected server-side failure (e.g. database unavailable) |

Successful results, including empty ones, are cached for 24 hours.
