from moviepy.editor import *
from docx2pdf import convert


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
