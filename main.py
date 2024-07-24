import argparse
import logging
from datetime import datetime
import os
import pygame
import numpy as np
from game.game import Game

def main():
    parser = argparse.ArgumentParser(description="Sokoban Game")
    parser.add_argument("--test", action="store_true", help="Run the game in test mode")
    parser.add_argument("--level", type=int, default=1, help="Specify the starting level")
    parser.add_argument("--log-file", type=str, default="sokoban.log", help="Specify the log file")
    parser.add_argument("--icon-style", type=str, default="images_v1", help="Specify the icon style")
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
    game = Game(lvl_num=args.level, icon_style=args.icon_style)
    if args.test:
        game.test(b_weights=[1, 10, 100, 1000, np.inf])
    else:
        game.run()

if __name__ == "__main__":
    main()