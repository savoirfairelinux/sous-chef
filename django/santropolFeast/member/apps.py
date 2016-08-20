from django.apps import AppConfig

# This allows to use SQLAlchemy Core
import aldjemy.core as ac
# We need the session manager but we do not use the SQLAlchemy ORM itself
from sqlalchemy.orm import sessionmaker, scoped_session

# See http://docs.sqlalchemy.org/en/latest/orm/
#            contextual.html#using-thread-local-scope-with-web-applications
db_sa_session = scoped_session(sessionmaker(bind=ac.get_engine()))


def db_sa_table(model_class):
    # get database table for use with SQLAlchemy Core
    return ac.get_tables()[model_class._meta.db_table]


class MemberConfig(AppConfig):
    name = 'member'
