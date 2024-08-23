from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import select
from Database.DatabaseModels import FileModel

Base = declarative_base()

class File():
    def __init__(self, database):
        """Initialize the File instance with a session."""
        self.database = database

    def get_all(self): 
        files = []
        """Get all keywords from the database."""
        query = select(FileModel)
        results = self.database.query(query)

        for result in results:
            file = result[0]
            files.append(file)

        return files

    def add(self, file_id, abstract, full_text):
        """Create a new file in the database."""
        new_file = FileModel(file_id=file_id, abstract=abstract, full_text=full_text)
        try:
            result = self.database.add(new_file)
            return result
        except Exception as e:
            self.session.rollback()
            print(f"Error adding file: {e}")
    