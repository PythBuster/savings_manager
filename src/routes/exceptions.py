class MissingSMTPSettingsError(Exception):
    """The MissingSMTPSettingsError class."""

    def __init__(self):
        self.message = "SMTP settings incomplete. Can't send email."
        super().__init__(self.message)
