from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from . import models


def init_db(app):
    global session
    engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'), convert_unicode=True)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    models.Base.metadata.create_all(bind=engine)
