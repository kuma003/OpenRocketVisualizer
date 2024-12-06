import requests
import os

def download_font(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs("./fonts", exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {save_path}")
    else:
        print(f"Failed to download {url}")

def main():
    fonts = {
        "Roboto": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Italic%5Bwght%5D.ttf",
        # "OpenSans": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf"
    }

    for font_name, font_url in fonts.items():
        save_path = f"./fonts/{font_name}.ttf"
        download_font(font_url, save_path)

if __name__ == "__main__":
    main()