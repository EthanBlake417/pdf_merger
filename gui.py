import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget,
                               QMessageBox, QMenuBar, QFileDialog, QPushButton, QLineEdit, QLabel, QHBoxLayout, QAbstractItemView)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction
from pdf_merger import ImagePDFConverter


class ReorderableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    local_file = url.toLocalFile()
                    if os.path.isdir(local_file):
                        # It's a directory, so list all files and filter by extension
                        for root, dirs, files in os.walk(local_file):
                            for file in files:
                                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                                    full_path = os.path.join(root, file)
                                    self.addItem(full_path)
                    else:
                        # It's a file, add it if it has the correct extension
                        if local_file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                            self.addItem(local_file)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def addFiles(self, file_paths):
        """
        Add files to the list widget from a given list of file paths.
        """
        for file_path in file_paths:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                self.addItem(file_path)

    def addItemsFromDirectory(self, directory_path):
        """
        Add files to the list widget from the selected directory.
        """
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    full_path = os.path.join(root, file)
                    self.addItem(full_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pdf Merger')
        self.resize(800, 500)
        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.add_files)
        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        self.output_file_name = ''
        self.setup_ui()
        self.create_menu_bar()

        # Show a message box on close to handle the files, if necessary
        self.closeEvent = self.handle_close

    def setup_ui(self):
        self.list_widget = ReorderableListWidget()

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.on_convert_click)

        self.output_line_edit = QLineEdit()
        self.output_line_edit.setPlaceholderText("Enter output file name here...")

        self.output_file_button = QPushButton("Choose File")
        self.output_file_button.clicked.connect(self.choose_output_file)

        # Set up layout for the output file selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(self.output_file_button)

        # Use a QVBoxLayout for the main layout
        main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_files_button)
        buttons_layout.addWidget(self.add_folder_button)
        main_layout.addLayout(buttons_layout)

        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.convert_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select one or more files to open",
            "",
            "Images or PDF (*.png *.jpg *.jpeg *.pdf)",
            options=options
        )
        if files:
            self.list_widget.addFiles(files)

    def add_folder(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            options=options
        )
        if directory:
            self.list_widget.addItemsFromDirectory(directory)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("&File")

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        self.setMenuBar(menu_bar)

    def choose_output_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Choose output file", "", "PDF Files (*.pdf)", options=options)
        if file_name:
            if not file_name.endswith('.pdf'):
                file_name += '.pdf'
            self.output_line_edit.setText(file_name)
            self.output_file_name = file_name

    def on_convert_click(self):
        # You would connect this method to your backend processing here.
        file_list = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        output_file = self.output_line_edit.text()

        if not output_file:
            QMessageBox.warning(self, "No Output File", "Please specify an output file name.")
            return

        if not file_list:
            QMessageBox.warning(self, "No Files", "Please drag and drop files to convert.")
            return

        # Here you could call a backend function to process these files, for example:
        # self.backend.convert_files(file_list, output_file)
        QMessageBox.information(self, "Conversion Started", f"Files will be converted to {output_file}")
        converter = ImagePDFConverter(file_list, output_file)
        status = converter.convert()
        QMessageBox.information(self, "Conversion Completed", status)

    def handle_close(self, event):
        # If needed, do any checks or cleanup before closing
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
