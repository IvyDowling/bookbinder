import json
import sys
import os
from collections import OrderedDict
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.graphics.shapes import Rect, Drawing
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch, cm

supportedStyles = [
    "font",
    "background-color",
    "margin",
    "margin-top",
    "margin-right",
    "margin-bottom",
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

    filename = filename.rsplit(".", 1)[0] + '.pdf'
    doc = BaseDocTemplate(filename, pagesize=landscape(letter),
                          rightMargin=0, leftMargin=0,
                          topMargin=0, bottomMargin=0)
    paragraphs = translate(doc, book)
    writer(doc, paragraphs)


def translate(doc, book):
    """
    :param book: List of content and style tuples for each pages
    :param doc: DocTemplate
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
    # this is the book
    story = []
    page_number = 0
    for pg in book:
        page_number += 1
        # setup style
        page_style = ParagraphStyle("page" + str(page_number))
        for style in pg.style:
            for cmd in style:
                if cmd == supportedStyles[0]:  # font: (size) (face)
                    page_style.fontName = int(style[cmd][1])
                    page_style.fontSize = int(style[cmd][0])
                elif cmd == supportedStyles[1]:  # background-color: (rgb)
                    # This is actually broken and dumb
                    # you just make a huge rectangle behind everything else here.
                    print("GET LANDSCAPE PAGE VALUES")
                    draw = Drawing(200, 200)
                    draw.add(Rect(0, 0, 200, 200,
                                  fillColor=style[cmd][0],
                                  strokeColor=style[cmd][0],
                                  strokeWidth=0))
                    story.append(draw)
                # http://code.activestate.com/recipes/123612-basedoctemplate-with-2-pagetemplate/
                # This shows PageTemplate and a function to use canvas
                # functions to alter a page
                elif cmd == supportedStyles[2]: # margin (top) (right) (bottom) (left)
                    PageTemplate()
                elif cmd == supportedStyles[3]: # margin-top
                    PageTemplate()
                elif cmd == supportedStyles[4]: # margin-right
                    PageTemplate()
                elif cmd == supportedStyles[5]: # margin-bottom
                    PageTemplate()
                elif cmd == supportedStyles[6]: # margin-left
                    PageTemplate()
        # content
        for key in pg.content:
            if key == "img":
                # Image("lj8100.jpg", width=2*inch, height=2*inch)
                story.append(Image(pg.content["img"]))
            elif key == "text":
                story.append(Paragraph(pg.content["text"], page_style))

        story.append(PageBreak())

    return book


def writer(doc, paragraphs):
    left = Frame(doc.leftMargin, doc.bottomMargin, doc.width / 2 - 6, doc.height, id='col1')
    right = Frame(doc.leftMargin + doc.width / 2 + 6, doc.bottomMargin, doc.width / 2 - 6,
                   doc.height, id='col2')
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
    doc.build(paragraphs)


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
