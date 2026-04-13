import sqlite3
from kivy.uix.screenmanager import Screen

class BookDetailScreen(Screen):

    def load_book(self, book_details):
        # Widgets mit den übergebenen Informationen ausfüllen
        self.ids.book_cover.source = book_details['cover']
        self.ids.book_title.text = book_details['title']
        self.ids.book_authors.text = book_details['authors']
        self.ids.book_description.text = book_details['description']
        self.ids.book_year.text = book_details['publication_year']
        self.ids.book_genre.text = book_details['genre']
        self.ids.book_publisher.text = book_details['publisher']
        self.ids.book_page_count.text = book_details['pageCount']
        self.ids.book_maturity_rating.text = book_details['maturityRating']

    def add_to_read(self):
        # Buch soll nicht mehrfach eingetragen werden können
        # Prüfen, ob Eintrag mit identischen Titel und Autor bereits existiert (wenn ja, dann return)
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM read_books WHERE title = ? AND author = ?",(self.ids.book_title.text, self.ids.book_authors.text))
        exists = cursor.fetchone()
        if exists:
            return

        # Neuen Eintrag in der Tabelle der bereits gelesenen Bücher erstellen
        cursor.execute(
            "INSERT INTO read_books (cover, title, author, publication_year, genre, rating, description, page_count, publisher, maturity_rating, finished_date)"
            " VALUES (:cover, :title, :author, :publication_year, :genre, :rating, :description, :page_count, :publisher, :maturity_rating, :finished_date)",
            {
                'cover': self.ids.book_cover.source,
                'title': self.ids.book_title.text,
                'author': self.ids.book_authors.text,
                'publication_year': self.ids.book_year.text,
                'genre': self.ids.book_genre.text,
                'rating': 0,  # Rating zu Beginn nicht vorhanden
                'description': self.ids.book_description.text,
                'page_count': self.ids.book_page_count.text,
                'publisher': self.ids.book_publisher.text,
                'maturity_rating': self.ids.book_maturity_rating.text,
                'finished_date': ""  # Datum vorerst leer
            })

        conn.commit()
        conn.close()


    def add_to_reading(self):
        # Buch soll nicht mehrfach eingetragen werden können
        # Prüfen, ob Eintrag mit identischen Titel und Autor bereits existiert (wenn ja, dann return)
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM reading_books WHERE title = ? AND author = ?",(self.ids.book_title.text, self.ids.book_authors.text))
        exists = cursor.fetchone()
        if exists:
            return

        # Neuen Eintrag in der Tabelle der momentan Bücher erstellen
        cursor.execute(
            "INSERT INTO reading_books (cover, title, author, publication_year, genre, description, page_count, publisher, maturity_rating)"
            " VALUES (:cover, :title, :author, :publication_year, :genre, :description, :page_count, :publisher, :maturity_rating)",
            {
                'cover': self.ids.book_cover.source,
                'title': self.ids.book_title.text,
                'author': self.ids.book_authors.text,
                'publication_year': self.ids.book_year.text,
                'genre': self.ids.book_genre.text,
                'description': self.ids.book_description.text,
                'page_count': self.ids.book_page_count.text,
                'publisher': self.ids.book_publisher.text,
                'maturity_rating': self.ids.book_maturity_rating.text
            })

        conn.commit()
        conn.close()

    def add_to_future(self):
        # Buch soll nicht mehrfach eingetragen werden können
        # Prüfen, ob Eintrag mit identischen Titel und Autor bereits existiert (wenn ja, dann return)
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute( "SELECT id FROM tbr_books WHERE title = ? AND author = ?",(self.ids.book_title.text, self.ids.book_authors.text))
        exists = cursor.fetchone()
        if exists:
            return

        # Neuen Eintrag in der Tabelle der zukünftigen Bücher erstellen
        cursor.execute(
            "INSERT INTO tbr_books (cover, title, author, publication_year, genre, description, page_count, publisher, maturity_rating)"
            " VALUES (:cover, :title, :author, :publication_year, :genre, :description, :page_count, :publisher, :maturity_rating)",
            {
                'cover': self.ids.book_cover.source,
                'title': self.ids.book_title.text,
                'author': self.ids.book_authors.text,
                'publication_year': self.ids.book_year.text,
                'genre': self.ids.book_genre.text,
                'description': self.ids.book_description.text,
                'page_count': self.ids.book_page_count.text,
                'publisher': self.ids.book_publisher.text,
                'maturity_rating': self.ids.book_maturity_rating.text
            })

        conn.commit()
        conn.close()