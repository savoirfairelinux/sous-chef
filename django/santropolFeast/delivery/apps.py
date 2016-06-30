from django.apps import AppConfig

# This allows to use SQLAlchemy for queries
import aldjemy.core as ac
from sqlalchemy.orm import sessionmaker
engine = ac.get_engine()
Session = sessionmaker(bind=engine)


class DeliveryConfig(AppConfig):
    name = 'delivery'
    Session = Session
