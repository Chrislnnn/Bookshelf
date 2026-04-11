from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition
import requests
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

class BookItem(ButtonBehavior, BoxLayout):
    def __init__(self, book_data, **kwargs):
        super(BookItem, self).__init__(**kwargs)

        self.book_data = book_data
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = Window.height * 0.7
        self.width = Window.width

        item_height = Window.height * 0.8

        # Cover-Bild (sofern vorhanden)
        thumbnail_url = self.book_data['volumeInfo'].get('imageLinks', {}).get('thumbnail', '')
        img = AsyncImage(source=thumbnail_url,
                         size_hint_y=None,
                         height=item_height * 0.6,
                         keep_ratio=True,
                         allow_stretch=True) if thumbnail_url else Label(text='Kein Bild verfügbar',size_hint_y=None, height=item_height * 0.6)
        img.width = self.width
        self.add_widget(img)

        # Layout für Inhalte (die Angaben zum Buch)
        info_layout = BoxLayout(orientation='vertical',
                                padding=(10, 10),
                                size_hint_y=None,
                                height=self.height * 0.3)

        # book_data
        title = self.book_data['volumeInfo'].get('title', 'Kein Titel verfügbar')
        authors = ', '.join(self.book_data['volumeInfo'].get('authors', ['Unbekannt']))
        year = self.book_data['volumeInfo'].get('publishedDate', '').split('-')[0]
        genre = ', '.join(self.book_data['volumeInfo'].get('categories', ['Unbekannt']))

        # Text mit allen Angaben
        details_text = f"\n{title}\n{authors}\n{year}\n{genre}"
        details_label = Label(text=details_text,
                              color=(0, 0, 0, 1),
                              size_hint_y=None,
                              height=self.height * 0.3,
                              halign='center',
                              valign='top')
        details_label.bind(size=details_label.setter('text_size'))

        info_layout.add_widget(details_label)

        self.add_widget(info_layout)

    def on_release(self):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction='left')
        app.show_book_detail(self.book_data)





class SearchScreen(Screen):
    def search_books(self, query):
        # URL für die Google Books API Abfrage
        #url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key=AIzaSyDP_8rVvEgs1jcmIgXC2SHfDpsq-WNJfi4"
        response = requests.get(url)
        data = response.json()

        # UI aktualisieren
        Clock.schedule_once(lambda dt: self.update_books_grid(data), 0.1)

    def update_books_grid(self, data):
        self.ids.books_grid.clear_widgets()
        if 'items' in data:
            for item in data['items']:
                book_item = BookItem(item)
                self.ids.books_grid.add_widget(book_item)
        else:
            self.ids.books_grid.add_widget(Label(text="Keine Bücher gefunden.", size_hint_y=None, height=40))