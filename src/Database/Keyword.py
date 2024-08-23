from sqlalchemy import func, select
from Database.DatabaseModels import KeywordModel

class Keyword():
    def __init__(self, database):
        """Initialize the Keyword instance with a session."""
        self.database = database

    def add(self, keyword_id, file_id, order):
        """Create a new keyword in the database."""
        new_keyword = KeywordModel(keyword_id=keyword_id, file_id=file_id, order=order)
        try:
            self.database.add(new_keyword)
            print(f"Keyword with ID {keyword_id} added successfully.")
        except Exception as e:
            print(f"Error adding keyword: {e}")

    def get_all(self): 
        """Get all keywords from the database."""
        keywords = []
        query = select(KeywordModel)

        results = self.database.query(query)

        for result in results:
            keyword = result[0]
            keywords.append(keyword)
        
        return keywords
    
    def get_by_keyword_id(self, keyword_id):
        """Get a keyword by its keyword_id."""
        query = select(KeywordModel).where(KeywordModel.keyword_id == keyword_id)

        result = self.database.query(query).first()
        return result
    
    def get_count_by_keyword_id(self, keyword_id):
        """Get the number of keywords associated with a given keyword_id."""
        query = select(func.count()).select_from(KeywordModel).filter(KeywordModel.keyword_id == keyword_id)
        result = self.database.query(query).scalar()

        return result
    
    def get_abstracts_by_keyword_id(self, keyword_id):
        """Get all abstracts associated with a given keyword_id."""
        from Database.DatabaseModels import FileModel
        abstracts = []
        query = (
            select(FileModel.abstract)
            .join(KeywordModel, FileModel.file_id == KeywordModel.file_id)
            .where(KeywordModel.keyword_id == keyword_id)
        )

        results = self.database.query(query)

        for result in results:
            abstract = result[0]
            print("-------------Abstract: ", abstract)
            abstracts.append(abstract)
        
        return abstracts