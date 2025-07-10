import logging
import os
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)

@dataclass
class BotSettings:
    token: str
    admin_ids: list[int]
    
@dataclass 
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str

@dataclass
class LoggSettings: 
    level: str
    format: str
    
@dataclass 
class Config:
    bot: BotSettings
    db: DatabaseSettings
    log: LoggSettings 
    
def load_config() -> Config:
    env = Env()
    
    env.read_env(path)
    
    token = env("BOT_TOKEN")
        
    raw_ids = env.list("ADMIN_IDS", default=[])
    
    db = DatabaseSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD")
    )
    
    logg_settings = LoggSettings(
        level=env("LOG_LEVEL"),
        format=env("LOG_FORMAT")
    )
    
    return Config(
        bot=BotSettings(token=token, admin_ids=admin_ids),
        db=db,
        log=logg_settings
    )