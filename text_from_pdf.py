from pypdf import PdfReader

reader = PdfReader("208.2024 WM Gęsickiego 1.pdf")
a = reader.pages[0]
print(reader.pages[0].get_contents())