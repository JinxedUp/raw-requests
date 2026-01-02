class RawRequestsError(Exception):
    pass


class HTTPError(RawRequestsError):
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


class Timeout(RawRequestsError):
    pass


class InvalidURL(RawRequestsError):
    pass
