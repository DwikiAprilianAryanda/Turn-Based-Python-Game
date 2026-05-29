# gui/widgets.py
import arcade

class StatusBar:
    def __init__(self, character, x, y, width, height, is_mana=False):
        self.character = character
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_mana = is_mana
        
        # Simpan nilai untuk animasi (Tweening)
        max_val = self.character._max_mana if self.is_mana else self.character._max_hp
        current_val = self.character.current_mana if self.is_mana else self.character.current_hp
        self.displayed_val = float(current_val)

    def update(self, delta_time):
        """Memperbarui nilai animasi secara halus (Tweening)"""
        target_val = self.character.current_mana if self.is_mana else self.character.current_hp
        speed = 5.0 * delta_time
        
        if self.displayed_val > target_val:
            self.displayed_val -= (self.displayed_val - target_val) * speed
            if self.displayed_val - target_val < 0.5:
                self.displayed_val = target_val
        elif self.displayed_val < target_val:
            self.displayed_val += (target_val - self.displayed_val) * speed
            if target_val - self.displayed_val < 0.5:
                self.displayed_val = target_val

    # --- HELPER AMAN UNTUK ARCADE 3.0 ---
    def _draw_rect(self, center_x, center_y, width, height, color):
        hw = width / 2
        hh = height / 2
        points = (
            (center_x - hw, center_y - hh),
            (center_x + hw, center_y - hh),
            (center_x + hw, center_y + hh),
            (center_x - hw, center_y + hh)
        )
        arcade.draw_polygon_filled(points, color)

    def _draw_outline(self, center_x, center_y, width, height, color, line_width):
        hw = width / 2
        hh = height / 2
        points = (
            (center_x - hw, center_y - hh),
            (center_x + hw, center_y - hh),
            (center_x + hw, center_y + hh),
            (center_x - hw, center_y + hh)
        )
        arcade.draw_polygon_outline(points, color, line_width=line_width)

    def draw(self):
        max_val = self.character._max_mana if self.is_mana else self.character._max_hp
        actual_val = self.character.current_mana if self.is_mana else self.character.current_hp
        
        if max_val <= 0: return

        # 1. Background Bar (Gelap)
        self._draw_rect(self.x, self.y, self.width, self.height, arcade.color.DARK_GRAY)

        tween_ratio = max(0, min(1, self.displayed_val / max_val))
        tween_width = self.width * tween_ratio
        
        actual_ratio = max(0, min(1, actual_val / max_val))
        actual_width = self.width * actual_ratio

        # 2. Gambar Efek Animasi
        if tween_width > 0:
            if self.displayed_val > actual_val:
                self._draw_rect(self.x - self.width/2 + tween_width/2, self.y, tween_width, self.height, arcade.color.YELLOW)
            elif self.displayed_val < actual_val:
                self._draw_rect(self.x - self.width/2 + actual_width/2, self.y, actual_width, self.height, arcade.color.LIGHT_GREEN)

        # 3. Gambar Bar Aktual
        if actual_width > 0:
            main_color = arcade.color.BLUE if self.is_mana else arcade.color.RED
            draw_width = actual_width if self.displayed_val > actual_val else tween_width
            self._draw_rect(self.x - self.width/2 + draw_width/2, self.y, draw_width, self.height, main_color)

        # 4. Outline Bar & Teks
        self._draw_outline(self.x, self.y, self.width, self.height, arcade.color.WHITE, line_width=2)
        text = f"{int(actual_val)}/{int(max_val)}"
        arcade.draw_text(text, self.x, self.y, arcade.color.WHITE, font_size=10, anchor_x="center", anchor_y="center", bold=True)

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