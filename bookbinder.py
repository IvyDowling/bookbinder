import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape


def reader(title):
    with open(title) as data_file:
        data = json.load(data_file)

    #document has style obj and pages array
    style = data["style"]
    pages = data["pages"]
    book = []
    for p in pages:
        page_style = [style if p is {} else ]
        book.append(Page(p["content"], page_style))
        print(p["content"])


def writer(title, book):
    filename = title + '.pdf'
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    #c.setFont()
    #c.drawString(x,y,text)
    c.showPage()
    print("writing to file: ", title, ".pdf")
    c.save()


class Page:
    def __init__(self, content, style):
        self.content = content
        self.style = style

if __name__ == "__main__":
    if len(sys.argv) is 2:
        reader(sys.argv[1])
    else:
        reader("book.json")
