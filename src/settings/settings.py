from dataclasses import dataclass


@dataclass
class POSTGRES_SETTINGS:
    host: str = "172.27.0.2"
    port: int = 5432
    db_name: str = "test_db"
    user: str = "root"
    password: str = "root"

postgres_settings = POSTGRES_SETTINGS()