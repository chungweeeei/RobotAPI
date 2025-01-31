from dataclasses import dataclass


@dataclass
class POSTGRES_SETTINGS:
    host: str = "172.27.0.2"
    port: int = 5432
    db_name: str = "robot_db"
    user: str = "root"
    password: str = "root"

@dataclass
class LEARNING_POSTGRES_SETTINGS:
    host: str = "172.27.0.2"
    port: int = 5432
    db_name: str = "learning_db"
    user: str = "root"
    password: str = "root"

postgres_settings = POSTGRES_SETTINGS()
learning_postgres_settings = LEARNING_POSTGRES_SETTINGS()