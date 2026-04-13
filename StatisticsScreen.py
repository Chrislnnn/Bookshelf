import sqlite3
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
import matplotlib.pyplot as plt
import io

class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super(StatisticsScreen, self).__init__(**kwargs)

    # Methode, die die Anzahl an Büchern in den 3 unterschiedlichen Tabellen zurückgibt
    # Gibt jeweils 0 aus, wenn keine Einträge in jeweiligen Tabelle vorhanden sind
    def get_books_count(self):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM read_books")
        read_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM reading_books")
        reading_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tbr_books")
        future_count = cursor.fetchone()[0]
        conn.close()
        return [('Read', read_count), ('Reading', reading_count), ('Future', future_count)]

    # Methode, die die Anzahl an gelesenen Bücher pro Monat zurückgibt (diese müssen ein finished date besitzen)
    def get_books_per_month(self):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT substr(finished_date, 1, 2) AS month, COUNT(*)
            FROM read_books 
            WHERE finished_date IS NOT NULL AND finished_date != ''
            GROUP BY month
            ORDER BY month
        """)
        books_per_month = cursor.fetchall()
        conn.close()

        # Wenn keine Einträge mit finished date vorhanden sind, werden alle Monate auf 0 gesetzt
        if not books_per_month:
            books_per_month = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0)]

        return books_per_month

    # Methode, die die Anzahl an gelesenen Seiten pro Monat zurückgibt (diese müssen ein finished date besitzen)
    def get_pages_per_month(self):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT substr(finished_date, 1, 2) AS month, SUM(page_count)
            FROM read_books
            WHERE finished_date IS NOT NULL AND finished_date != '' AND page_count IS NOT NULL
            GROUP BY month
            ORDER BY month
        """)
        pages_per_month = cursor.fetchall()
        conn.close()

        # Wenn keine Einträge mit finished date vorhanden sind, werden alle Monate auf 0 gesetzt
        if not pages_per_month:
            pages_per_month = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0)]

        print("Daten aus der Datenbank: ", pages_per_month)  # Drucken der Daten zum Debuggen
        return pages_per_month

    # Methode, die die Anzahl an Büchern pro Rating (0-5 Sterne zurückgibt)
    def get_ratings_distribution(self):
        conn = sqlite3.connect('books_database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rating, COUNT(*)
            FROM read_books
            WHERE rating IS NOT NULL
            GROUP BY rating
            ORDER BY rating
        """)
        data = cursor.fetchall()
        conn.close()

        # Wenn noch keine Bewertungen in der Tabelle vorliegen, werden alle auf 0 gesetzt
        if not data:
            data = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]

        return data

    def on_enter(self):
        # Erzeugen und Hinzufügen von Plots nur, wenn der Screen tatsächlich geöffnet wird
        self.generate_plot()

    def generate_plot(self):
        # clear widget, damit vorherige Plots entfernt werden
        self.ids.graphs.clear_widgets()

        self.plot_height = Window.height * 0.7

        # Erzeugen von Images (Widgets) für die unterschiedlichen Plots
        self.book_count_image = Image(size_hint=(1, None), height=self.plot_height, keep_ratio=True, allow_stretch=True)
        self.books_read_per_month = Image(size_hint=(1, None), height=self.plot_height, keep_ratio=True, allow_stretch=True)
        self.pages_read_per_month = Image(size_hint=(1, None), height=self.plot_height, keep_ratio=True, allow_stretch=True)
        self.rating_distribution = Image(size_hint=(1, None), height=self.plot_height, keep_ratio=True, allow_stretch=True)

        # Erstellung der Diagramme
        self.books_count_plot()
        self.books_per_month_plot()
        self.pages_per_month_plot()
        self.rating_distribution_plot()

        # Image (Diagramm) zu graphs (GridLayout im ScrollView) hinzufügen
        self.ids.graphs.add_widget(self.book_count_image)
        # Divider (Linie) zwischen den Diagrammen hinzufügen
        divider1 = Widget(size_hint_y=None, height=1)
        with divider1.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            divider1.rect = Rectangle(pos=divider1.pos, size=divider1.size)
            divider1.bind(pos=lambda *a: setattr(divider1.rect, 'pos', divider1.pos),
                          size=lambda *a: setattr(divider1.rect, 'size', divider1.size))
        self.ids.graphs.add_widget(divider1)

        # Image (Diagramm) zu graphs (GridLayout im ScrollView) hinzufügen
        self.ids.graphs.add_widget(self.books_read_per_month)
        # Divider (Linie) zwischen den Diagrammen hinzufügen
        divider2 = Widget(size_hint_y=None, height=1)
        with divider2.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            divider2.rect = Rectangle(pos=divider2.pos, size=divider2.size)
            divider2.bind(pos=lambda *a: setattr(divider2.rect, 'pos', divider2.pos),
                          size=lambda *a: setattr(divider2.rect, 'size', divider2.size))
        self.ids.graphs.add_widget(divider2)

        # Image (Diagramm) zu graphs (GridLayout im ScrollView) hinzufügen
        self.ids.graphs.add_widget(self.pages_read_per_month)
        # Divider (Linie) zwischen den Diagrammen hinzufügen
        divider3 = Widget(size_hint_y=None, height=1)
        with divider3.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            divider3.rect = Rectangle(pos=divider3.pos, size=divider3.size)
            divider3.bind(pos=lambda *a: setattr(divider3.rect, 'pos', divider3.pos),
                          size=lambda *a: setattr(divider3.rect, 'size', divider3.size))
        self.ids.graphs.add_widget(divider3)

        # Image (Diagramm) zu graphs (GridLayout im ScrollView) hinzufügen
        self.ids.graphs.add_widget(self.rating_distribution)

    # Methode für die Darstellung des mit Matplotlib erstellten Diagramms in einem Kivy Image-Widget
    def save_plot_to_image(self, fig, image_widget):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        from kivy.core.image import Image as CoreImage
        image = CoreImage(buf, ext='png')

        image_widget.texture = image.texture
        width, height = image.texture.size
        image_widget.texture_size = (width, height)
        image_widget.height = height

        buf.close()
        plt.close(fig)

    # Erstellung des Diagramms Anzahl an Büchern pro Kategorie (gelesen, momentan am Lesen, zukünftige Bücher)
    def books_count_plot(self):
        # SQL Abfrage, um die Daten aus der Datenbank zu erhalten
        books_count = self.get_books_count()

        # Größeneinstellungen (Schrift und Diagramm)
        dpi = 100
        fig_width = Window.width / dpi
        fig_height = self.plot_height / dpi
        base_font = Window.width / 30
        title_size = base_font * 2
        label_size = base_font * 1.3
        tick_size = base_font * 0.9

        if books_count:
            # Kategorien gegen Anzahl der Bücher auftragen
            categories, counts = zip(*books_count)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

            # Säulendiagramm erstellen
            ax.bar(categories, counts, color=['blue', 'green', 'red'])

            # Name der Achsen
            ax.set_title('Status', fontsize=title_size)
            ax.set_ylabel('Book Count', fontsize=label_size)

            # Größe der Achsenbeschriftung festlegen
            ax.tick_params(axis='both', which='major', labelsize=tick_size)
            plt.tight_layout()

            self.save_plot_to_image(fig, self.book_count_image)

    # Erstellung des Diagramms gelesene Bücher pro Monat
    def books_per_month_plot(self):
        # SQL Abfrage, um die Daten aus der Datenbank zu erhalten
        data = self.get_books_per_month()

        # Größeneinstellungen (Schrift und Diagramm)
        dpi = 100
        fig_width = Window.width / dpi
        fig_height = self.plot_height / dpi
        base_font = Window.width / 30
        title_size = base_font * 2
        label_size = base_font * 1.3
        tick_size = base_font * 0.9

        if data:
            # Monate gegen Anzahl der Bücher auftragen
            months, counts = zip(*[(int(m), c) for m, c in data if m])
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

            # Säulendiagramm erstellen
            ax.bar(months, counts, color='blue')

            # Achsenabschnitte festlegen und Beschriftung der x-Achse
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

            # Name der Achsen
            ax.set_title('Books Per Month', fontsize=title_size)
            ax.set_ylabel('Books Read', fontsize=label_size)

            # Größe der Achsenbeschriftung festlegen und x-Beschriftung rotieren (sonst überlappen die Beschriftungen schnell auf dem Handy Bildschirm)
            ax.tick_params(axis='both', labelsize=tick_size)
            plt.xticks(rotation=-90)
            plt.tight_layout()

            self.save_plot_to_image(fig, self.books_read_per_month)

    # Erstellung des Diagramms gelesene Seiten pro Monat
    def pages_per_month_plot(self):
        # SQL Abfrage, um die Daten aus der Datenbank zu erhalten
        data = self.get_pages_per_month()

        # Größeneinstellungen (Schrift und Diagramm)
        dpi = 100
        fig_width = Window.width / dpi
        fig_height = self.plot_height / dpi
        base_font = Window.width / 30
        title_size = base_font * 2
        label_size = base_font * 1.3
        tick_size = base_font * 0.9

        if data:
            # Monate gegen Anzahl der Seiten auftragen
            months, pages = zip(*[(int(m), p) for m, p in data if m])
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

            # Säulendiagramm erstellen
            ax.bar(months, pages, color='purple')

            # Achsenabschnitte festlegen und Beschriftung der x-Achse
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

            # Name der Achsen
            ax.set_title('Pages Per Month', fontsize=title_size)
            ax.set_ylabel('Total Pages Read', fontsize=label_size)

            # Größe der Achsenbeschriftung festlegen und x-Beschriftung rotieren (sonst überlappen die Beschriftungen schnell auf dem Handy Bildschirm)
            ax.tick_params(axis='both', labelsize=tick_size)
            plt.xticks(rotation=-90)
            plt.tight_layout()

            self.save_plot_to_image(fig, self.pages_read_per_month)

    # Erstellung des Diagramms Anzahl an Büchern pro Bewertung (0-6 Sterne)
    def rating_distribution_plot(self):
        # SQL Abfrage, um die Daten aus der Datenbank zu erhalten
        data = self.get_ratings_distribution()

        # Größeneinstellungen (Schrift und Diagramm)
        dpi = 100
        fig_width = Window.width / dpi
        fig_height = self.plot_height / dpi
        base_font = Window.width / 30
        title_size = base_font * 2
        label_size = base_font * 1.3
        tick_size = base_font * 0.9
        if data:
            # Bewertungen gegen Anzahl der Bücher auftragen
            ratings, counts = zip(*data)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

            # Säulendiagramm erstellen
            ax.bar(ratings, counts, color='orange')

            # Achsenabschnitte festlegen und Beschriftung der x-Achse
            ax.set_xticks([0, 1, 2, 3, 4, 5])
            ax.set_xticklabels(['Unrated', '1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])

            # Name der Achsen
            ax.set_title('Rating', fontsize=title_size)
            ax.set_ylabel('Book Count', fontsize=label_size)

            # Größe der Achsenbeschriftung festlegen und x-Beschriftung rotieren (sonst überlappen die Beschriftungen schnell auf dem Handy Bildschirm)
            ax.tick_params(axis='both', labelsize=tick_size)
            plt.xticks(rotation=-90)
            plt.tight_layout()

            self.save_plot_to_image(fig, self.rating_distribution)