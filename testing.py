import os

from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget,
                               QMessageBox, QMenuBar, QFileDialog, QPushButton, QLineEdit, QLabel, QHBoxLayout, QAbstractItemView)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction


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


# To run the application and see the widget, you can use the following code:
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    list_widget = ReorderableListWidget()
    list_widget.show()
    sys.exit(app.exec_())
