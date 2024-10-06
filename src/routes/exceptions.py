"""All fastAOI route exceptions are located here."""


class MissingSMTPSettingsError(Exception):
    """The MissingSMTPSettingsError class."""

    def __init__(self) -> None:
        """Initialize the MissingSMTPSettingsError instance."""

        self.message: str = "SMTP settings incomplete. Can't send email."
        super().__init__(self.message)


class BadUsernameOrPasswordError(Exception):
    """The BadUsernameOrPasswordError class."""

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name
        self.message: str = "Username or password incorrect."
        super().__init__(self.message)
