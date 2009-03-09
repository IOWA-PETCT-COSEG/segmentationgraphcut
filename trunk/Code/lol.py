import Image
im = Image.open("E-VTT-pre-2.jpg")
im.convert("L").save("image.bmp")