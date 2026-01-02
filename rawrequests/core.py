import json as _json
import ssl
import urllib.parse
import http.client

from .exceptions import HTTPError, Timeout, InvalidURL


_DEFAULT_UA = "rawrequests/0.1"


class Response:
    def __init__(self, status_code, headers, content, url):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.url = url

    @property
    def ok(self):
        return 200 <= self.status_code < 400

    @property
    def text(self):
        encoding = "utf-8"
        content_type = self.headers.get("content-type", "")
        if "charset=" in content_type:
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()
        try:
            return self.content.decode(encoding, errors="replace")
        except LookupError:
            return self.content.decode("utf-8", errors="replace")

    def json(self):
        return _json.loads(self.text)

    def raise_for_status(self):
        if not self.ok:
            message = f"{self.status_code} Error"
            raise HTTPError(message, response=self)


class Session:
    def __init__(self, headers=None, timeout=None, verify=True):
        self.headers = dict(headers or {})
        self.timeout = timeout
        self.verify = verify

    def request(self, method, url, **kwargs):
        return request(
            method,
            url,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify,
            **kwargs,
        )

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("HEAD", url, **kwargs)

    def options(self, url, **kwargs):
        return self.request("OPTIONS", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)


def request(
    method,
    url,
    params=None,
    data=None,
    json=None,
    headers=None,
    timeout=None,
    verify=True,
):
    method = method.upper()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise InvalidURL("Only https:// URLs are supported")
    if not parsed.hostname:
        raise InvalidURL("URL must include a hostname")

    query = parsed.query
    if params:
        extra_query = urllib.parse.urlencode(params, doseq=True)
        if query:
            query = f"{query}&{extra_query}"
        else:
            query = extra_query

    path = parsed.path or "/"
    if query:
        path = f"{path}?{query}"

    body = None
    request_headers = {
        "host": parsed.hostname,
        "user-agent": _DEFAULT_UA,
        "accept": "*/*",
    }
    if headers:
        request_headers.update(headers)

    if json is not None:
        body = _json.dumps(json).encode("utf-8")
        request_headers.setdefault("content-type", "application/json")
    elif data is not None:
        if isinstance(data, (bytes, bytearray)):
            body = data
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
            request_headers.setdefault(
                "content-type", "application/x-www-form-urlencoded"
            )

    if body is not None:
        request_headers.setdefault("content-length", str(len(body)))

    context = ssl.create_default_context()
    if not verify:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    conn = http.client.HTTPSConnection(
        parsed.hostname,
        parsed.port or 443,
        timeout=timeout,
        context=context,
    )
    try:
        conn.request(method, path, body=body, headers=request_headers)
        resp = conn.getresponse()
        content = resp.read()
    except TimeoutError as exc:
        raise Timeout("Request timed out") from exc
    finally:
        conn.close()

    headers_dict = {k.lower(): v for k, v in resp.getheaders()}
    return Response(resp.status, headers_dict, content, url)


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def post(url, **kwargs):
    return request("POST", url, **kwargs)


def put(url, **kwargs):
    return request("PUT", url, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)


def head(url, **kwargs):
    return request("HEAD", url, **kwargs)


def options(url, **kwargs):
    return request("OPTIONS", url, **kwargs)


def patch(url, **kwargs):
    return request("PATCH", url, **kwargs)
