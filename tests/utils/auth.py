from datetime import datetime

from src.custom_types import UserRoleType


def create_jwt_access_token(
    user_name: str,
    role: UserRoleType,
    expires_at: datetime,
) -> str:
    return "test"