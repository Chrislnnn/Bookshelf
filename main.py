from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
import sqlite3
from kivymd.app import MDApp
from kivy.lang import Builder

from BookDetailScreen import BookDetailScreen
from CurrentBookScreen import CurrentBookScreen
from ReadBookScreen import ReadBookScreen
from HomeScreen import HomeScreen
from SearchScreen import SearchScreen
from ShelfScreen import ShelfScreen
from StatisticsScreen import StatisticsScreen
from ToBeReadScreen import ToBeReadScreen
from kivymd.utils.set_bars_colors import set_bars_colors

class WindowManager(ScreenManager):
    pass

class main(MDApp):
    last_screen = None

    def build(self):
        # KV-Datei laden
        self.initialize_book_database()
        Builder.load_file('windows.kv')

        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ShelfScreen(name='shelf'))
        self.sm.add_widget(SearchScreen(name='search'))
        self.sm.add_widget(StatisticsScreen(name='statistics'))
        self.sm.add_widget(BookDetailScreen(name='book_detail'))
        self.sm.add_widget(ReadBookScreen(name='read_book'))
        self.sm.add_widget(CurrentBookScreen(name='current_book'))
        self.sm.add_widget(ToBeReadScreen(name='tbr_book'))
        Window.clearcolor = (1, 1, 1, 1)

        set_bars_colors((1, 0.898, 0.816, 1), (1, 0.898, 0.816, 1), "Light")

        return self.sm



    def show_book_detail(self, book_data):
        # Zugriff auf den BookDetailScreen über den ScreenManager
        book_detail_screen = self.sm.get_screen('book_detail')
        book_detail_screen.ids.book_cover.source = book_data['volumeInfo'].get('imageLinks', {}).get('thumbnail', '')
        book_detail_screen.ids.book_title.text = book_data['volumeInfo'].get('title', 'Title missing')
        book_detail_screen.ids.book_authors.text = ', '.join(book_data['volumeInfo'].get('authors', ['Author unknown']))
        published_date = book_data['volumeInfo'].get('publishedDate', '')
        year = published_date.split('-')[0] if published_date else 'Unknown'
        book_detail_screen.ids.book_year.text = year
        book_detail_screen.ids.book_genre.text = ', '.join(book_data['volumeInfo'].get('categories', ['Unknown']))
        book_detail_screen.ids.book_description.text = book_data['volumeInfo'].get('description', 'No description available')

        book_detail_screen.ids.book_publisher.text = book_data['volumeInfo'].get('publishedDate', '').split('-')[0]
        page_count = book_data['volumeInfo'].get('pageCount', 0)
        book_detail_screen.ids.book_page_count.text = str(page_count)
        book_detail_screen.ids.book_maturity_rating.text = book_data['volumeInfo'].get('maturityRating', '')

        self.sm.current = 'book_detail'

        # Transitionsrichtung setzen
        self.sm.transition = SlideTransition(direction='right')
        self.sm.current = 'book_detail'
        # Transitionsrichtung zurücksetzen auf Standardwert (links)
        self.sm.transition = SlideTransition(direction='left')

    def initialize_book_database(self):
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()

        # Tabelle für bereits gelesene Bücher erstellen
        cursor.execute("""CREATE TABLE IF NOT EXISTS read_books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cover TEXT,
                            title TEXT,
                            author TEXT,
                            publication_year INTEGER,
                            genre TEXT,
                            rating INTEGER,
                            description TEXT,
                            page_count INTEGER,
                            publisher TEXT,
                            maturity_rating TEXT,
                            finished_date TEXT)""")

        # Tabelle für Bücher, die momentan gelesen werden
        cursor.execute("""CREATE TABLE IF NOT EXISTS reading_books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cover TEXT,
                            title TEXT,
                            author TEXT,
                            publication_year INTEGER,
                            genre TEXT,
                            description TEXT,
                            page_count INTEGER,
                            publisher TEXT,
                            maturity_rating TEXT)""")

        # Tabelle für Bücher, die in der Zukunft gelesen werden sollen
        cursor.execute("""CREATE TABLE IF NOT EXISTS tbr_books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cover TEXT,
                            title TEXT,
                            author TEXT,
                            publication_year INTEGER,
                            genre TEXT,
                            description TEXT,
                            page_count INTEGER,
                            publisher TEXT,
                            maturity_rating TEXT)""")

        # Änderungen speichern und Verbindung schließen
        conn.commit()
        conn.close()

    # Methode zum Löschen der Daten in der Datenbank
    def reset_database(self):
        # Eine Datenbank muss erstellt werden
        conn = sqlite3.connect('books_database.db')

        # Ein Cursor wird benötigt
        cursor = conn.cursor()

        # Einträge der Datenbank löschen
        cursor.execute("DELETE FROM read_books")
        cursor.execute("DELETE FROM reading_books")
        cursor.execute("DELETE FROM tbr_books")

        # Zähler zurücksetzen
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='read_books'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='reading_books'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tbr_books'")

        # Änderungen speichern
        conn.commit()
        # Schließen der Verbindung
        conn.close()



if __name__ == '__main__':
    main().run()