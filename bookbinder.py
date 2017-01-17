import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape


supportedStyles = [
    "font",
    "background-color",
    "rotate",
    "margin"
]

def reader(title):
    with open(title) as data_file:
        data = json.load(data_file)

    #document has style obj and pages obj
    style = data["style"]
    pages = data["pages"]
    page_style = [style if p is {} else inheritGlobalStyle(style,p)]
    print(page_style)
    book = []
    for p in pages:
        book.append(Page(p["content"], page_style))


def writer(title, book):
    filename = title + '.pdf'
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    for pg in book:
        #setup style
        for style in pg.style:
            css_to_reportlab(c, style)

        #content
        for cont in pg.content:

        #ends page
        c.showPage()
    print("writing to file: ", title, ".pdf")
    c.save()


def inheritGlobalStyle(glob, loc):
    for key in vars(newStyle).keys():
        glob[key] = newStyle[key]


def css_to_reportlab(canvas, css):
    #c.setFont(psfontname, size)
    #canvas.getAvailableFonts()
    #c.drawString(x,y,text)
    #c.setFillColor(red)
    #canvas.rotate(theta)
    if css is supportedStyles[0]: #font: (size px) (face)
    if css is supportedStyles[1]: #background-color: (rgb)
    if css is supportedStyles[2]: #rotate (degrees)
    if css is supportedStyles[3]: #margin (top) (right) (bottom) (left) 


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
    if len(sys.argv) is 2:
        if(sys.argv[1] is "--help" or sys.argv[1] is "-h"):
            print("supported styles: ", supportedStyles)
        else:
            reader(sys.argv[1])
    else:
        reader("book.json")
