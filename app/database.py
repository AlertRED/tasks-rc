from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'postgresql://merov:2511@localhost:5432/test_db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionMaker = sessionmaker(bind=engine)
