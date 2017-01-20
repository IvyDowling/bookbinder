import json
import sys
import os
from collections import OrderedDict
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch, cm

supportedStyles = [
    "font",
    "background-color",
    "rotate",
    "margin",
    "margin-top",
    "margin-bottom",
    "margin-right",
    "margin-left"
]


def reader(filename):
    with open(filename) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
    # document has style obj and pages obj
    global_style = data["style"]
    page_style = []
    for p in data["pages"]:
        inherit = global_style.copy()
        for key, value in p["style"].iteritems():
            inherit[key] = value
        page_style.append(inherit)
    book = []
    for p in data["pages"]:
        book.append(Page(OrderedDict(p["content"]), page_style))
    paragraphs = translate(book)
    writer(filename.rsplit(".", 1)[0], paragraphs)


def translate(book):
    """
    :param book: List of content and style tuples for each pages
    :return: List of Paragraphs with styling and content setup for platypus

    --here are all of the params of ParagraphStyle:
    spaceBefore = 0, fontName = Helvetica, bulletFontName = Helvetica
    borderRadius = None, firstLineIndent = 0, leftIndent = 0
    underlineProportion = 0.0, rightIndent = 0, wordWrap = None
    allowWidows = 1, backColor = None, justifyLastLine = 0
    textTransform = None, justifyBreaks = 0
    spaceShrinkage = 0.05, alignment = 0, borderColor = None,
    splitLongWords = 1, leading = 12, bulletIndent = 0,
    allowOrphans = 0, bulletFontSize = 10, fontSize = 10,
    borderWidth = 0, bulletAnchor = start, borderPadding = 0,
    endDots = None, textColor = Color(0,0,0,1), spaceAfter = 0
    """
    # https://www.blog.pythonlibrary.org/2010/03/08/a-simple-step-by-step-reportlab-tutorial/
    # this is the book now.
    story = []
    page_number = 0
    for pg in book:
        page_number += 1
        # setup style
        page_style = ParagraphStyle("page" + str(page_number))
        for style in pg.style:
            for cmd in style:
                if cmd == supportedStyles[0]:  # font: (size px) (face)
                if cmd == supportedStyles[1]:  # background-color: (rgb)
                if cmd == supportedStyles[2]:  # rotate (degrees)
                if cmd == supportedStyles[3]:  # margin (top) (right) (bottom) (left)
        # content
        for key in pg.content:
            if key == "img":
                # Image("lj8100.jpg", width=2*inch, height=2*inch)
                story.append(Image(pg.content["img"]))
            elif key == "text":
                story.append(Paragraph(pg.content["text"], page_style))

        story.append(PageBreak())

    return book


def writer(title, paragraphs):
    filename = title + '.pdf'
    margin = 18
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter),
                            rightMargin=margin, leftMargin=margin,
                            topMargin=margin, bottomMargin=margin)
    """
    for pg in paragraphs:
        # setup style
        for style in pg.style:
            for cmd in style:
                if cmd == supportedStyles[0]:  # font: (size px) (face)
                    print(style[cmd][1], int(style[cmd][0]))
                    c.setFont(style[cmd][1], int(style[cmd][0]))
                if cmd == supportedStyles[1]:  # background-color: (rgb)
                    # must find out what this will take, rgb, plaintext, hex ...
                    print(style[cmd])
                    c.setFillColor(style[cmd])
                if cmd == supportedStyles[2]:  # rotate (degrees)
                    print(int(style[cmd]))
                    c.rotate(int(style[cmd]))
                if cmd == supportedStyles[3]:  # margin (x) (y)
                    # want to support inch & cm here
                    print(style[cmd][0], style[cmd][1])
                    c.translate(int(style[cmd][0]) * inch, int(style[cmd][1]) * inch)
        # content
        for key in pg.content:
            if key == "img":
                content_img = ImageReader(pg.content["img"])
                c.drawImage(content_img, 10, 10, mask="auto")
            elif key == "text":
                c.drawString(10, 10, pg.content["text"])
        # ends page
        c.showPage()
    print("writing to file: ", title, ".pdf")
    c.save()
    """


class Page:
    def __init__(self, content, style):
        self.content = content
        self.style = style

    def __eq__(self, other):
        if self.content == other.content:
            if self.style == other.style:
                return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("supported styles: ", supportedStyles)
        else:
            reader(sys.argv[1])
    else:
        reader("book.json")
