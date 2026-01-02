# raw requests example
import rawrequests as rr

resp = rr.get("https://example.com", params={"q": "test"})
print("status:", resp.status_code)
print("ok:", resp.ok)
print("content-type:", resp.headers.get("content-type"))
print("text snippet:", resp.text[:60])
resp.raise_for_status()

