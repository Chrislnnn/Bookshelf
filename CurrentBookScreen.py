import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import Screen

class CurrentBookScreen(Screen):
    book_id = None

    def load_book(self, book_id):
        # book_id erstellen
        self.book_id = book_id

        # Buch mit der book_id aus der Tabelle der Bücher abfragen, die der Nutzer momentan liest
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reading_books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        conn.close()

        # Wenn Buch vorhanden ist, sollen alle Widgets mit den Informationen vom Buch ausgefüllt werden
        if book:
            self.ids.book_cover.source = book[1] or ''
            self.ids.book_title.text = book[2]
            self.ids.book_authors.text = book[3]
            self.ids.book_year.text = str(book[4])
            self.ids.book_genre.text = book[5]
            self.ids.book_description.text = book[6] if book[6] else ''
            self.ids.book_page_count.text = str(book[7])
            self.ids.book_publisher.text = book[8]
            self.ids.book_maturity_rating.text = book[9]

        else:
            print("Book not found")

    def delete_book(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:
            # Eintrag vom Buch mit book_id aus der Datenbank löschen
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reading_books WHERE id = ?", (self.book_id,))
            conn.commit()
            conn.close()
            print("Book deleted successfully")

            # Daraufhin muss Screen verlassen (zurück zum Shelf Screen und Richtung der Transition festlegen)
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('reading')
        else:
            print("No book ID available for deletion")

    def move_to_read(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:
            # Alle Informationen vom Buch mit book_id aus der Datenbank erhalten
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reading_books WHERE id=?", (self.book_id,))
            book = cursor.fetchone()

            # Alle Informationen vom Buch in die Tabelle der gelesenen Bücher eintragen
            if book:
                cursor.execute(
                    "INSERT INTO read_books (cover, title, author, publication_year, genre, rating, description, page_count, publisher, maturity_rating, finished_date)"
                    " VALUES (:cover, :title, :author, :publication_year, :genre, :rating, :description, :page_count, :publisher, :maturity_rating, :finished_date)",
                    {
                        'cover': book[1],
                        'title': book[2],
                        'author': book[3],
                        'publication_year': book[4],
                        'genre': book[5],
                        'rating': 0,  # Rating zu Beginn nicht vorhanden
                        'description': book[6],
                        'page_count': book[7],
                        'publisher': book[8],
                        'maturity_rating': book[9],
                        'finished_date': ''  # Datum vorerst leer
                    })

                # Anschließend muss das Buch selbst aus der Tabelle der momentanen Bücher gelöscht werden
                cursor.execute("DELETE FROM reading_books WHERE id=?", (self.book_id,))
                conn.commit()
                print("Book has been moved to read_books")
            conn.close()

            # Zurück zum Shelf Screen und Richtung der Transition festlegen
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('reading')

    def move_to_tbr(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:
            # Alle Informationen vom Buch mit book_id aus der Datenbank erhalten
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reading_books WHERE id=?", (self.book_id,))
            book = cursor.fetchone()

            # Alle Informationen vom Buch in die Tabelle der zukünftigen Bücher eintragen
            if book:
                cursor.execute(
                    "INSERT INTO tbr_books (cover, title, author, publication_year, genre, description, page_count, publisher, maturity_rating)"
                    " VALUES (:cover, :title, :author, :publication_year, :genre, :description, :page_count, :publisher, :maturity_rating)",
                    {
                        'cover': book[1],
                        'title': book[2],
                        'author': book[3],
                        'publication_year': book[4],
                        'genre': book[5],
                        'description': book[6],
                        'page_count': book[7],
                        'publisher': book[8],
                        'maturity_rating': book[9]
                    })

                # Anschließend muss das Buch selbst aus der Tabelle der momentanen Bücher gelöscht werden
                cursor.execute("DELETE FROM reading_books WHERE id=?", (self.book_id,))
                conn.commit()
                print("Book has been moved to tbr_books")
            conn.close()

            # Zurück zum Shelf Screen und Richtung der Transition festlegen
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('reading')