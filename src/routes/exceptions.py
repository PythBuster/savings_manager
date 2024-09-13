"""All fastAOI route exceptions are located here."""


class MissingSMTPSettingsError(Exception):
    """The MissingSMTPSettingsError class."""

    def __init__(self) -> None:
        """Initialize the MissingSMTPSettingsError instance."""

        self.message = "SMTP settings incomplete. Can't send email."
        super().__init__(self.message)
