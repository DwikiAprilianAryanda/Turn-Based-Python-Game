# main.py
import arcade
from gui.views import MainMenuView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "OOP Turn-Based Game"

if __name__ == "__main__":
    # Membuat Window aplikasi GUI
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Memulai game langsung dari Main Menu
    menu_view = MainMenuView()
    window.show_view(menu_view)

    # Menjalankan Game Loop
    arcade.run()