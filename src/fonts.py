"""font."""
import requests
import os
import pygame as pg

class Fonts:
    """
        Font manager class. This class manages the fonts used in the game.

        Attributes:
            font_list (dict[str, str]): the dictionary of fonts that can be used in the game. The key is the name of the font, and the value is the github URL of the font file. you can add more fonts to the font_list by adding the font name and the URL of the font file.
    """
    font_list = {
        "ZenMaruGothic": "https://github.com/googlefonts/zen-marugothic/blob/main/fonts/ttf/ZenMaruGothic-Regular.ttf",
    }
    
    __fonts : dict[str, pg.font.Font] = {}
    
    @classmethod
    def initialize(cls) -> None:
        """
            Initialize the fonts. This method should be called before using the fonts.
        """
        pg.font.init() 
    
    @classmethod
    def get_font(cls, font_name : str):
        """
            Get the font object by the font name.

            Args:
                font_name (str): the name of the font.

            Returns:
                pg.font.Font: the font object.
        """
        return cls.__fonts.get(font_name)
    
    @classmethod
    def download_fonts(cls):
        """
            Download the fonts. This method downloads the fonts from the internet and saves them in the "./fonts" directory.
        """
        os.makedirs("./fonts", exist_ok=True)
        for font_name, font_url in cls.font_list.items():
            if font_name in cls.__fonts:
                # no need to download the font if it's already downloaded
                continue
            
            # download font
            response = requests.get(font_url)
            save_path = os.path.join("fonts", f"{font_name}.ttf")
            with open(save_path, 'wb') as file:
                if response.status_code == 200:
                    file.write(response.content)
                    print(f"Downloaded {font_name}")
                else:
                    print(f"Failed to download {font_name}")
                    continue
            cls.__fonts[font_name] = pg.font.Font(save_path, 32)

Fonts.initialize() # initialize the fonts

if __name__ == "__main__":
    Fonts.download_fonts()
    print(Fonts.get_font("ZenMaruGothic"))