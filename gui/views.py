# gui/views.py
import arcade
from models.character import Character

class BattleView(arcade.View):
    def __init__(self, player1: Character, player2: Character):
        super().__init__()
        self.player1 = player1
        self.player2 = player2

        # Menyimpan pesan log pertempuran
        self.battle_log = "Pertempuran Dimulai!"

    def on_show_view(self):
        """Dipanggil sekali saat View ini mulai ditampilkan di window."""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        """Dipanggil setiap frame untuk menggambar objek ke layar."""
        self.clear() # Membersihkan layar sebelum menggambar frame baru

        # Mendapatkan ukuran layar saat ini
        screen_width = self.window.width
        screen_height = self.window.height

        # ==========================================
        # MENGGAMBAR STATUS PLAYER 1 (KIRI)
        # ==========================================
        arcade.Text(
            self.player1.name, 
            x=50, y=screen_height - 50, 
            color=arcade.color.WHITE, font_size=20, bold=True
        ).draw()
        
        arcade.Text(
            f"HP: {self.player1.current_hp} / {self.player1._max_hp}", 
            x=50, y=screen_height - 80, 
            color=arcade.color.LIGHT_GREEN, font_size=14
        ).draw()
        
        arcade.Text(
            f"Mana: {self.player1.current_mana} / {self.player1._max_mana}", 
            x=50, y=screen_height - 100, 
            color=arcade.color.LIGHT_BLUE, font_size=14
        ).draw()

        # ==========================================
        # MENGGAMBAR STATUS PLAYER 2 (KANAN)
        # ==========================================
        arcade.Text(
            self.player2.name, 
            x=screen_width - 250, y=screen_height - 50, 
            color=arcade.color.WHITE, font_size=20, bold=True
        ).draw()
        
        arcade.Text(
            f"HP: {self.player2.current_hp} / {self.player2._max_hp}", 
            x=screen_width - 250, y=screen_height - 80, 
            color=arcade.color.LIGHT_GREEN, font_size=14
        ).draw()
        
        arcade.Text(
            f"Mana: {self.player2.current_mana} / {self.player2._max_mana}", 
            x=screen_width - 250, y=screen_height - 100, 
            color=arcade.color.LIGHT_BLUE, font_size=14
        ).draw()

        # ==========================================
        # MENGGAMBAR LOG PERTEMPURAN (TENGAH BAWAH)
        # ==========================================
        arcade.Text(
            self.battle_log,
            x=screen_width // 2, y=150,
            color=arcade.color.YELLOW, font_size=16,
            anchor_x="center", anchor_y="center"
        ).draw()