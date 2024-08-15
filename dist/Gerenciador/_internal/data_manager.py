import pandas as pd

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path, dtype=str)
            print("CSV Loaded")
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['Nome', 'CPF/CNPJ', 'Data de nascimento', 'Telefone', 'Número do processo', 'Tipo do processo', 'Descrição'])
            self.save_data()
            print("New CSV created")

    def save_data(self):
        self.df.to_csv(self.file_path, index=False)

    def add_data(self, new_data):
        self.df = pd.concat([self.df, pd.DataFrame(new_data)], ignore_index=True)
        self.save_data()

    def edit_data(self, index, edited_data):
        self.df.loc[index] = edited_data
        self.save_data()

    def delete_data(self, index):
        self.df = self.df.drop(index)
        self.save_data()