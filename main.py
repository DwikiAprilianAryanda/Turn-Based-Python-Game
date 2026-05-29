import arcade
from gui.views import MainMenuView

# Ubah ukuran layar menjadi format HD (16:9)
SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Epic Turn-Based Arena"

class GameWindow(arcade.Window):
    def __init__(self):
        # Tambahkan parameter resizable=True agar jendela bisa di-drag ujungnya
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

    def on_key_press(self, key, modifiers):
        """Mendeteksi tombol keyboard yang ditekan"""
        # Jika tombol F11 ditekan, ubah mode layar (Fullscreen / Windowed)
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            
            # Mendapatkan ukuran layar monitor asli saat fullscreen
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)

def main():
    window = GameWindow()
    menu_view = MainMenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()