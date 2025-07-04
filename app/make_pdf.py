import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def make_pdf(output_path="best_quotes.pdf"):
    """
    Fetches quotes with value 10 from quotes.db and generates a PDF file.
    Each quote has content, and at the bottom, author and book in smaller font.
    Quotes are sorted alphabetically by book.
    Returns the path to the generated PDF file.
    """
    # Register a Unicode font (DejaVuSans)
    font_name = "DejaVuSans"
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        print( f"Font file not found: {font_path}")
        return None
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    # Check if database exists
    if not os.path.exists("quotes.db"):
        # Setup PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        styles = getSampleStyleSheet()
        quote_style = ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=14,
            leading=18,
            spaceAfter=12,
        )
        story.append(Paragraph("No best quotes found.", quote_style))
        doc.build(story)
        return output_path

    # Connect to the database
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, book, author FROM quotes WHERE value = 10
    """)
    quotes = cursor.fetchall()
    conn.close()

    # Sort quotes by book (alphabetically)
    quotes.sort(key=lambda x: (x[1] or '').lower())

    # Setup PDF
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()
    quote_style = ParagraphStyle(
        'Quote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceAfter=12,
    )
    author_style = ParagraphStyle(
        'AuthorBook',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=12,
        textColor=colors.grey,
        alignment=2,  # right align
        italic=True,
        spaceAfter=24,
    )

    for content, book, author in quotes:
        story.append(Paragraph(content, quote_style))
        author_book = f"{author or ''} <br/><i>{book or ''}</i>"
        story.append(Paragraph(author_book, author_style))
        story.append(Spacer(1, 0.5*cm))

    if not story:
        story.append(Paragraph("No best quotes found.", quote_style))

    doc.build(story)
    return output_path

