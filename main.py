import pygame
import argparse
from game.game import Game
import logging
from datetime import datetime
import os

def main():
    parser = argparse.ArgumentParser(description="Sokoban Game")
    parser.add_argument("--test", action="store_true", help="Run the game in test mode")
    parser.add_argument("--level", type=int, default=1, help="Specify the starting level")
    parser.add_argument("--log-file", type=str, default="sokoban.log", help="Specify the log file")
    parser.add_argument("--icon-style", type=str, default="image_v1", help="Specify the icon style")
    args = parser.parse_args()
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    log_filename = datetime.now().strftime(os.path.join("logs","sokoban_%Y%m%d_%H%M%S.log"))
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(log_filename),
                            logging.StreamHandler()
                        ])
    pygame.init()
    game = Game(args.level, args.icon_style)
    if args.test:
        game.test()
    else:
        game.run()

if __name__ == "__main__":
    main()