from moviepy.editor import *
from docx2pdf import convert
from pdf2image import convert_from_path
import subprocess
import os


def convert_docx_to_pdf(docx_path, pdf_path):
    """Converts a .docx file to a .pdf file."""
    try:
        convert(docx_path, pdf_path)

        print(f"Successfully converted {docx_path} to {pdf_path}")
    except Exception as e:
        print(f"Error converting {docx_path} to PDF: {e}")


def convert_pptx_to_mp4(pptx_path, mp4_path):
    """Converts a .pptx file to a .mp4 video."""
    try:
        clip = VideoFileClip(pptx_path)
        clip.write_videofile(mp4_path, fps=24)
        print(f"Successfully converted {pptx_path} to {mp4_path}")
    except Exception as e:
        print(f"Error converting {pptx_path} to MP4: {e}")

def convert_to_pdf_using_libreoffice(word_file, pdf_file):
    # Set output path if not specified
    if pdf_file is None:
        pdf_file = os.path.splitext(word_file)[0] + ".pdf"
    
    # Run the LibreOffice command to convert to PDF
    result = subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
        os.path.dirname(pdf_file), word_file
    ], check=True)
    
    # Check if the file was created successfully
    if os.path.exists(pdf_file):
        print(f"Conversion successful: {pdf_file}")
        return pdf_file
    else:
        raise FileNotFoundError("PDF conversion failed.")


def convert_pptx_to_mp4_opencv(input_pdf, output_video, output_dir=None, image_format="png", dpi=300):
    # Set output directory
    if output_dir is None:
        output_dir = os.path.splitext(input_pdf)[0]
    os.makedirs(output_dir, exist_ok=True)

    # Convert PDF to a list of images (one per page)
    images = convert_from_path(input_pdf, dpi=dpi)

    # Save each page as an image
    image_paths = []
    for i, img in enumerate(images):
        image_name = str(i + 1).zfill(3)
        image_path = os.path.join(output_dir, f"page_{image_name}.{image_format}")
        img.save(image_path, image_format.upper())
        image_paths.append(image_path)
    
    print(f"PDF converted to images. Images saved in {output_dir}")
    
    image_folder = output_dir

    # Get list of images sorted by name
    images = [img for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()  # Ensure images are in correct order

    # Get the dimensions of the first image
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # Define the video codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4
    fps = 0.5  # Frames per second
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Add each image to the video
    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        video.write(frame)  # Write each image as a frame

    # Release the video writer
    video.release()
    print(f"Video saved as {output_video}")