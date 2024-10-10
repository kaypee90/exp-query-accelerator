# QueryAccelerator

Experimental Query Accelerator

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
