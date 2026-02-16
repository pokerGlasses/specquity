from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

class PokerHUD:
    def __init__(self):
        # 0x3C is the default address for these Amazon OLEDs
        self.serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(self.serial)
        
        try:
            # Use a clean font. You can drop a .ttf file in your repo!
            self.font = ImageFont.truetype("arial.ttf", 12)
        except:
            self.font = ImageFont.load_default()

    def update(self, stage, cards, win_rate):
        with canvas(self.device) as draw:
            # Draw a border
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            
            # Text layout (x, y)
            draw.text((5, 5),  f"STAGE: {stage}", font=self.font, fill="white")
            draw.text((5, 20), f"HAND: {' '.join(cards)}", font=self.font, fill="white")
            
            # Make the win rate big and bold
            draw.text((5, 40), f"WIN: {win_rate:.1f}%", font=self.font, fill="white")

    def show_reset(self):
        with canvas(self.device) as draw:
            draw.text((20, 25), "READY: NEW HAND", font=self.font, fill="white")    