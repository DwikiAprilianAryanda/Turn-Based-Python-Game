# gui/widgets.py
import arcade
from models.character import Character

class StatusBar:
    """Class khusus untuk menggambar Bar HP atau Bar Mana (Single Responsibility Principle)"""
    def __init__(self, character: Character, x: int, y: int, width: int, height: int, is_mana: bool = False):
        self.character = character
        self.x = x # Koordinat kiri
        self.y = y # Koordinat bawah
        self.width = width
        self.height = height
        self.is_mana = is_mana

    def draw(self):
        # Tentukan nilai dan warna berdasarkan tipe bar (HP atau Mana)
        current_val = self.character.current_mana if self.is_mana else self.character.current_hp
        max_val = self.character._max_mana if self.is_mana else self.character._max_hp
        
        bg_color = arcade.color.DARK_BLUE if self.is_mana else arcade.color.DARK_RED
        fg_color = arcade.color.LIGHT_BLUE if self.is_mana else arcade.color.LIGHT_GREEN
        
        # Hitung persentase isi bar
        ratio = max(current_val / max_val, 0)
        current_width = self.width * ratio

# 1. Gambar Background Bar (Warna Gelap / Kosong)
        arcade.draw_lrbt_rectangle_filled(
            left=self.x,
            right=self.x + self.width,
            bottom=self.y,
            top=self.y + self.height,
            color=bg_color
        )

        # 2. Gambar Foreground Bar (Warna Terang / Isi)
        if current_width > 0:
            arcade.draw_lrbt_rectangle_filled(
                left=self.x,
                right=self.x + current_width,
                bottom=self.y,
                top=self.y + self.height,
                color=fg_color
            )
        
        # 3. Tambahkan Teks Angka di tengah Bar
        arcade.Text(
            f"{current_val}/{max_val}",
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
            color=arcade.color.WHITE,
            font_size=12, bold=True,
            anchor_x="center", anchor_y="center"
        ).draw()

        # Tambahkan di bagian paling bawah gui/widgets.py

class FloatingText:
    """Kelas untuk membuat efek teks melayang yang bersih dan modern."""
    def __init__(self, text: str, x: int, y: int, color: tuple):
        self.text = text
        self.x = x
        self.y = y
        
        # Konversi warna ke format RGBA agar bisa dibuat transparan
        if len(color) == 3:
            self.color = [color[0], color[1], color[2], 255]
        else:
            self.color = list(color)
            
        self.text_obj = arcade.Text(
            self.text, self.x, self.y, tuple(self.color), 
            font_size=18, bold=True, anchor_x="center"
        )

    def update(self):
        self.y += 1.5       # Mengambang ke atas
        self.color[3] -= 5  # Mengurangi opacity (memudar)
        if self.color[3] < 0:
            self.color[3] = 0
            
        self.text_obj.y = self.y
        self.text_obj.color = tuple(self.color)

    def is_dead(self):
        return self.color[3] <= 0

    def draw(self):
        if self.color[3] > 0:
            self.text_obj.draw()