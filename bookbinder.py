import json
import sys
import os
from collections import OrderedDict
from reportlab.pdfgen import canvas
# from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

supportedStyles = [
    "font",
    "background-color",
    "rotate",
    "margin"
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
    writer(filename.rsplit(".", 1)[0], book)


def writer(title, book):
    filename = title + '.pdf'
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    for pg in book:
        # setup style
        for style in pg.style:
            """
            canvas.setFont(fontname, size)
            canvas.getAvailableFonts()
            canvas.setFillColor(red)
            canvas.rotate(theta)
            """
            for cmd in style:
                if cmd is supportedStyles[0]:  # font: (size px) (face)
                    c.setFont(style[cmd][1], style[cmd][0])
                if cmd is supportedStyles[1]:  # background-color: (rgb)
                    c.setFillColor(style[cmd])
                if cmd is supportedStyles[2]:  # rotate (degrees)
                    c.rotate(style[cmd])
                if cmd is supportedStyles[3]:  # margin (x) (y)
                    c.translate(style[cmd][0], style[cmd][1])
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
