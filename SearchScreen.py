from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import requests

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
        thumbnail_url = self.book_data['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'noImage.png')
        img = AsyncImage(source=thumbnail_url,
                         size_hint_y=None,
                         height=item_height * 0.6,
                         keep_ratio=True,
                         allow_stretch=True)
        img.width = self.width
        self.add_widget(img)

        # Layout für Inhalte (die Angaben zum Buch)
        info_layout = BoxLayout(orientation='vertical',
                                padding=(10, 10),
                                size_hint_y=None,
                                height=self.height * 0.3)

        # Titel, Author, Veröffentlichungsdatum und Genre aus book_data erhalten
        title = self.book_data['volumeInfo'].get('title', 'Title missing')
        authors = ', '.join(self.book_data['volumeInfo'].get('authors', ['Author unknown']))
        year = self.book_data['volumeInfo'].get('publishedDate', '').split('-')[0]
        genre = ', '.join(self.book_data['volumeInfo'].get('categories', ['Genre unknown']))

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

    # Öffne Book Details Screen (+übergebe Informationen vom Buch), wenn auf das BookItem geklickt wird
    def on_release(self):
        app = App.get_running_app()
        app.sm.transition = SlideTransition(direction='left')

        # Zugriff auf den BookDetailScreen über den ScreenManager
        book_detail_screen = app.sm.get_screen('book_detail')
        book_detail_screen.ids.book_cover.source = self.book_data['volumeInfo'].get('imageLinks', {}).get('thumbnail','noImage.png')
        book_detail_screen.ids.book_title.text = self.book_data['volumeInfo'].get('title', 'Title missing')
        book_detail_screen.ids.book_authors.text = ', '.join(self.book_data['volumeInfo'].get('authors', ['Author unknown']))
        published_date = self.book_data['volumeInfo'].get('publishedDate', '')
        year = published_date.split('-')[0] if published_date else 'Unknown'
        book_detail_screen.ids.book_year.text = year
        book_detail_screen.ids.book_genre.text = ', '.join(self.book_data['volumeInfo'].get('categories', ['Genre unknown']))
        book_detail_screen.ids.book_description.text = self.book_data['volumeInfo'].get('description','No description available')
        book_detail_screen.ids.book_publisher.text = self.book_data['volumeInfo'].get('publishedDate', '').split('-')[0]
        page_count = self.book_data['volumeInfo'].get('pageCount', 0)
        book_detail_screen.ids.book_page_count.text = str(page_count)
        book_detail_screen.ids.book_maturity_rating.text = self.book_data['volumeInfo'].get('maturityRating', '')

        # Book Detail Screen öffnen
        app.sm.current = 'book_detail'

        # Transitionsrichtung setzen
        app.sm.transition = SlideTransition(direction='right')
        app.sm.current = 'book_detail'
        # Transitionsrichtung zurücksetzen auf Standardwert (links)
        app.sm.transition = SlideTransition(direction='left')


class SearchScreen(Screen):
    def search_books(self, query):
        # URL für die Google Books API Abfrage
        # url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        # mit eigenem API Key:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key=AIzaSyDP_8rVvEgs1jcmIgXC2SHfDpsq-WNJfi4"
        response = requests.get(url)
        # Antwort liegt im JSON Format vor
        data = response.json()

        # UI aktualisieren
        Clock.schedule_once(lambda dt: self.update_books_grid(data), 0.1)

    def update_books_grid(self, data):
        # Zuerst Grid Layout leeren
        self.ids.books_grid.clear_widgets()
        # Für jeden Eintrag ein BookItem (Button) erstellen und diesen zum Grid Layout hinzufügen
        if 'items' in data:
            for item in data['items']:
                book_item = BookItem(item)
                self.ids.books_grid.add_widget(book_item)
        else:
            self.ids.books_grid.add_widget(Label(text="Could not find any books", size_hint_y=None, height=40))