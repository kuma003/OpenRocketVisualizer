"""font.py"""

import os

import pygame as pg
import requests


class Fonts:
    """
    Font manager class.

    Attributes:
        font_list (dict[str, str]): the dictionary of fonts that can be used in the game. The key is the name of the font, and the value is the github URL of the font file. you can add more fonts to the font_list by adding the font name and the URL of the font file.
    """

    font_list = {
        "ZenKakuGothic": "https://github.com/googlefonts/zen-kakugothic/raw/refs/heads/main/fonts/ttf/ZenKakuGothicAntique-Medium.ttf",
        "oswald": "https://github.com/vernnobile/OswaldFont/raw/refs/heads/master/3.0/Roman/400/Oswald-Regular.ttf",
        "sawarabi": "https://github.com/google/fonts/raw/refs/heads/main/ofl/sawarabigothic/SawarabiGothic-Regular.ttf",
        "r_Mplus_regular": "https://github.com/google/fonts/raw/refs/heads/main/ofl/roundedmplus1c/RoundedMplus1c-Regular.ttf",
        "r_Mplus_medium": "https://github.com/google/fonts/raw/refs/heads/main/ofl/roundedmplus1c/RoundedMplus1c-Medium.ttf",
    }

    __FONT_DIR = "./fonts"

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the fonts. This method should be called before using the fonts.
        """
        pg.font.init()

    @classmethod
    def get_font(cls, font_name: str, font_size: int = 32) -> pg.font.Font:
        """
        Get the font object by the font name.

        Args:
            font_name (str): the name of the font.
            font_size (int): the size of the font.

        Returns:
            pg.font.Font: the font object.
        """
        if os.path.exists(os.path.join(cls.__FONT_DIR, f"{font_name}.ttf")):
            return pg.font.Font(
                os.path.join(cls.__FONT_DIR, f"{font_name}.ttf"), font_size
            )
        else:
            print(
                f"Font {font_name} is not found. Make sure you have downloaded the font via 'download_fonts'."
            )
            return None

    @classmethod
    def download_fonts(cls):
        """
        Download the fonts. This method downloads the fonts from the internet and saves them in the "./fonts" directory.
        """
        print("Verifying fonts...")
        os.makedirs(cls.__FONT_DIR, exist_ok=True)
        for font_name, font_url in cls.font_list.items():
            if os.path.exists(os.path.join(cls.__FONT_DIR, f"{font_name}.ttf")):
                # no need to download the font if it's already downloaded
                print(f"{font_name} is already downloaded.")
                continue
            print(f"{font_name} is not found. Downloading...", end="")
            # download font
            response = requests.get(font_url)
            save_path = os.path.join("fonts", f"{font_name}.ttf")
            with open(save_path, "wb") as file:
                if response.status_code == 200:
                    file.write(response.content)
                    print("Done.")
                else:
                    print("Failed (status code: {response.status_code}).")
                    continue
        print("All fonts are ready.")


Fonts.initialize()  # initialize the fonts
Fonts.download_fonts()  # download the fonts

if __name__ == "__main__":
    print(Fonts.get_font("ZenMaruGothic"))
