import os
import shutil
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QCheckBox, QListWidget, QListWidgetItem, QPushButton, QFileDialog, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, QMimeData
import fitz  # PyMuPDF

from PySide6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtGui import QPixmap, QImage, QDrag, QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout
import logging
import psutil

ENABLE_LOGGING = True
if not os.path.exists("temp_files"):
    os.makedirs("temp_files")

if ENABLE_LOGGING:
    logging.basicConfig(filename='pdf_editor.log', level=logging.DEBUG)
else:
    logging.basicConfig(handlers=[logging.NullHandler()])


class PdfPageItem(QWidget):
    def __init__(self, page_number, image, original_pdf_path, original_page_number):
        super().__init__()
        self.original_page_number = original_page_number  # Store the original page number
        self.original_pdf_path = original_pdf_path  # Store the path of the original PDF
        self.page_number = page_number  # This

        self.drag_start_position = None  # Initialize here
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
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.checkbox.setChecked(not self.checkbox.isChecked())
        super().mousePressEvent(event)  # Call the parent class's mousePressEvent method
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
        self.counter = 0
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

        # Add menu bar
        self.create_menu_bar()
        self.delete_pdf_files("temp_files")

    def delete_pdf_files(self, folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def create_menu_bar(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        # Exit Action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)  # Connect to the close method of the window
        file_menu.addAction(exit_action)

        # Help Section
        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction("&Usage", self)
        help_action.triggered.connect(self.show_help_message)
        help_menu.addAction(help_action)

    def show_help_message(self):
        message = "Press Ctrl and click on a page to select its checkbox."
        QMessageBox.information(self, "How to Use", message)

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
        try:
            new_pdf.save(output_file)
            new_pdf.close()

            if self.open_pdf_checkbox.isChecked():
                self.open_pdf(output_file)
        except ValueError:
            QMessageBox.warning(self, "Error", "Cannot save with zero pages.")

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
                self.load_pdf_or_image(file_name)

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
                self.load_pdf_or_image(full_path)

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

    def find_pdf_page_item_at(self, position):
        for child in self.central_widget.findChildren(PdfPageItem):
            if child.geometry().contains(position):
                return child
        return None

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():  # Handling file drop
            for url in mime.urls():
                if url.isLocalFile():
                    self.load_pdf_or_image(url.toLocalFile())
        elif mime.hasText():  # Handling internal widget drop
            source_index = int(mime.text())
            target_widget_pos = event.position().toPoint()
            target_widget = self.find_pdf_page_item_at(target_widget_pos)
            if target_widget and isinstance(target_widget, PdfPageItem):
                target_index = self.page_items.index(target_widget)
                if target_index != source_index:
                    # Swap the items in self.page_items list
                    moved_item = self.page_items.pop(source_index)
                    self.page_items.insert(target_index, moved_item)

                    # Rebuild the grid layout with the new order
                    self.rearrange_grid(self.column_count)
                    self.update_page_numbers()

        event.acceptProposedAction()

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

    def load_pdf_or_image(self, file_path):
        if file_path.lower().endswith('.pdf'):
            self.load_pdf(file_path)
        else:
            self.load_image_as_pdf(file_path)

    def load_image_as_pdf(self, image_path):
        try:
            self.counter += 1
            # Create a new PDF document
            pdf_doc = fitz.open()

            # Create a new page with dimensions based on the image size
            img = fitz.open(image_path)  # Open the image as a document
            rect = img[0].rect  # The dimensions of the image
            pdf_page = pdf_doc.new_page(width=rect.width, height=rect.height)

            # Insert the image into the new page
            pdf_page.insert_image(rect, filename=image_path)

            # Save the PDF to a temporary file or in memory
            temp_pdf = f"temp_files/{self.counter}.pdf"  # Consider using a more robust temp file approach
            pdf_doc.save(temp_pdf)
            pdf_doc.close()

            # Now load this temporary PDF as usual
            self.load_pdf(temp_pdf)  # Pass original image path for reference
        except Exception as e:
            QMessageBox.warning(self, "Error", f"{e}")

    def load_pdf(self, pdf_path):
        logging.info(f"Attempting to load PDF: {pdf_path}")
        print(f"Attempting to load PDF: {pdf_path}")

        # Check file size
        file_size = os.path.getsize(pdf_path)
        logging.debug(f"File size: {file_size / (1024 * 1024):.2f} MB")
        print(f"File size: {file_size / (1024 * 1024):.2f} MB")
        if file_size > 100_000_000:  # 100 MB limit, adjust as needed
            logging.warning(f"File is too large: {file_size / (1024 * 1024):.2f} MB")
            QMessageBox.warning(self, "Error", "File is too large to load")
            return

        try:
            # Attempt to open the PDF
            doc = fitz.open(pdf_path)
            logging.info(f"Successfully opened {pdf_path}")
            print(f"Successfully opened {pdf_path}")

            # Log PDF information
            logging.debug(f"Number of pages: {len(doc)}")
            logging.debug(f"Metadata: {doc.metadata}")
            logging.debug(f"Is encrypted: {doc.is_encrypted}")
            logging.debug(f"Permissions: {doc.permissions}")
            print(f"Number of pages: {len(doc)}")
            print(f"Metadata: {doc.metadata}")
            print(f"Is encrypted: {doc.is_encrypted}")
            print(f"Permissions: {doc.permissions}")

            # Check permissions
            if doc.permissions <= 0:
                logging.warning(f"Unusual permissions value ({doc.permissions}) for {pdf_path}")
                print(f"Warning: Unusual permissions value ({doc.permissions}) for {pdf_path}")

            current_count = len(self.page_items)
            for page_num in range(len(doc)):
                try:
                    # Check available memory before loading each page
                    available_memory = psutil.virtual_memory().available
                    if available_memory < 100 * 1024 * 1024:  # 100 MB threshold
                        logging.warning(f"Low memory warning: Only {available_memory / (1024 * 1024):.2f} MB available")
                        print(f"Low memory warning: Only {available_memory / (1024 * 1024):.2f} MB available")
                        QMessageBox.warning(self, "Low Memory", "Running low on memory. The application might become unstable.")

                    # Load the page
                    page = doc.load_page(page_num)
                    logging.debug(f"Loaded page {page_num + 1}")
                    print(f"Loaded page {page_num + 1}")

                    # Create pixmap with error handling
                    try:
                        pix = page.get_pixmap(alpha=False)  # Disable alpha channel
                        logging.debug(f"Created pixmap for page {page_num + 1}")
                        print(f"Created pixmap for page {page_num + 1}")
                    except Exception as e:
                        logging.error(f"Error creating pixmap for page {page_num + 1}: {str(e)}")
                        print(f"Error creating pixmap for page {page_num + 1}: {str(e)}")
                        continue  # Skip this page and try the next one

                    # Create QImage with error handling
                    try:
                        if pix.samples:
                            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                            if image.isNull():
                                raise ValueError(f"Created QImage is null for page {page_num + 1}")
                            logging.debug(f"Created QImage for page {page_num + 1}")
                            print(f"Created QImage for page {page_num + 1}")
                        else:
                            raise ValueError(f"Pixmap samples are null for page {page_num + 1}")
                    except Exception as e:
                        logging.error(f"Error creating QImage for page {page_num + 1}: {str(e)}")
                        print(f"Error creating QImage for page {page_num + 1}: {str(e)}")
                        continue  # Skip this page and try the next one

                    # Create and add widget
                    try:
                        item_widget = PdfPageItem(current_count + page_num + 1, image, pdf_path, page_num + 1)
                        self.page_items.append(item_widget)
                        self.grid_layout.addWidget(item_widget, (current_count + page_num) // self.column_count, (current_count + page_num) % self.column_count)
                        item_widget.set_image_size(self.zoom_level)
                        logging.debug(f"Added widget for page {page_num + 1}")
                        print(f"Added widget for page {page_num + 1}")
                    except Exception as e:
                        logging.error(f"Error adding widget for page {page_num + 1}: {str(e)}")
                        print(f"Error adding widget for page {page_num + 1}: {str(e)}")

                except Exception as e:
                    logging.error(f"Error processing page {page_num + 1} of {pdf_path}: {str(e)}")
                    print(f"Error processing page {page_num + 1} of {pdf_path}: {str(e)}")
                    QMessageBox.warning(self, "Error", f"Failed to process page {page_num + 1}: {str(e)}")

            # Close the document
            doc.close()
            self.update_page_numbers()
            self.update_grid_layout()
            logging.info(f"Successfully loaded all pages from {pdf_path}")
            print(f"Successfully loaded all pages from {pdf_path}")

        except fitz.FileDataError as e:
            logging.error(f"PyMuPDF FileDataError for {pdf_path}: {str(e)}")
            print(f"PyMuPDF FileDataError for {pdf_path}: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load PDF: {str(e)}")
        except MemoryError:
            logging.error(f"MemoryError while loading {pdf_path}")
            print(f"MemoryError while loading {pdf_path}")
            QMessageBox.warning(self, "Error", "Not enough memory to load this PDF")
        except Exception as e:
            logging.error(f"Unexpected error loading {pdf_path}: {str(e)}")
            print(f"Unexpected error loading {pdf_path}: {str(e)}")
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")

        # Add a final check to see if any pages were successfully loaded
        if not self.page_items:
            logging.warning(f"No pages were successfully loaded from {pdf_path}")
            print(f"No pages were successfully loaded from {pdf_path}")
            QMessageBox.warning(self, "Warning", "No pages were successfully loaded from the PDF.")

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

    def closeEvent(self, event):
        """Override closeEvent to clean up temp files before closing."""
        self.cleanup_temp_files()
        super().closeEvent(event)

    def cleanup_temp_files(self):
        """Remove the temp_files directory and its contents."""
        try:
            shutil.rmtree("temp_files")
            logging.info(f"Successfully removed temp files directory.")
        except Exception as e:
            logging.error(f"Failed to remove temp_files directory: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
