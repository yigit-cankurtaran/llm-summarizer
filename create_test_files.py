#!/usr/bin/env python3
"""
Create test PDF and EPUB files for testing the book processing functionality.
"""

import os
from pathlib import Path

# Create test PDF using reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create test EPUB using ebooklib
from ebooklib import epub

def create_test_pdf():
    """Create a simple test PDF with a few pages."""
    pdf_path = Path("test_books/test.pdf")
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    # Page 1
    c.drawString(100, 750, "This is chapter 1 page 1 of a PDF")
    c.drawString(100, 730, "This is some additional content for testing.")
    c.drawString(100, 710, "The PDF reader should extract this text properly.")
    c.showPage()
    
    # Page 2
    c.drawString(100, 750, "This is chapter 1 page 2 of a PDF")
    c.drawString(100, 730, "More content on the second page.")
    c.drawString(100, 710, "This should be extracted as page 2.")
    c.showPage()
    
    # Page 3
    c.drawString(100, 750, "This is chapter 2 page 3 of a PDF")
    c.drawString(100, 730, "Now we're in chapter 2.")
    c.drawString(100, 710, "Third page of the document.")
    c.showPage()
    
    c.save()
    print(f"Created test PDF: {pdf_path}")

def create_test_epub():
    """Create a simple test EPUB with a few chapters."""
    epub_path = Path("test_books/test.epub")
    
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier('test123')
    book.set_title('Test Book')
    book.set_language('en')
    book.add_author('Test Author')
    
    # Create chapters
    chapter1 = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
    chapter1.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head><title>Chapter 1</title></head>
    <body>
    <h1>Chapter 1</h1>
    <p>This is chapter 1 page 1 of an EPUB.</p>
    <p>This is some additional content for testing the EPUB reader.</p>
    <p>The EPUB processor should extract this text properly.</p>
    </body>
    </html>
    '''
    
    chapter2 = epub.EpubHtml(title='Chapter 2', file_name='chap_02.xhtml', lang='en')
    chapter2.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head><title>Chapter 2</title></head>
    <body>
    <h1>Chapter 2</h1>
    <p>This is chapter 2 page 1 of an EPUB.</p>
    <p>Now we're in the second chapter.</p>
    <p>More content to test the chapter extraction.</p>
    </body>
    </html>
    '''
    
    chapter3 = epub.EpubHtml(title='Chapter 3', file_name='chap_03.xhtml', lang='en')
    chapter3.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head><title>Chapter 3</title></head>
    <body>
    <h1>Chapter 3</h1>
    <p>This is chapter 3 page 1 of an EPUB.</p>
    <p>Final chapter for testing purposes.</p>
    <p>The summarizer should process all chapters.</p>
    </body>
    </html>
    '''
    
    # Add chapters to book
    book.add_item(chapter1)
    book.add_item(chapter2)
    book.add_item(chapter3)
    
    # Create table of contents
    book.toc = (
        epub.Link("chap_01.xhtml", "Chapter 1", "chapter1"),
        epub.Link("chap_02.xhtml", "Chapter 2", "chapter2"),
        epub.Link("chap_03.xhtml", "Chapter 3", "chapter3")
    )
    
    # Add navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS style
    style = 'body { font-family: Arial, sans-serif; }'
    nav_css = epub.EpubItem(uid="nav_css", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    
    # Create spine
    book.spine = ['nav', chapter1, chapter2, chapter3]
    
    # Write EPUB file
    epub.write_epub(str(epub_path), book, {})
    print(f"Created test EPUB: {epub_path}")

if __name__ == "__main__":
    # Ensure test_books directory exists
    Path("test_books").mkdir(exist_ok=True)
    
    create_test_pdf()
    create_test_epub()
    print("Test files created successfully!")
