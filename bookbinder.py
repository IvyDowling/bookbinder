import json
import sys
import os
from collections import OrderedDict
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, \
    Frame, Paragraph, Spacer, Image, PageBreak, NextPageTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import Color, HexColor
from reportlab.graphics.shapes import Rect, Drawing
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

marginCommands = [
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
    templates = []
    page_number = 0
    for pg in book:
        page_number += 1
        # MARGINS
        # pre-build frame bc we need one either way
        # frame takes height & width, not top and right
        frame = Frame(doc.leftMargin* cm, doc.bottomMargin* cm,
                      (doc.width/2) * cm, (doc.height) * cm, id='p' + str(page_number))
        for mrgn in pg.style:
            if mrgn == supportedStyles[2]:  # margin (top) (right) (bottom) (left)
                frame = Frame(int(style[cmd][3])* cm, int(style[cmd][2])* cm,
                          (doc.width/2) - int(style[cmd][1])* cm,
                          doc.height - int(style[cmd][0])* cm,
                          id='p' + str(page_number))
            elif mrgn == supportedStyles[3]:  # margin-top
                frame.height = doc.height - int(style[cmd][0]) * cm
            elif mrgn == supportedStyles[4]:  # margin-right
                frame.width = (doc.width/2) - int(style[cmd][1]) * cm
            elif mrgn == supportedStyles[5]:  # margin-bottom
                frame.y1 = int(style[cmd][2]) * cm
            elif mrgn == supportedStyles[6]:  # margin-left
                frame.x1 = int(style[cmd][3]) * cm
        # STYLE
        page_style = ParagraphStyle("page" + str(page_number))
        for style in pg.style:
            for cmd in style:
                if cmd == supportedStyles[0]:  # font: (size) (face)
                    page_style.fontName = style[cmd][1]
                    page_style.fontSize = int(style[cmd][0])
                elif cmd == supportedStyles[1]:  # background-color: [r, g, b] or hex
                    # This is actually broken and dumb
                    # you just make a huge rectangle
                    draw = Drawing(doc.width/2, doc.height)
                    if len(style[cmd]) == 6:
                        # hex
                        color = HexColor('0x' + style[cmd][0])
                    else:
                        # rgb values in report lab take 0-1, import 0-255
                        r = float(style[cmd][0])/255
                        g = float(style[cmd][1])/255
                        b = float(style[cmd][2])/255
                        color = Color(r, g, b)

                    draw.add(Rect(0 * cm, 0 * cm, (doc.width/2) * cm, doc.height * cm,
                                  fillColor=color,
                                  strokeColor=color,
                                  strokeWidth=0))
                    story.append(draw)
        # CREATE PAGE TEMPLATE
        templates.append(PageTemplate(
            id='pt'+str(page_number),
            frames=frame
        ))
        # CONTENT
        for key in pg.content:
            if key == "img":
                story.append(Image(pg.content["img"][0],
                                   int(pg.content["img"][1]) * cm,
                                   int(pg.content["img"][2]) * cm))
            elif key == "text":
                story.append(Paragraph(pg.content["text"], page_style))

        # story.append(NextPageTemplate('pt'+str(page_number+1)))
        story.append(PageBreak())
    doc.addPageTemplates(templates)
    return story


def writer(doc, paragraphs):
    doc.build(paragraphs)


class Page:
    def __init__(self, content, style):
        self.content = content
        self.style = style


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("supported styles: ", supportedStyles)
        else:
            reader(sys.argv[1])
    else:
        reader("book.json")
