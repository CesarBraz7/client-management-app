from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from data_manager import DataManager
import pandas as pd

class Labels:
    class ColoredHeaderLabel(Label):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            with self.canvas.before:
                Color(0, 0, 1, 0.2, mode='hsv')
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(pos=self.update_rect, size=self.update_rect)

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

    class ColoredRowLabel(Label):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            with self.canvas.before:
                Color(0, 0, 1, 0.5, mode='hsv')
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(pos=self.update_rect, size=self.update_rect)

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

class HomeScreen(Screen):
    data_manager = DataManager('tabela_clientes.csv')

    def on_enter(self):
        Clock.schedule_once(self.load_data, 0.1)

    def load_data(self, dt):
        print("Entering HomeScreen")
        try:
            data_table = self.ids['data_table']
            data_table.clear_widgets()
            print("Cleared widgets")
            
            header_box = self.ids['header_box']
            header_box.clear_widgets()
            headers = self.data_manager.df.columns.tolist() + ['Ações']
            for header in headers:
                header_box.add_widget(Labels.ColoredHeaderLabel(text=header, size_hint_y=None, height=100))

            rows = self.data_manager.df.iterrows()
            for index, row in rows:
                for cell in row:
                    data_table.add_widget(Labels.ColoredRowLabel(text=self.truncate_text(str(cell)), size_hint_y=None, height=60))

                layout = BoxLayout(orientation='horizontal')
                edit_button = Button(text='Editar')
                edit_button.bind(on_press=lambda x, idx=index: self.edit_data(idx))
                delete_button = Button(text='Excluir')
                delete_button.bind(on_press=lambda x, idx=index: self.delete_data(idx))
                layout.add_widget(edit_button)
                layout.add_widget(delete_button)
                data_table.add_widget(layout)

            print("Data table populated")
        except Exception as e:
            print(f"Error: {e}")

    def edit_data(self, index):
        self.manager.current = 'edit'
        edit_screen = self.manager.get_screen('edit')
        row_data = self.data_manager.df.iloc[index]
        edit_screen.index = index
        edit_screen.ids.edit_name.text = str(row_data['Nome'])
        edit_screen.ids.edit_cpf.text = str(row_data['CPF/CNPJ'])
        edit_screen.ids.edit_birthdate.text = str(row_data['Data de nascimento'])
        edit_screen.ids.edit_phone.text = str(row_data['Telefone'])
        edit_screen.ids.edit_process_number.text = str(row_data['Número do processo'])
        edit_screen.ids.edit_process_type.text = str(row_data['Tipo do processo'])
        edit_screen.ids.edit_description.text = str(row_data['Descrição'])

    def delete_data(self, index):
        self.data_manager.delete_data(index)
        self.load_data(0)

    def truncate_text(self, text, length=20):
        if len(text) > length:
            return text[:length] + '...'
        return text

class AddScreen(Screen):
    def add_data(self):
        new_data = {
            'Nome': [self.ids.name.text],
            'CPF/CNPJ': [str(self.ids.cpfcnpj.text)],
            'Data de nascimento': [self.ids.birthdate.text],
            'Telefone': [self.ids.phone.text],
            'Número do processo': [str(self.ids.process.text)],
            'Tipo do processo': [str(self.ids.process_type.text)],
            'Descrição': [str(self.ids.description.text)]
        }
        HomeScreen.data_manager.add_data(new_data)
        self.manager.current = 'home'
        self.manager.get_screen('home').load_data(0)
        print("Data added to CSV successfully")

class EditScreen(Screen):
    index = None

    def save_edit(self):
        edited_data = {
            'Nome': str(self.ids.edit_name.text),
            'Data de nascimento': str(self.ids.edit_birthdate.text),
            'CPF/CNPJ': str(self.ids.edit_cpf.text),
            'Telefone': str(self.ids.edit_phone.text),
            'Número do processo': str(self.ids.edit_process_number.text),
            'Tipo do processo': str(self.ids.edit_process_type.text),
            'Descrição': str(self.ids.edit_description.text)
        }
        HomeScreen.data_manager.edit_data(self.index, edited_data)
        self.manager.current = 'home'
        self.manager.get_screen('home').load_data(0)

class SearchScreen(Screen):
    def on_enter(self):
        df = pd.read_csv('tabela_clientes.csv', dtype=str)

        header_box = self.ids['header_box']
        header_box.clear_widgets()
        headers = df.columns.tolist() + ['Ações']
        for header in headers:
            header_box.add_widget(Labels.ColoredHeaderLabel(text=header, size_hint_y=None, height=100))

    def search_cpf(self):
        cpf = self.ids.search_cpjcnpj.text.strip()
        df = pd.read_csv('tabela_clientes.csv', dtype=str)
        result = df[df['CPF/CNPJ'].str.replace('.', '').replace('-', '') == cpf.replace('.', '').replace('-', '')]

        print(cpf)
        print(type(cpf))
        
        header_box = self.ids['header_box']
        header_box.clear_widgets()
        headers = df.columns.tolist() + ['Ações']
        for header in headers:
            header_box.add_widget(Labels.ColoredHeaderLabel(text=header, size_hint_y=None, height=100))

        content_box = self.ids['content_box']
        content_box.clear_widgets()
        rows = result.iterrows()
        for index, row in rows:
            for cell in row:
                content_box.add_widget(Labels.ColoredRowLabel(text=str(cell), size_hint_y=None, height=100))

            layout = BoxLayout(orientation='horizontal')
            edit_button = Button(text='Editar')
            edit_button.bind(on_press=lambda x, idx=index: self.manager.get_screen('home').edit_data(idx))
            delete_button = Button(text='Excluir')
            delete_button.bind(on_press=lambda x, idx=index: self.self.manager.get_screen('home').delete_data(idx))
            layout.add_widget(edit_button)
            layout.add_widget(delete_button)
            content_box.add_widget(layout)


class ScreenManagement(ScreenManager):
    pass

kv = '''
<ScreenManagement>:
    HomeScreen:
    AddScreen:
    EditScreen:
    SearchScreen:

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 40
        Label:
            text: 'Tabela de clientes'
            font_size: 40
            size: 70, 70
            size_hint_y: None
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                size_hint_y: None
                height: dp(100)
                id: header_box
            ScrollView:
                BoxLayout:
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    GridLayout:
                        id: data_table
                        cols: 8
                        size_hint_y: None
                        height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            Button:
                text: 'Adicionar clientes'
                on_press: app.root.current = 'add'
            Button:
                text: 'Procurar clientes'
                on_press: app.root.current = 'search'

<AddScreen>:
    name: 'add'
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 40
        Label:
            text: 'Adicionar cliente'
            font_size: 40
            size: 70, 70
            size_hint_y: None
        GridLayout:
            cols: 2
            spacing: dp(10)
            padding: dp(10)
            Label:
                text: 'Nome:'
            TextInput:
                id: name
                multiline: False
            Label:
                text: 'CPF/CNPJ:'
            TextInput:
                id: cpfcnpj
                multiline: False
            Label:
                text: 'Data de nascimento:'
            TextInput:
                id: birthdate
                multiline: False
            Label:
                text: 'Telefone:'
            TextInput:
                id: phone
                multiline: False
            Label:
                text: 'Número do processo:'
            TextInput:
                id: process
                multiline: False
            Label:
                text: 'Selecione o Tipo de Processo'
            Spinner:
                id: process_type
                values: ['Civil', 'Penal', 'Trabalhista', 'Previdenciário', 'Consumidor', 'Dpvat', 'Assessoria empresarial', 'Assessoria política']
            Label:
                text: 'Descrição:'
            TextInput:
                id: description
                multiline: False    
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            Button:
                text: 'Adicionar'
                on_press: root.add_data()
            Button:
                text: 'Voltar'
                on_press: app.root.current = 'home'

<EditScreen>:
    name: 'edit'
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 40
        Label:
            text: 'Editar dados do cliente'
            font_size: 40
            size: 70, 70
            size_hint_y: None
        GridLayout:
            cols: 2
            spacing: dp(10)
            padding: dp(10)
            Label:
                text: 'Nome:'
            TextInput:
                id: edit_name
                multiline: False
            Label:
                text: 'Data de Nascimento:'
            TextInput:
                id: edit_birthdate
                multiline: False
            Label:
                text: 'CPF/CNPJ:'
            TextInput:
                id: edit_cpf
                multiline: False
            Label:
                text: 'Telefone:'
            TextInput:
                id: edit_phone
                multiline: False
            Label:
                text: 'Número do Processo Judicial:'
            TextInput:
                id: edit_process_number
                multiline: False
            Label:
                text: 'Tipo de processo:'
            Spinner:
                id: edit_process_type
                values: ['Civil', 'Penal', 'Trabalhista', 'Previdenciário', 'Consumidor', 'Dpvat', 'Assessoria empresarial', 'Assessoria política']
            Label:
                text: 'Descrição:'
            TextInput:
                id: edit_description
                multiline: False
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            Button:
                text: 'Salvar Alterações'
                on_press: root.save_edit()
            Button:
                text: 'Voltar'
                on_press: app.root.current = 'home'
<SearchScreen>:
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 40
        Label:
            text: 'Procurar clientes'
            font_size: 40
            size: 70, 70
            size_hint_y: None
        GridLayout:
            size_hint_y: None
            height: dp(70)
            cols: 2
            spacing: dp(10)
            padding: dp(10)
            Label:
                text: 'Digite CPF ou CNPJ desejado:'
            TextInput:
                id: search_cpjcnpj
                multiline: False
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                size_hint_y: None
                height: dp(100)
                id: header_box
            ScrollView:
                BoxLayout:
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    GridLayout:
                        id: content_box
                        cols: 8
                        size_hint_y: None
                        height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            Button:
                text: 'Procurar'
                on_press: root.search_cpf()
            Button:
                text: 'Voltar'
                on_press: app.root.current = 'home'
'''

Builder.load_string(kv)

class Gerenciador(App):
    def build(self):
        return ScreenManagement()

Gerenciador().run()