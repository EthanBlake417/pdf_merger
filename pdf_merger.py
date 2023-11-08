# import PyPDF2
# import time
# import os
# from PIL import Image
#
#
# class PNGtoPDFConverter:
#     def __init__(self, png_directory, output_file):
#         self.png_directory = png_directory
#         self.output_file = output_file
#
#     def convert(self):
#         images = []
#         for filename in os.listdir(self.png_directory):
#             if filename.endswith('.png'):
#                 image_path = os.path.join(self.png_directory, filename)
#                 image = Image.open(image_path).convert('RGB')
#                 images.append(image)
#
#         if images:
#             images[0].save(
#                 self.output_file,
#                 save_all=True,
#                 append_images=images[1:]
#             )
#             print(f'Successfully converted {len(images)} PNG images to PDF!')
#         else:
#             print(f'No PNG images found in {self.png_directory}!')
#
# import os
# from PyPDF2 import PdfReader, PdfWriter
# import fitz  # PyMuPDF
# import io  # For bytes stream
#
# def combine_pdf_jpg(folder_path, output_pdf_name):
#     writer = PdfWriter()
#
#     # List all files in the directory and sort them alphabetically
#     files = sorted([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
#
#     for filename in files:
#         if filename.lower().endswith('.pdf'):
#             # Open the PDF file
#             pdf_file_path = os.path.join(folder_path, filename)
#             pdf_reader = PdfReader(pdf_file_path)
#
#             # Add all its pages to the writer
#             for page in pdf_reader.pages:
#                 writer.add_page(page)
#
#         elif filename.lower().endswith('.jpg'):
#             # Open the JPG file and convert it to a PDF page
#             jpg_file_path = os.path.join(folder_path, filename)
#             img_doc = fitz.open(jpg_file_path)  # Open image as a document
#             img_pdf_bytes = img_doc.convert_to_pdf()  # Convert to PDF bytes
#             img_doc.close()
#
#             # Use a BytesIO stream to make it file-like
#             pdf_stream = io.BytesIO(img_pdf_bytes)
#             pdf_reader = PdfReader(pdf_stream)
#
#             # Add the single page from the converted PDF
#             writer.add_page(pdf_reader.pages[0])
#
#     # Write out the combined PDF
#     output_pdf_path = os.path.join(folder_path, output_pdf_name)
#     with open(output_pdf_path, 'wb') as out:
#         writer.write(out)
#
#     print(f"Created combined PDF '{output_pdf_name}' with all PDF and JPG files from '{folder_path}'.")
#
# # Example usage:
# combine_pdf_jpg(r'C:\Users\ethan\Desktop\sherri_album', 'sherri_album_music.pdf')
#
#
# import os
# from PIL import Image
# from PyPDF2 import PdfReader, PdfWriter
#
#
# class ImagePDFConverter:
#     def __init__(self, input_directory, output_file):
#         self.input_directory = input_directory
#         self.output_file = output_file
#
#     def convert(self):
#         # Initialize a list to hold PIL images and a PdfFileWriter object
#         images = []
#         pdf_writer = PdfWriter()
#
#         for filename in os.listdir(self.input_directory):
#             file_path = os.path.join(self.input_directory, filename)
#
#             # Check if the file is the output file to avoid reading and writing the same file
#             if file_path == self.output_file:
#                 continue
#
#             if filename.endswith('.png') or filename.endswith('.jpg'):
#                 # Open the image and convert it to RGB
#                 image = Image.open(file_path).convert('RGB')
#                 images.append(image)
#             elif filename.endswith('.pdf'):
#                 # Read the existing PDF and add its pages
#                 pdf_reader = PdfReader(file_path)
#                 for page in range(len(pdf_reader.pages)):
#                     pdf_writer.add_page(pdf_reader.pages[page])
#
#         # Save all the images as a PDF
#         if images:
#             images[0].save(
#                 self.output_file,
#                 save_all=True,
#                 append_images=images[1:],
#                 quality=100,
#                 resolution=100.0
#             )
#
#         # Append the output PDF to the existing PDFs collected
#         if os.path.exists(self.output_file):
#             with open(self.output_file, "rb") as f:
#                 pdf_reader = PdfReader(f)
#                 for page in range(pdf_reader.getNumPages()):
#                     pdf_writer.addPage(pdf_reader.getPage(page))
#
#             # Write the combined PDF to a new file
#             with open(self.output_file, "wb") as f:
#                 pdf_writer.write(f)
#
#         # Print success messages
#         num_images = len(images)
#         num_pdfs = len(pdf_writer.pages)
#         if num_images > 0:
#             print(f'Successfully converted {num_images} image(s) to PDF.')
#         if num_pdfs > 0:
#             print(f'Successfully appended {num_pdfs} page(s) from existing PDF(s).')
#         if num_images == 0 and num_pdfs == 0:
#             print(f'No images or PDF files found in {self.input_directory}!')
#
#
# if __name__ == '__main__':
#     # Usage
#     # Make sure to import the required modules at the beginning of your script.
#     # Create an instance of the class and call the convert method.
#     converter = ImagePDFConverter('files', 'output.pdf')
#     converter.convert()
#
#     # After conversion code
#     output_file_path = 'output.pdf'  # Ensure this matches your actual output path
#
#     if os.path.isfile(output_file_path):
#         print(f"The output file is located at: {output_file_path}")
#         print(f"File size: {os.path.getsize(output_file_path)} bytes")
#     else:
#         print(f"The output file was not found. Please check the directory and permissions.")


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
