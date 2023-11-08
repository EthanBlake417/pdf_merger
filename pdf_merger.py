import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import tempfile


class ImagePDFConverter:
    def __init__(self, file_list, output_file):
        self.file_list = file_list  # Expect a list of file paths
        self.output_file = output_file

    def convert(self):
        # Initialize a list to hold PIL images and a PdfFileWriter object
        images = []
        pdf_writer = PdfWriter()

        # Process images and PDFs in the file list
        for file_path in self.file_list:
            if file_path == self.output_file:
                continue

            filename = os.path.basename(file_path)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(file_path).convert('RGB')
                images.append(image)
            elif filename.lower().endswith('.pdf'):
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

        # Save all images to a temporary PDF if there are any
        if images:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                images[0].save(
                    tmp.name,
                    save_all=True,
                    append_images=images[1:],
                    quality=100,
                    resolution=100.0
                )
                tmp.close()

                temp_pdf_reader = PdfReader(tmp.name)
                for page in temp_pdf_reader.pages:
                    pdf_writer.add_page(page)

                os.unlink(tmp.name)

        # Write the final PDF to the output file
        with open(self.output_file, "wb") as f:
            pdf_writer.write(f)

        # Print success messages
        num_images = len(images)
        num_pdfs = len(pdf_writer.pages)
        if num_images > 0:
            print(f'Successfully converted {num_images} image(s) to PDF.')
        if num_pdfs > 0:
            print(f'Successfully combined {num_pdfs} page(s) into {self.output_file}.')
        if num_images == 0 and num_pdfs == 0:
            print(f'No images or PDF files found in the provided file list!')


if __name__ == '__main__':
    # Usage
    file_paths = [
        '/path/to/file1.jpg',
        '/path/to/file2.png',
        '/path/to/document.pdf',
        # Add more file paths as needed
    ]
    converter = ImagePDFConverter(file_paths, 'output.pdf')
    converter.convert()
