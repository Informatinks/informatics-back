class RequestError(Exception):
    """Base class for API exceptions."""

    def __init__(self, description='Ooops!'):
        super().__init__()
        self.description = description


class ServerError(RequestError):
    """Raised when connection error (or smth) happened."""

    def __init__(self):
        super().__init__('Error communicating with service')


class ClientError(RequestError):
    """Raised when status code is not OK."""

    def __init__(self, status_code):
        super().__init__('Response was not successful')
        self.status_code = status_code
