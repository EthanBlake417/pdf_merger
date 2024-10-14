from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtCore import Qt


class HelpMenu(QMenu):
    def __init__(self, parent=None, icon=None):
        super().__init__("&Help", parent)
        self.icon = icon
        self.create_actions()

    def create_actions(self):
        usage_action = QAction(QIcon(self.windowIcon()), "&Usage", self)
        usage_action.triggered.connect(self.show_help_message)
        self.addAction(usage_action)

        about_action = QAction(QIcon(self.windowIcon()), "&About", self)
        about_action.triggered.connect(self.show_about_message)
        self.addAction(about_action)

    def show_help_message(self):
        help_html = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 500px;">
            <h2 style="color: #4a4a4a;">PDF Editor Usage Guide</h2>
            <ol>
                <li><strong>Adding Files:</strong>
                    <ul>
                        <li>Click "Add Files" to select individual PDF or image files.</li>
                        <li>Click "Add Folder" to add all PDFs and images from a folder.</li>
                    </ul>
                </li>
                <li><strong>Managing Pages:</strong>
                    <ul>
                        <li>Select pages by clicking their checkboxes.</li>
                        <li>Use Ctrl+Click to toggle selection of individual pages.</li>
                        <li>"Select All" and "Deselect All" buttons are available.</li>
                    </ul>
                </li>
                <li><strong>Editing:</strong>
                    <ul>
                        <li>"Remove Selected Pages" deletes chosen pages.</li>
                        <li>"Rotate Selected Pages" rotates chosen pages 90 degrees clockwise.</li>
                        <li>"Normalize Selected Pages" adjusts page sizes (options: Fit, Fill, Stretch).</li>
                        <li>"Unnormalize Selected Pages" reverts normalization.</li>
                    </ul>
                </li>
                <li><strong>Viewing:</strong>
                    <ul>
                        <li>Use "Zoom In" and "Zoom Out" buttons or Ctrl+Mouse Wheel to adjust view.</li>
                    </ul>
                </li>
                <li><strong>Creating Output:</strong>
                    <ul>
                        <li>Specify output filename in the text field or use "Choose File".</li>
                        <li>"Create From Selected Pages" uses only selected pages.</li>
                        <li>"Create All Pages" uses all current pages.</li>
                        <li>Check "Open PDF after creation" to view the result automatically.</li>
                    </ul>
                </li>
                <li><strong>Rearranging:</strong>
                    <ul>
                        <li>Drag and drop pages to reorder them.</li>
                    </ul>
                </li>
                <li><strong>Clearing:</strong>
                    <ul>
                        <li>"Clear" button removes all pages from the editor.</li>
                    </ul>
                </li>
            </ol>
            <p><strong>Supported file types:</strong> PDF (.pdf), PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)</p>
        </body>
        </html>
        """

        help_box = QMessageBox(self.parent())
        help_box.setWindowTitle("How to Use PDF Editor")
        help_box.setText(help_html)
        help_box.setTextFormat(Qt.RichText)

        if self.icon:
            icon_pixmap = self.icon.pixmap(64, 64)
            help_box.setIconPixmap(icon_pixmap)

        help_box.setMinimumWidth(600)
        help_box.exec()

    def show_about_message(self):
        about_html = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #4a4a4a;">PDF Editor</h2>
            <p><strong>Version:</strong> 1.0</p>
            <p>This application allows you to edit and manipulate PDF files and images. 
            You can combine multiple PDFs, rearrange pages, rotate, normalize, 
            and create new PDFs from selected pages.</p>
            <p><strong>Developed using:</strong></p>
            <ul>
                <li>Python 3.12</li>
                <li>PySide6 for the GUI</li>
                <li>PyMuPDF (fitz) for PDF manipulation</li>
            </ul>
            <p style="font-size: 0.9em; color: #888;">© 2024 Ethan Blake. All rights reserved.</p>
        </body>
        </html>
        """

        about_box = QMessageBox(self.parent())
        about_box.setWindowTitle("About PDF Editor")
        about_box.setText(about_html)
        about_box.setTextFormat(Qt.RichText)

        if self.icon:
            icon_pixmap = self.icon.pixmap(64, 64)
            about_box.setIconPixmap(icon_pixmap)

        about_box.setMinimumWidth(400)
        about_box.exec()


if __name__ == '__main__':
    pass
