import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    DATABASE_HOST = os.environ.get('DB_HOST')
    DATABASE_PORT = int(os.environ.get('DB_PORT', 3306))
    DATABASE_USER = os.environ.get('DB_USER')
    DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
    DATABASE_DB = os.environ.get('DB_NAME')
    DATABASE_SSL_CA = os.environ.get('DB_SSL_CA')
    
    # External APIs
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
    CURRENCY_API_KEY = os.environ.get('CURRENCY_API_KEY')
    
    # Unsplash API (Images)
    UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', '4hpNoiAbLWN18eXDRUKt8B9TG0kMsYXGRh8TbMXvOXE')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}