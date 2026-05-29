# main.py
import arcade
from gui.views import MainMenuView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "OOP Turn-Based Game"

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # biar Main Menu dulu yang muncul
    menu_view = MainMenuView()
    window.show_view(menu_view)

    arcade.run()