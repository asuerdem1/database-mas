import configparser
from sqlalchemy import create_engine
import sqlalchemy as db
config = configparser.ConfigParser()
config.read('config.txt')
# db.create_engine('postgresql+psycopg2://postgres:pw@localhost/eu')
engine = db.create_engine(config.get('database', 'sqlcon'))