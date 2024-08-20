"""The email sender exceptions are located here."""


class UnsupportedReceiverTypeError(Exception):
    """The UnsupportedReceiverType exception clas."""

    def __init__(self, receiver_type: str):
        self.receiver_type = receiver_type
        super().__init__(f'Unsupported receiver type "{receiver_type}"')
