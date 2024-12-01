from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

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
            return False


    def close(self):
        self.session.close()

    def get_engine(self):
        return self.engine
    
    def get_all_files(self):
        try:
            query = text("SELECT file_id, full_text FROM public.files;")
            result = self.session.execute(query).fetchall()
            # Convertir los resultados a una lista de diccionarios
            files = [{"file_id": row.file_id, "full_text": row.full_text} for row in result]
            return files
        except Exception as e:
            print(f"Error fetching files: {e}")
            return []

    def update_file_summary(self, file_id, summary):
            try:
                query = text("UPDATE public.files SET summarized_text = :summary WHERE file_id = :file_id;")
                self.session.execute(query, {"summary": summary, "file_id": file_id})
                self.session.commit()
                print(f"Updated summarized_text for file_id {file_id}")
            except Exception as e:
                self.session.rollback()
                print(f"Error updating summary for file_id {file_id}: {e}")