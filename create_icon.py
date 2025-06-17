from PIL import Image, ImageDraw, ImageFont
import os

def create_search_icon():
    # Create a new image with a transparent background
    size = (256, 256)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a magnifying glass
    # Circle
    circle_bbox = (40, 40, 180, 180)
    draw.ellipse(circle_bbox, outline=(26, 26, 46, 255), width=20, fill=(15, 52, 96, 255))
    
    # Handle
    draw.line((160, 160, 216, 216), fill=(26, 26, 46, 255), width=20)
    
    # Save as ICO
    image.save('search_widget.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

if __name__ == '__main__':
    create_search_icon() 