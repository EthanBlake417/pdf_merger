import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QCheckBox, QListWidget, QListWidgetItem
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

        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        label = QLabel()
        pixmap = QPixmap.fromImage(image)
        label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        layout.addWidget(label)

        page_label = QLabel(f"Page {page_number + 1}")
        layout.addWidget(page_label)

        self.setLayout(layout)

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

        # Enable drag and drop
        self.central_widget.setAcceptDrops(True)

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
