import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QCheckBox, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, QMimeData
import fitz  # PyMuPDF

from PySide6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout


class PdfPageItem(QWidget):
    def __init__(self, page_number, image):
        super().__init__()
        layout = QHBoxLayout()

        self.checkbox = QCheckBox(f"Page {page_number + 1}")
        layout.addWidget(self.checkbox)

        self.label = QLabel()
        self.pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(self.pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        layout.addWidget(self.label)

        self.setLayout(layout)

    def set_image_size(self, size):
        self.label.setPixmap(self.pixmap.scaled(size, size, Qt.KeepAspectRatio))

    def is_checked(self):
        return self.checkbox.isChecked()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.resize(1200, 800)

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.scroll_area = QScrollArea(self.central_widget)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.scroll_area)
        self.grid_layout = QGridLayout(self.scroll_widget)

        # Zoom in Functionallity:
        self.zoom_level = 200

        self.zoom_in_button = QPushButton("Zoom In", self.central_widget)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out", self.central_widget)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.layout.addWidget(self.zoom_out_button)

        # Enable drag and drop
        self.central_widget.setAcceptDrops(True)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()

    def zoom_in(self):
        self.zoom_level += 20
        self.update_thumbnails()
        self.update_grid_layout()

    def zoom_out(self):
        if self.zoom_level > 20:
            self.zoom_level -= 20
            self.update_thumbnails()
            self.update_grid_layout()

    def update_thumbnails(self):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, PdfPageItem):
                widget.set_image_size(self.zoom_level)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.fileName().endswith('.pdf'):
                self.load_pdf(url.toLocalFile())

    def load_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        self.clear_grid()

        column = 0
        row = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, QImage.Format_RGB888)

            item_widget = PdfPageItem(page_num, image)
            self.grid_layout.addWidget(item_widget, row, column)

            column += 1
            if column >= 3:  # Adjust number of columns as needed
                column = 0
                row += 1

        doc.close()
        self.update_grid_layout()

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.update_grid_layout()

    def update_grid_layout(self):
        window_width = self.scroll_widget.width()
        # Determine the number of columns based on window width and zoom level
        column_count = max(1, window_width // (self.zoom_level + 20))  # Adjust 20 for padding/margins
        self.rearrange_grid(column_count)

    def rearrange_grid(self, column_count):
        # Temporary storage for widgets
        temp_widgets = []
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            temp_widgets.append((widget, self.grid_layout.getItemPosition(i)))

        # Clear the layout
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Re-add widgets in the correct order
        row = column = 0
        for widget, _ in sorted(temp_widgets, key=lambda x: x[1]):
            self.grid_layout.addWidget(widget, row, column)
            column += 1
            if column >= column_count:
                column = 0
                row += 1

    def clear_grid(self):
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
