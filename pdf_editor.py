import os
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QCheckBox, QListWidget, QListWidgetItem, QPushButton, QFileDialog, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, QMimeData
import fitz  # PyMuPDF

from PySide6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPixmap, QImage, QDrag
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout


class PdfPageItem(QWidget):
    def __init__(self, page_number, image, original_pdf_path):
        super().__init__()
        self.original_page_number = page_number
        self.original_pdf_path = original_pdf_path  # Store the path of the original PDF

        self.drag_start_position = None  # Initialize here
        # Using QVBoxLayout for vertical stacking of elements
        layout = QVBoxLayout()

        self.checkbox = QCheckBox(f"Page {page_number + 1}")
        layout.addWidget(self.checkbox)

        self.label = QLabel()
        self.pixmap = QPixmap.fromImage(image)
        # self.label.setPixmap(self.pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        layout.addWidget(self.label)

        self.setLayout(layout)

    def set_image_size(self, size):
        self.label.setPixmap(self.pixmap.scaled(size, size, Qt.KeepAspectRatio))

    def is_checked(self):
        return self.checkbox.isChecked()

    def update_page_number(self, new_number):
        self.page_number = new_number  # Update the page number
        self.checkbox.setText(f"Page {new_number}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return

        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimedata = QMimeData()
        index = self.window().page_items.index(self)
        mimedata.setText(str(index))  # Store the index of the widget
        drag.setMimeData(mimedata)
        drag.exec(Qt.MoveAction)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.page_items = []
        self.column_count = 3  # You can adjust this as needed

        self.setWindowTitle("Pdf Editor")
        self.resize(1200, 800)

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.scroll_area = QScrollArea(self.central_widget)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.add_top_widgets()

        self.layout.addWidget(self.scroll_area)
        self.add_bottom_widgets()

        self.grid_layout = QGridLayout(self.scroll_widget)

        # Zoom in Functionallity:
        self.zoom_level = 400

        # Enable drag and drop
        self.central_widget.setAcceptDrops(True)
        self.setAcceptDrops(True)

    def add_top_widgets(self):
        # Create a horizontal layout for buttons
        self.buttons_layout = QHBoxLayout()

        # Add 'Add Files' button
        self.add_files_button = QPushButton("Add Files", self.central_widget)
        self.add_files_button.clicked.connect(self.add_files)
        self.buttons_layout.addWidget(self.add_files_button)

        # Add 'Add Folder' button
        self.add_folder_button = QPushButton("Add Folder", self.central_widget)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.buttons_layout.addWidget(self.add_folder_button)

        # Add buttons to the horizontal layout
        self.remove_selected_button = QPushButton("Remove Selected Pages", self.central_widget)
        self.remove_selected_button.clicked.connect(self.remove_selected_pages)
        self.buttons_layout.addWidget(self.remove_selected_button)

        self.clear_button = QPushButton("Clear", self.central_widget)
        self.clear_button.clicked.connect(self.clear_pages)
        self.buttons_layout.addWidget(self.clear_button)

        self.select_all_button = QPushButton("Select All", self.central_widget)
        self.select_all_button.clicked.connect(self.select_all_pages)
        self.buttons_layout.addWidget(self.select_all_button)

        # Add Deselect All button
        self.deselect_all_button = QPushButton("Deselect All", self.central_widget)
        self.deselect_all_button.clicked.connect(self.deselect_all_pages)
        self.buttons_layout.addWidget(self.deselect_all_button)

        self.zoom_in_button = QPushButton("Zoom In", self.central_widget)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.buttons_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out", self.central_widget)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.buttons_layout.addWidget(self.zoom_out_button)

        # Add the buttons layout to the top of the main layout
        self.layout.addLayout(self.buttons_layout)

    def add_bottom_widgets(self):
        # Create a layout for output file settings
        self.output_file_layout = QHBoxLayout()

        self.output_label = QLabel("Output PDF:")
        self.output_file_layout.addWidget(self.output_label)

        self.output_line_edit = QLineEdit()
        self.output_line_edit.setPlaceholderText("Enter output file name here...")
        self.output_file_layout.addWidget(self.output_line_edit)

        self.choose_file_button = QPushButton("Choose File")
        self.choose_file_button.clicked.connect(self.choose_output_file)
        self.output_file_layout.addWidget(self.choose_file_button)

        self.open_pdf_checkbox = QCheckBox("Open PDF after creation")
        self.output_file_layout.addWidget(self.open_pdf_checkbox)
        self.open_pdf_checkbox.setChecked(True)
        # Add the output file layout to the main layout
        self.layout.addLayout(self.output_file_layout)

        # Create a layout for the create buttons
        self.create_buttons_layout = QHBoxLayout()

        self.create_selected_button = QPushButton("Create From Selected Pages")
        self.create_selected_button.clicked.connect(self.create_from_selected_pages)
        self.create_buttons_layout.addWidget(self.create_selected_button)

        self.create_all_button = QPushButton("Create All Pages")
        self.create_all_button.clicked.connect(self.create_all_pages)
        self.create_buttons_layout.addWidget(self.create_all_button)

        # Add the create buttons layout to the main layout
        self.layout.addLayout(self.create_buttons_layout)

    # Slot functions for the create buttons
    def create_pdf(self, selected_only):
        output_file = self.output_line_edit.text()
        if not output_file:
            QMessageBox.warning(self, "Error", "Please specify an output file name.")
            return

        new_pdf = fitz.open()  # Create a new empty PDF
        for item in self.page_items:
            if selected_only and not item.is_checked():
                continue

            original_pdf_path, original_page_number = item.original_pdf_path, item.original_page_number
            original_pdf = fitz.open(original_pdf_path)
            new_pdf.insert_pdf(original_pdf, from_page=original_page_number - 1, to_page=original_page_number - 1)
            original_pdf.close()

        new_pdf.save(output_file)
        new_pdf.close()

        if self.open_pdf_checkbox.isChecked():
            self.open_pdf(output_file)

    def create_from_selected_pages(self):
        self.create_pdf(selected_only=True)

    def create_all_pages(self):
        self.create_pdf(selected_only=False)

    def open_pdf(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])

    def choose_output_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Choose output file", "", "PDF Files (*.pdf)")
        if file_name:
            if not file_name.endswith('.pdf'):
                file_name += '.pdf'
            self.output_line_edit.setText(file_name)

    def add_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            for file_name in file_names:
                self.load_pdf(file_name)

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.load_pdfs_from_folder(folder_path)

    def load_pdfs_from_folder(self, folder_path):
        # Assuming you're using os.listdir, adjust if using a different method
        import os
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.pdf'):
                full_path = os.path.join(folder_path, file_name)
                self.load_pdf(full_path)

    def deselect_all_pages(self):
        for item in self.page_items:
            item.checkbox.setChecked(False)

    def remove_selected_pages(self):
        self.page_items = [item for item in self.page_items if not item.is_checked()]
        self.rearrange_grid(self.column_count)
        self.update_page_numbers()

    def clear_pages(self):
        self.page_items.clear()
        self.rearrange_grid(self.column_count)

    def select_all_pages(self):
        for item in self.page_items:
            item.checkbox.setChecked(True)

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():  # Handling file drop
            for url in mime.urls():
                if url.isLocalFile() and url.fileName().endswith('.pdf'):
                    self.load_pdf(url.toLocalFile())
        elif mime.hasText():  # Handling internal widget drop
            source_index = int(mime.text())
            target_widget_pos = event.position().toPoint()
            target_widget = self.childAt(target_widget_pos)

            if target_widget and isinstance(target_widget, PdfPageItem):
                target_index = self.page_items.index(target_widget)
                if target_index != source_index:
                    # Swap the items in self.page_items list
                    self.page_items[source_index], self.page_items[target_index] = \
                        self.page_items[target_index], self.page_items[source_index]

                    # Rebuild the grid layout with the new order
                    self.rearrange_grid(self.column_count)
                    self.update_page_numbers()
                    self.update_page_items_order()  # Update the order of self.page_items

        event.acceptProposedAction()

    def update_page_items_order(self):
        # Update the order of self.page_items to match the current grid layout
        ordered_items = []
        for row in range(self.grid_layout.rowCount()):
            for column in range(self.grid_layout.columnCount()):
                widget = self.grid_layout.itemAtPosition(row, column)
                if widget is not None and isinstance(widget.widget(), PdfPageItem):
                    ordered_items.append(widget.widget())
        self.page_items = ordered_items

    def find_nearest_widget_index(self, position):
        min_distance = float('inf')
        nearest_index = None

        for i, widget in enumerate(self.page_items):
            # Calculate the position of the widget in the grid
            row, column = self.grid_layout.getItemPosition(i)[:2]
            widget_pos = self.grid_layout.cellRect(row, column).center()

            # Calculate the distance to the drop position
            distance = (widget_pos - position).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                nearest_index = i

        return nearest_index

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
        elif event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def load_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        current_count = len(self.page_items)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, QImage.Format_RGB888)

            item_widget = PdfPageItem(current_count + page_num + 1, image, pdf_path)
            self.page_items.append(item_widget)
            self.grid_layout.addWidget(item_widget, (current_count + page_num) // self.column_count, (current_count + page_num) % self.column_count)
            # Set the image size according to the current zoom level
            item_widget.set_image_size(self.zoom_level)
        doc.close()
        self.update_page_numbers()
        self.update_grid_layout()

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        # Dynamically calculate the number of columns
        self.column_count = self.calculate_column_count()
        self.update_grid_layout()

    def update_grid_layout(self):
        # Determine the number of columns based on window width and zoom level
        self.column_count = self.calculate_column_count()
        self.rearrange_grid(self.column_count)

    def calculate_column_count(self):
        window_width = self.scroll_widget.width()
        item_width = self.zoom_level + 50  # or self.zoom_level + some padding
        return max(1, window_width // item_width)

    def rearrange_grid(self, column_count):
        # Clear the layout
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Re-add widgets in the new order
        row = column = 0
        for widget in self.page_items:
            self.grid_layout.addWidget(widget, row, column)
            column += 1
            if column >= column_count:
                column = 0
                row += 1

    def update_page_numbers(self):
        for i, widget in enumerate(self.page_items):
            widget.update_page_number(i + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
