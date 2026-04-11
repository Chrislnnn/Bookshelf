import datetime
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.metrics import dp
import sqlite3

# Custom Button mit abgerundeten Ecken und passender Farbe (wird im Homescreen verwendet)
class DetailButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(rgba=(0.13, 0.13, 0.13, 1))
            self.rect = RoundedRectangle(radius=[10])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class HomeScreen(Screen):
    read_count = StringProperty('0')
    reading_count = StringProperty('0')
    future_count = StringProperty('0')

    def on_pre_enter(self):
        self.update_book_counts()

        Clock.schedule_once(lambda dt: self.display_books(), 0.1)

    def display_books(self):
        books = self.get_books_from_db()
        self.ids.books_grid.clear_widgets()

        item_width = Window.width * 1
        item_height = Window.height * 0.75

        self.ids.books_grid.cols = len(books)
        self.ids.books_grid.spacing = 10

        for book in books:
            book_layout = BoxLayout(orientation='vertical',
                                    size_hint=(None, None),
                                    width=item_width,
                                    height=item_height,
                                    padding=[0, dp(10), 0, 0])
            cover_image = AsyncImage(source=book['cover'],
                                     size_hint=(None, None),
                                     size=(item_width, item_height * 0.6),
                                     keep_ratio=True,
                                     allow_stretch=True)
            title_label = Label(text=book['title'], color=[0, 0, 0, 1], size_hint=(None, None),
                                size=(item_width, item_height * 0.1),
                                font_size='18sp',
                                halign='center',
                                valign='middle',
                                max_lines=1,
                                shorten_from='right',
                                shorten=True,
                                text_size=(item_width * 0.95, item_height * 0.1))
            author_label = Label(text=book['author'], color=[0, 0, 0, 1], size_hint=(None, None),
                                 size=(item_width, item_height * 0.1),
                                 font_size='16sp',
                                 halign='center',
                                 valign='middle',
                                 max_lines=1,
                                 shorten_from='right',
                                 shorten=True,
                                 text_size=(item_width * 0.95, item_height * 0.1))

            button_wrapper = AnchorLayout(
                anchor_x='center', anchor_y='center',
                size_hint=(None, None),
                size=(item_width, item_height * 0.2)
            )
            detail_button = DetailButton(text='Details', size_hint=(None, None), size=(item_width*0.6, item_height * 0.1),
                                         color=[1, 1, 1, 1])
            detail_button.bind(on_press=lambda x, book_id=book['id']: self.open_book_details(book_id))
            button_wrapper.add_widget(detail_button)

            book_layout.add_widget(cover_image)
            book_layout.add_widget(title_label)
            book_layout.add_widget(author_label)
            book_layout.add_widget(button_wrapper)

            self.ids.books_grid.add_widget(book_layout)

    def update_book_counts(self):
        self.read_count = str(self.get_book_count('read_books'))
        self.reading_count = str(self.get_book_count('reading_books'))
        self.future_count = str(self.get_book_count('tbr_books'))

    def get_book_count(self, category):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {category}")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def get_books_from_db(self):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, cover, title, author FROM reading_books")
        books = [{'id': row[0], 'cover': row[1], 'title': row[2], 'author': row[3]} for row in cursor.fetchall()]
        conn.close()
        return books

    def open_book_details(self, book_id):
        book_screen = self.manager.get_screen('current_book')
        book_screen.load_book(book_id)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'current_book'

        app = App.get_running_app()
        app.last_screen = 'home'


