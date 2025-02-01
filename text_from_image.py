import PIL.ImageDraw
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# Open the image file
image = Image.open('faktura.png')

# Perform OCR using PyTesseract
#text = pytesseract.image_to_string(image, lang = 'pol')
data = pytesseract.image_to_data(image, lang='pol', output_type=pytesseract.Output.DICT)
# Print the extracted text
#print(text)
print(data)
blocks = dict()
for i in range(len(data["block_num"])):
    block_id = data["block_num"][i]
    if block_id in blocks:
        blocks[block_id].append(data["text"][i])
    else:
        blocks[block_id] = [data["text"][i]]
print(blocks)

n_boxes = len(data['level'])
for i in range(n_boxes):
    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    draw = PIL.ImageDraw.Draw(image)
    draw.rectangle(xy=(x, y, x + w, y + h), outline=(0, i, 0), width=1)

image.show()