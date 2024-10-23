import os
from PIL import Image

im = Image.open("./preview.png")

card_width, card_height = 160, 224
tile_width, tile_height = 192, 264
tile_x, tile_y = 32, 32

if not os.path.exists("./.out"):
    os.makedirs("./.out")

suits = ["S", "H", "C", "D", "J"]

for row in range(5):
    for col in range(13):
        left = tile_x + col * tile_width
        top = tile_y + row * tile_height
        im_cropped = im.crop((left, top, left + card_width, top + card_height))
        im_cropped.save(f".out/{suits[row]}{col+1}.png")
