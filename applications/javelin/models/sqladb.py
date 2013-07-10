from sqlalchemy import create_engine, MetaData, Column, Integer, Text, Table
from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgres://postgres:p0stmast3r!@localhost/javelin', convert_unicode=True)
metadata = MetaData(bind=engine)
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def todict(proxy):
	return dict(zip(proxy.keys(), proxy))
		
def tolist(proxy):
	return [row.todict() for row in proxy]

RowProxy.todict = todict
ResultProxy.tolist = tolist

Model = declarative_base()
Model.query = db.query_property()
Model.metadata.create_all(bind=engine)