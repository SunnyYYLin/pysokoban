import requests
from bs4 import BeautifulSoup
import os
import re

class SokobanLevelScraper:
    def __init__(self, url, output_dir='levels'):
        self.url = url
        self.output_dir = output_dir
        self.img_to_char = {
            "p_wall.gif": '#',
            "p_goal.gif": '.',
            "p_box.gif": '$',
            "p_player.gif": '@',
            "p_box_on_goal.gif": '+',
            "p_player_on_goal.gif": '-',
            "p_floor.gif": ' '
        }

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def fetch_page(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    def find_levels(self, content):
        soup = BeautifulSoup(content, "lxml")
        paragraphs = soup.find_all("p")
        paragraphs = [p for p in paragraphs if not p.find("p")]
        
        level_pattern = re.compile(r"^关数: (\d+)")
        for i in range(len(paragraphs) - 1):
            p = paragraphs[i]
            if level_pattern.match(p.text):
                level_number = int(level_pattern.match(p.text).group(1))
                p = paragraphs[i + 1]
                i += 1
                level_matrix = self.parse_level(str(p))
                yield level_number, level_matrix
    
    def parse_level(self, paragraph):
        rows = paragraph.split("<br/>")
        level_matrix = []
        for row in rows:
            soup_row = BeautifulSoup(row, "html.parser")
            img_tags = soup_row.find_all("img")
            row_str = ""
            for img in img_tags:
                img_src = img["src"]
                row_str += self.img_to_char.get(img_src, "?")
            if row_str:
                level_matrix.append(row_str)
        return level_matrix

    def save_levels(self, levels):
        for level_number, level_matrix in levels:
            filename = os.path.join(self.output_dir, f"level{level_number}.txt")
            with open(filename, "w") as file:
                file.write("\n".join(level_matrix))
            print(f"Level {level_number} saved to {filename}")

    def run(self):
        content = self.fetch_page()
        levels = self.find_levels(content)
        self.save_levels(levels)

if __name__ == "__main__":
    url = "https://sokoban.cn/utility/levelset.php?set=box_it"
    scraper = SokobanLevelScraper(url)
    scraper.run()
