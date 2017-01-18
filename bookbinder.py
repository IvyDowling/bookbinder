import json
import sys
import os
from collections import OrderedDict
from reportlab.pdfgen import canvas
# from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch, cm

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
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = letter
    for pg in book:
        # setup style
        for style in pg.style:
            """
            canvas.getAvailableFonts()
            """
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
