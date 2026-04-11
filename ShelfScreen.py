from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
import sqlite3


def run_query(sql):
    conn = sqlite3.connect('books_database.db')  # Stelle sicher, dass der korrekte Datenbankname angegeben ist
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

class BookItem(ButtonBehavior, BoxLayout):
    pass

class ShelfScreen(Screen):
    def load_books(self, category):
        # SQL-Abfrage basierend auf der Kategorie
        if category == 'read':
            sql = "SELECT id, cover, title, author FROM read_books"
        elif category == 'reading':
            sql = "SELECT id, cover, title, author FROM reading_books"
        else:
            sql = "SELECT id, cover, title, author FROM tbr_books"

        item_width = Window.width * 1
        item_height = Window.height * 0.8

        self.ids.books_grid.clear_widgets()
        results = run_query(sql)

        for book in results:
            # Jedes Item muss klickbar sein, damit der jeweils passende Screen geöffnet werden kann
            book_button = BookItem(
                orientation='horizontal',
                size_hint_y=None,
                height=item_height * 0.6,
                padding=10,
                spacing=10
            )
            # Cover-Bild links
            img = AsyncImage(
                source=book[1],
                size_hint=(None, None),
                size=(item_width * 0.5, item_height * 0.6),
                keep_ratio=True,
                allow_stretch=True
            )

            # Texte rechts
            text_layout = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(item_width * 0.5, item_height * 0.6),
            )

            title_label = Label(
                text=book[2],
                color=[0, 0, 0, 1],
                size_hint=(None, None),
                width = item_width * 0.5 - 20,
                font_size=40,
                halign='center',
                valign='bottom',
                text_size=(item_width * 0.5 - 20, item_height * 0.3),
                shorten=True,
                shorten_from='right',
                max_lines=2,
                size_hint_y=None,
                height=item_height * 0.25
            )
            by_label = Label(
                text="by",
                color=[0.3, 0.3, 0.3, 1],
                size_hint=(None, None),
                width = item_width * 0.5 - 20,
                font_size=32,
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=item_height * 0.1
            )
            author_label = Label(
                text=book[3],
                color=[0.3, 0.3, 0.3, 1],
                size_hint=(None, None),
                width = item_width * 0.5 - 20,
                font_size=32,
                halign='center',
                valign='top',
                text_size=(item_width * 0.5 - 20, item_height * 0.3),
                shorten=True,
                shorten_from='right',
                max_lines=2,
                size_hint_y=None,
                height=item_height * 0.25
            )

            text_layout.add_widget(title_label)
            text_layout.add_widget(by_label)
            text_layout.add_widget(author_label)


            book_button.add_widget(img)
            book_button.add_widget(text_layout)

            # Event binden
            book_button.bind(on_release=lambda btn, bk_id=book[0]: self.open_book_details(bk_id, category))
            self.ids.books_grid.add_widget(book_button)

    def open_book_details(self, book_id, category):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {category}_books WHERE id = ?", (book_id,))
        book_details = cursor.fetchone()
        conn.close()

        if book_details:
            if category == 'reading':
                screen_name = 'current_book'
            elif category == 'read':
                screen_name = 'read_book'
            else:
                screen_name = 'tbr_book'

            book_screen = self.manager.get_screen(screen_name)
            book_screen.load_book(book_id)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = screen_name

        app = App.get_running_app()
        app.last_screen = 'shelf'
