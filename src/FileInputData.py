class FileInputData:
    def __init__(self, categories, text_input):
        self.categories = categories
        self.text_input = text_input
        self.entities = []

    # Getters
    def get_categories(self):
        return self.categories

    def get_text_input(self):
        return self.text_input

    # Setters
    def set_category(self, category):
        self.categories[category] = 1