# main.py
import arcade
from models.emperor import Emperor
from models.gladiator import Gladiator
from gui.views import BattleView

# Konstanta untuk ukuran Window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "OOP Turn-Based Game"

if __name__ == "__main__":
    # 1. Inisialisasi Karakter (Model)
    p1 = Emperor("Qin Shi Huang")
    p2 = Gladiator("Spartacus")

    # 2. Membuat Window aplikasi GUI
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # 3. Menginisialisasi View pertempuran dan memasukkannya ke Window
    battle_view = BattleView(p1, p2)
    window.show_view(battle_view)

    # 4. Menjalankan Game Loop bawaan Arcade
    arcade.run()