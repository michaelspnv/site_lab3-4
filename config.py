class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///auth.db'


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
