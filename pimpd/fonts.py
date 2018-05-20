from PIL import ImageFont
import os.path

if os.path.exists('Arial.ttf'):
    DEFAULT_FONT = 'Arial.ttf'
else:
    DEFAULT_FONT = 'DejaVuSans.ttf'
DEFAULT_FONT_12 = ImageFont.truetype(DEFAULT_FONT, 12)
DEFAULT_FONT_14 = ImageFont.truetype(DEFAULT_FONT, 14)

#DEFAULT_FONT = 'NotoSans-Regular.ttf'
#DEFAULT_FONT_12 = ImageFont.truetype(DEFAULT_FONT, 11)
#DEFAULT_FONT_14 = ImageFont.truetype(DEFAULT_FONT, 13)
