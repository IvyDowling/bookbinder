import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


supportedStyles = [
    "font",
    "background-color",
    "rotate",
    "margin"
]


def reader(title):
    with open(title) as data_file:
        data = json.load(data_file)

    # document has style obj and pages obj
    global_style = data["style"]
    page_style = []
    for p in data["pages"]:
        inhrt = global_style.copy()
        for key, value in p["style"].iteritems():
            inhrt[key] = value
        page_style.append(inhrt)
    book = []
    for p in data["pages"]:
        book.append(Page(p["content"], page_style))


def writer(title, book):
    filename = title + '.pdf'
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    for pg in book:
        # setup style
        for style in pg.style:
            print(style)
            css_to_reportlab(c, style)

        # content
        for cont in pg.content:
            print(cont)

        # ends page
        c.showPage()
    print("writing to file: ", title, ".pdf")
    c.save()


def css_to_reportlab(canvas, css):
    # c.setFont(fontname, size)
    # canvas.getAvailableFonts()
    # c.drawString(x,y,text)
    # c.setFillColor(red)
    # canvas.rotate(theta)
    if css is supportedStyles[0]: # font: (size px) (face)
        print(css)
    if css is supportedStyles[1]: # background-color: (rgb)
        print(css)
    if css is supportedStyles[2]: # rotate (degrees)
        print(css)
    if css is supportedStyles[3]: # margin (top) (right) (bottom) (left)
        print(css)


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
