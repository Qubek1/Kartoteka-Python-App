from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

class PDF_Generator:
    def __init__(self):
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf')) 
        self.story = []
        tblstyle = TableStyle([('FONT', (0, 0), (-1, -1), 'FreeSans')])
        tblstyle.add("GRID", (0,0), (-1,-1), 0.5, colors.black)
        prstyle = ParagraphStyle(name="Default", fontName="FreeSans", fontSize=12)
        self.tblstyle = tblstyle
        self.prstyle = prstyle
    
    def add_table(self, data):
        tbl = Table(data)
        tbl.setStyle(self.tblstyle)
        self.story.append(tbl)

    def add_text(self, text:str):
        t = Paragraph(text, style=self.prstyle)
        self.story.append(t)

    def add_spacer(self, size:float):
        space = Spacer(width=1, height=size)
        self.story.append(space)
    
    def build(self, file_name:str):
        doc = SimpleDocTemplate(filename = file_name, pagesize = letter, leftMargin = 40, rightMargin = 40, topMargin = 40, bottomMargin = 0)
        doc.build(self.story)
