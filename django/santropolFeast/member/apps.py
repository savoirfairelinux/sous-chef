from django.apps import AppConfig

# This allows to use SQLAlchemy for queries
import aldjemy.core as ac
from sqlalchemy.orm import sessionmaker, scoped_session

# See http://docs.sqlalchemy.org/en/latest/orm/
#            contextual.html#using-thread-local-scope-with-web-applications
db_session = scoped_session(sessionmaker(bind=ac.get_engine()))


class MemberConfig(AppConfig):
    name = 'member'
