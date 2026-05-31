import sqlite3
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.pickers import MDDockedDatePicker

class ReadBookScreen(Screen):
    book_id = None
    date_dialog = None

    def show_date_picker(self, focus):
        if not focus:
            return
        # Wenn der Nutzer auf den Date Picker klickt, soll ein Fenster geöffnet werden, in dem das Datum ausgewählt werden kann
        self.ids.field.focus = False
        date_dialog = MDDockedDatePicker()
        date_dialog.width = min(dp(300), Window.width * 0.9)
        date_dialog.height = min(dp(400), Window.height * 0.6)
        date_dialog.pos = [
            self.ids.field.center_x - date_dialog.width / 2,
            self.ids.field.y + dp(75),
        ]
        # Event on ok und on cancel binden
        date_dialog.bind(on_ok=self.on_ok, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_ok(self, instance_date_picker):
        # Ausgewähltes Datum erhalten
        date_obj = instance_date_picker.get_date()[0]
        # Datum formatieren (zB zu "04/29/2025")
        formatted_date = date_obj.strftime('%m/%d/%Y')

        # Sicherstellen, dass book_id existiert
        if self.book_id:
            # Datum aktualisieren für das Buch mit der book_id (Tabelle der bereits gelesenen Bücher)
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE read_books SET finished_date=? WHERE id=?", (formatted_date, self.book_id))
            conn.commit()
            conn.close()

            # Widget aktualisieren
            self.ids.MD_text.text = f"Finished on: "
            self.ids.field.text = f"{formatted_date}"
            instance_date_picker.dismiss()
        else:
            print("No book ID available for saving date")

    def on_cancel(self, instance_date_picker):
        # Date Picker schließen
        instance_date_picker.dismiss()



    def load_book(self, book_id):
        # book_id erstellen
        self.book_id = book_id

        # Buch mit der book_id aus der Tabelle der bereits gelesenen Bücher abfragen
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM read_books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        conn.close()

        # Wenn Buch vorhanden ist, sollen alle Widgets mit den Informationen vom Buch ausgefüllt werden
        if book:
            self.ids.book_cover.source = book[1] or ''
            self.ids.book_title.text = book[2]
            self.ids.book_authors.text = book[3]
            self.ids.book_year.text = str(book[4])
            self.ids.book_genre.text = book[5]
            self.update_stars_display(book[6])
            self.ids.book_description.text = book[7] if book[7] else ''
            self.ids.book_page_count.text = str(book[8])
            self.ids.book_publisher.text = book[9]
            self.ids.book_maturity_rating.text = book[10]
            if book[11]:
                # Datum, an dem Nutzer das Buch fertig gelesen hat, eintragen, sofern vorhanden
                try:
                    month, day, year = map(int, book[11].split('/'))
                    self.ids.MD_text.text = f"Finished on: "
                    self.ids.field.text = f"{month:02d}/{day:02d}/{year}"
                # Sicherstellen, dass es nicht zum Absturz kommt bei einem falschen Format
                except ValueError:
                    print("Das Datum ist nicht im erwarteten Format YYYY-MM-DD.")
            else:
                    self.ids.MD_text.text = f"Finished on: "
                    self.ids.field.text = "Pick date"

        else:
            print("Book not found")


    def update_rating(self, rating):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:
            # png Datei für die Sterne abhängig vom rating auswählen (gefüllte und leere Sterne)
            self.ids['star1'].background_normal = 'filledstar.png' if rating >= 1 else 'emptystar.png'
            self.ids['star2'].background_normal = 'filledstar.png' if rating >= 2 else 'emptystar.png'
            self.ids['star3'].background_normal = 'filledstar.png' if rating >= 3 else 'emptystar.png'
            self.ids['star4'].background_normal = 'filledstar.png' if rating >= 4 else 'emptystar.png'
            self.ids['star5'].background_normal = 'filledstar.png' if rating >= 5 else 'emptystar.png'

            # Eintrag vom Buch mit book_id aktualisieren (neues rating einfügen)
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE read_books SET rating=? WHERE id=?", (rating, self.book_id))
            conn.commit()
            conn.close()

    def update_stars_display(self, rating):
        # Sterne Images basierend auf dem Rating updaten
        self.update_rating(rating)

    def delete_book(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:

            # Eintrag vom Buch mit book_id aus der Datenbank löschen
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM read_books WHERE id = ?", (self.book_id,))
            conn.commit()
            conn.close()
            print("Book deleted successfully")

            # Daraufhin muss Screen verlassen (zurück zum Shelf Screen und Richtung der Transition festlegen)
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('read')
        else:
            print("No book ID available for deletion")

    def move_to_reading(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:

            # Alle Informationen vom Buch mit book_id aus der Datenbank erhalten
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM read_books WHERE id=?", (self.book_id,))
            book = cursor.fetchone()

            # Alle Informationen vom Buch in die Tabelle der Bücher eintragen, die der Nutzer momentan liest
            if book:
                cursor.execute(
                    "INSERT INTO reading_books (cover, title, author, publication_year, genre, description, page_count, publisher, maturity_rating)"
                    " VALUES (:cover, :title, :author, :publication_year, :genre, :description, :page_count, :publisher, :maturity_rating)",
                    {
                        'cover': book[1],
                        'title': book[2],
                        'author': book[3],
                        'publication_year': book[4],
                        'genre': book[5],
                        'description': book[7],
                        'page_count': book[8],
                        'publisher': book[9],
                        'maturity_rating': book[10],
                    })

                # Anschließend muss das Buch selbst aus der Tabelle der bereits gelesenen Bücher gelöscht werden
                cursor.execute("DELETE FROM read_books WHERE id=?", (self.book_id,))
                conn.commit()
                print("Book has been moved to reading_books")

            conn.close()

            # Zurück zum Shelf Screen und Richtung der Transition festlegen
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('read')

    def move_to_tbr(self):
        # Sicherstellen, dass book_id existiert
        if self.book_id is not None:

            # Alle Informationen vom Buch mit book_id aus der Datenbank erhalten
            conn = sqlite3.connect('books_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM read_books WHERE id=?", (self.book_id,))
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
                        'description': book[7],
                        'page_count': book[8],
                        'publisher': book[9],
                        'maturity_rating': book[10]
                    })

                # Anschließend muss das Buch selbst aus der Tabelle der bereits gelesenen Bücher gelöscht werden
                cursor.execute("DELETE FROM read_books WHERE id=?", (self.book_id,))
                conn.commit()
                print("Book has been moved to tbr_books")

            conn.close()

            # Zurück zum Shelf Screen und Richtung der Transition festlegen
            self.manager.transition.direction = "right"
            self.manager.current = 'shelf'
            self.manager.get_screen('shelf').load_books('read')