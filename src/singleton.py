from src.db.db_manager import DBManager
from src.utils import get_db_settings, load_environment

load_environment()

db_manager = DBManager(
    db_settings=get_db_settings(),
)