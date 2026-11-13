class AuthError(Exception):
    """An authentication (401) or authorization (403) failure.
    `error` is a dict with a stable machine-readable `code` and a human
    `description`, so every endpoint reports failures the same way.
    """

    def __init__(self, error, status_code):
        super().__init__(error.get("description"))
        self.error = error
        self.status_code = status_code