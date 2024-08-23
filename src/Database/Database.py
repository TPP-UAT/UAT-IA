from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

class Database:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.session = get_db_session(self.engine)

    def init_db(self):
        Base.metadata.create_all(self.engine)

    def query(self, query, fetch='all'):
        return self.session.execute(query)

    def add(self, instance):
        try:
            self.session.add(instance)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error adding instance: {e}")


    def close(self):
        self.session.close()

    def get_engine(self):
        return self.engine
