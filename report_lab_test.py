from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def table_fonts():
    doc = SimpleDocTemplate("table_fonts.pdf", pagesize=letter)
    story = []
    data = [["xd","xd","adsf","ddd"], ["asdf","ś", "ż", "a"]]
    tblstyle = TableStyle([('FONT', (0, 0), (-1, -1), 'FreeSans')])
    tblstyle.add("GRID", (0,0), (-1,-1), 0.5, colors.black)
    tbl = Table(data)
    tbl.setStyle(tblstyle)
    story.append(tbl)
    doc.build(story)

class PDF_Generator:
    def __init__(self):
        self.story = []
        tblstyle = TableStyle([('FONT', (0, 0), (-1, -1), 'FreeSans')])
        tblstyle.add("GRID", (0,0), (-1,-1), 0.5, colors.black)
        self.tblstyle = tblstyle
    
    def add_table(self, data):
        tbl = Table(data)
        tbl.setStyle(self.tblstyle)
        self.story.append(tbl)
    
    def build(self, file_name:str):
        doc = SimpleDocTemplate(filename = file_name, pagesize = letter)
        doc.build(self.story)

if __name__ == '__main__':
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf')) 
    generator = PDF_Generator()
    generator.add_table([["xd","xd","adsf","ddd"], ["asdf","ś", "ż", "a"]])
    generator.build("table_text.pdf")
    #table_fonts()