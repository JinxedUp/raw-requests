# rawrequests

Tiny, requests-style HTTPS client built on the Python standard library.

## Quick start

```python
import rawrequests as rr

resp = rr.get("https://example.com", params={"q": "test"})
resp.raise_for_status()
print(resp.status_code)
print(resp.text)
```

## Features

- HTTPS only
- `get/post/put/delete/head/options/patch`
- `params`, `data`, `json`, `headers`, `timeout`, `verify`
- `Response.text`, `Response.json()`, `Response.raise_for_status()`
