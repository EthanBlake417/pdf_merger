import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import tempfile


class ImagePDFConverter:
    def __init__(self, input_directory, output_file):
        self.input_directory = input_directory
        self.output_file = output_file

    def convert(self):
        # Initialize a list to hold PIL images and a PdfFileWriter object
        images = []
        pdf_writer = PdfWriter()

        # Process images and PDFs in the directory
        for filename in os.listdir(self.input_directory):
            file_path = os.path.join(self.input_directory, filename)
            if file_path == self.output_file:
                continue

            if filename.lower().endswith(('.png', '.jpg')):
                image = Image.open(file_path).convert('RGB')
                images.append(image)
            elif filename.lower().endswith('.pdf'):
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

        # Save all images to a temporary PDF if there are any
        if images:
            # Use tempfile to create a temporary file with .pdf extension
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                images[0].save(
                    tmp.name,
                    save_all=True,
                    append_images=images[1:],
                    quality=100,
                    resolution=100.0
                )
                # Ensure the temporary file is closed before attempting to read it
                tmp.close()

                # Read the temporary PDF and add its pages to the writer
                temp_pdf_reader = PdfReader(tmp.name)
                for page in temp_pdf_reader.pages:
                    pdf_writer.add_page(page)

                # Delete the temporary file after appending its pages to the writer
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
            print(f'No images or PDF files found in {self.input_directory}!')


if __name__ == '__main__':
    # Usage
    converter = ImagePDFConverter('files', 'output.pdf')
    converter.convert()
