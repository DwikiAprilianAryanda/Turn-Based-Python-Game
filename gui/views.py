# gui/views.py
import arcade
import arcade.gui
import random
import os
import math
from models.character import Character
from gui.widgets import StatusBar, FloatingText
from engine.commands import BasicAttackCommand, SpecialSkillCommand, UseItemCommand
from models.item import HealthPotion
from engine.factory import CharacterFactory 
from engine.history_manager import HistoryManager
from engine.save_manager import SaveManager, DIFFICULTY_SETTINGS
from engine.gacha_system import GachaSystem

# ==========================================
# 1. LAYAR PEMILIHAN MODE (STANDARD VS ENDLESS)
# ==========================================
class ModeSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.build_ui()

    def build_ui(self):
        self.manager.clear()
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        
        title = arcade.gui.UILabel(text="PILIH JALUR PERTANDINGAN", font_size=32, bold=True, text_color=arcade.color.GOLD)
        v_box.add(title)
        v_box.add(arcade.gui.UILabel(text="", height=20))
        
        btn_standard = arcade.gui.UIFlatButton(text="⚔️ Standard Mode (1v1, 2v2, 3v3)", width=350, height=50)
        btn_standard.on_click = self.on_standard_click
        
        btn_endless = arcade.gui.UIFlatButton(text="♾️ Endless Tower (Wajib 3v3)", width=350, height=50)
        btn_endless.on_click = self.on_endless_click
        
        btn_back = arcade.gui.UIFlatButton(text="Kembali", width=350, height=50)
        btn_back.on_click = self.on_back_click
        
        v_box.add(btn_standard)
        v_box.add(btn_endless)
        v_box.add(btn_back)
        
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_standard_click(self, event):
        self.manager.disable()
        from gui.views import DifficultySelectionView 
        self.window.show_view(DifficultySelectionView(party_size=3)) 

    def on_endless_click(self, event):
        self.manager.disable()
        from gui.views import EndlessCharacterSelectionView
        self.window.show_view(EndlessCharacterSelectionView())

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()


# ==========================================
# 2. LAYAR MENU UTAMA
# ==========================================
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.build_ui()

    def build_ui(self):
        self.manager.clear()
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)

        title = arcade.gui.UILabel(text="EPIC TURN-BASED ARENA", font_size=36, bold=True, text_color=arcade.color.GOLD)
        v_box.add(title)
        v_box.add(arcade.gui.UILabel(text="", height=10))

        start_btn = arcade.gui.UIFlatButton(text="⚔️ Mulai Bermain", width=250, height=45)
        start_btn.on_click = self.on_start_click
        v_box.add(start_btn)
        
        inv_btn = arcade.gui.UIFlatButton(text="🎒 Inventory", width=250, height=45)
        inv_btn.on_click = self.on_inv_click
        v_box.add(inv_btn)

        gacha_btn = arcade.gui.UIFlatButton(text="🎁 Gacha Equipment", width=250, height=45)
        gacha_btn.on_click = self.on_gacha_click
        v_box.add(gacha_btn)
        
        hist_btn = arcade.gui.UIFlatButton(text="📜 Riwayat Pertandingan", width=250, height=45)
        hist_btn.on_click = self.on_hist_click
        v_box.add(hist_btn)

        quit_btn = arcade.gui.UIFlatButton(text="❌ Keluar", width=250, height=45)
        quit_btn.on_click = self.on_quit_click
        v_box.add(quit_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_start_click(self, event):
        self.manager.disable()
        # PASTIKAN memanggil ModeSelectionView, BUKAN DifficultySelectionView
        from gui.views import ModeSelectionView
        self.window.show_view(ModeSelectionView())

    def on_inv_click(self, event):
        self.manager.disable()
        from gui.views import InventoryView 
        self.window.show_view(InventoryView())

    def on_gacha_click(self, event):
        self.manager.disable()
        from gui.views import GachaView
        self.window.show_view(GachaView())
        
    def on_hist_click(self, event):
        self.manager.disable()
        from gui.views import HistoryView 
        self.window.show_view(HistoryView())

    def on_quit_click(self, event):
        arcade.exit()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# LAYAR GACHA (UPDATE: SPRITELIST FIX)
# ==========================================
class GachaView(arcade.View):
    def __init__(self):
        super().__init__()
        from engine.save_manager import SaveManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        self.state = "IDLE" 
        self.anim_timer = 0.0
        self.time_elapsed = 0.0
        
        self.pulled_item_name = ""
        self.pulled_item_stats = ""
        self.rarity_color = arcade.color.WHITE
        self.chest_scale = 1.0
        self.chest_shake_x = 0.0
        self.flash_alpha = 0
        self.error_msg = ""
        
        self.item_sprite = None
        # FIX ERROR: Siapkan wadah SpriteList
        self.sprite_list = arcade.SpriteList() 
        
        self.build_ui()

    def build_ui(self):
        from engine.save_manager import SaveManager
        self.manager.clear()
        
        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=100)
        back_btn.on_click = self.on_back_click
        anchor_tl = arcade.gui.UIAnchorLayout()
        anchor_tl.add(child=back_btn, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        
        self.v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        title = arcade.gui.UILabel(text="GACHA EQUIPMENT", font_size=28, bold=True, text_color=arcade.color.GOLD)
        
        current_gold = SaveManager.get_gold()
        gold_label = arcade.gui.UILabel(text=f"🪙 Gold Anda: {current_gold}", font_size=16, text_color=arcade.color.YELLOW)
        
        from engine.gacha_system import GachaSystem
        pull_btn = arcade.gui.UIFlatButton(text=f"✨ Tarik 1x ({GachaSystem.COST_PER_PULL} Gold)", width=250, height=50)
        pull_btn.on_click = self.on_pull_click
        
        self.v_box.add(title)
        self.v_box.add(gold_label)
        self.v_box.add(pull_btn)
        
        if self.error_msg:
            self.v_box.add(arcade.gui.UILabel(text=self.error_msg, font_size=14, text_color=arcade.color.RED, bold=True))
        
        anchor_center = arcade.gui.UIAnchorLayout()
        anchor_center.add(child=self.v_box, anchor_x="center", anchor_y="center")
        
        self.manager.add(anchor_tl)
        self.manager.add(anchor_center)

    def get_rarity_color(self, rarity):
        if rarity == "Mythic": return arcade.color.RED
        elif rarity == "Legendary": return arcade.color.GOLD
        elif rarity == "Rare": return arcade.color.LIGHT_GREEN
        else: return arcade.color.WHITE

    def on_pull_click(self, event):
        from engine.gacha_system import GachaSystem
        from engine.save_manager import SaveManager

        if not SaveManager.deduct_gold(GachaSystem.COST_PER_PULL):
            self.error_msg = "❌ Gold tidak cukup!"
            self.build_ui()
            return
            
        pulled_name, pulled_rarity = GachaSystem.pull_item()
        item_data = GachaSystem.ITEM_POOL[pulled_name]
        
        self.pulled_item_name = pulled_name
        self.pulled_item_stats = item_data.get("desc", "")
        self.rarity_color = self.get_rarity_color(pulled_rarity)
        
        import os
        img_path = item_data.get("img", "")
        if os.path.exists(img_path):
            self.item_sprite = arcade.Sprite(img_path, scale=2.0)
        else:
            self.item_sprite = arcade.SpriteSolidColor(width=100, height=100, color=self.rarity_color)
            
        # FIX ERROR: Masukkan gambar ke dalam SpriteList
        self.sprite_list.clear()
        self.sprite_list.append(self.item_sprite)
        
        SaveManager.add_equipment(self.pulled_item_name)
        
        self.manager.clear() 
        self.state = "SHAKING"
        self.anim_timer = 2.0 
        self.chest_scale = 1.0
        self.error_msg = ""

    def on_back_click(self, event):
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_continue_click(self, event):
        self.state = "IDLE"
        self.build_ui()

    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time
        import math
        
        if self.state == "SHAKING":
            self.anim_timer -= delta_time
            intensity = 2.0 - self.anim_timer
            self.chest_shake_x = math.sin(self.time_elapsed * 50) * (5 * intensity)
            self.chest_scale = 1.0 + (1.0 - (self.anim_timer / 2.0)) * 0.3
            
            if self.anim_timer <= 0:
                self.state = "FLASH"
                self.anim_timer = 0.5 
                self.flash_alpha = 255
                
        elif self.state == "FLASH":
            self.anim_timer -= delta_time
            self.flash_alpha = max(0, int((self.anim_timer / 0.5) * 255))
            
            if self.anim_timer <= 0:
                self.state = "REVEAL"
                cont_btn = arcade.gui.UIFlatButton(text="Lanjutkan", width=150)
                cont_btn.on_click = self.on_continue_click
                anchor_bot = arcade.gui.UIAnchorLayout()
                anchor_bot.add(child=cont_btn, anchor_x="center", anchor_y="bottom", align_y=50)
                self.manager.add(anchor_bot)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def _draw_rect(self, center_x, center_y, width, height, color):
        hw, hh = width / 2, height / 2
        points = ((center_x - hw, center_y - hh), (center_x + hw, center_y - hh), 
                  (center_x + hw, center_y + hh), (center_x - hw, center_y + hh))
        arcade.draw_polygon_filled(points, color)

    def on_draw(self):
        self.clear()
        sw, sh = self.window.width, self.window.height
        cx, cy = sw / 2, sh / 2

        if self.state in ["SHAKING", "FLASH"]:
            chest_width = 100 * self.chest_scale
            chest_height = 80 * self.chest_scale
            self._draw_rect(cx + self.chest_shake_x, cy, chest_width, chest_height, arcade.color.GOLDENROD)
            self._draw_rect(cx + self.chest_shake_x, cy + 10, chest_width, 10, arcade.color.DARK_GOLDENROD) 
            arcade.draw_text("Membuka Peti...", cx, cy - 80, arcade.color.WHITE, 14, anchor_x="center")

        elif self.state == "REVEAL":
            import math
            ray_length = 400
            ray_count = 12
            for i in range(ray_count):
                angle = self.time_elapsed + (i * (2 * math.pi / ray_count))
                end_x = cx + math.cos(angle) * ray_length
                end_y = cy + math.sin(angle) * ray_length
                ray_color = (*self.rarity_color[:3], 100) 
                arcade.draw_line(cx, cy, end_x, end_y, ray_color, 40)

            if self.item_sprite:
                self.item_sprite.center_x = cx
                self.item_sprite.center_y = cy + 20
                # FIX ERROR: Memanggil gambar dari SpriteList
                self.sprite_list.draw() 
            
            arcade.draw_text("SELAMAT! ANDA MENDAPATKAN:", cx, cy - 60, arcade.color.WHITE, 12, anchor_x="center")
            arcade.draw_text(self.pulled_item_name, cx, cy - 90, self.rarity_color, 24, bold=True, anchor_x="center")
            arcade.draw_text(self.pulled_item_stats, cx, cy - 110, arcade.color.LIGHT_GREEN, 14, anchor_x="center")

        if self.state == "FLASH" and self.flash_alpha > 0:
            flash_color = (*self.rarity_color[:3], self.flash_alpha)
            points = ((0, 0), (sw, 0), (sw, sh), (0, sh))
            arcade.draw_polygon_filled(points, flash_color)

        self.manager.draw()

# ==========================================
# 3. LAYAR PILIH KESULITAN (BARU)
# ==========================================
class DifficultySelectionView(arcade.View):
    def __init__(self, party_size):
        super().__init__()
        self.party_size = party_size
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        self.v_box.add(arcade.gui.UILabel(text="PILIH TINGKAT KESULITAN", text_color=arcade.color.GOLD, font_size=28, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="Semakin sulit, semakin banyak EXP yang didapat!", text_color=arcade.color.LIGHT_GRAY, font_size=16, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        btn_easy = arcade.gui.UIFlatButton(text="🟢 EASY (Musuh Mentok Lv.10 | EXP x1.0)", width=350)
        btn_med = arcade.gui.UIFlatButton(text="🟡 MEDIUM (Musuh Mentok Lv.30 | EXP x1.5)", width=350)
        btn_hard = arcade.gui.UIFlatButton(text="🔴 HARD (Musuh Mentok Lv.100 | EXP x2.5)", width=350)

        btn_easy.on_click = self.on_easy
        btn_med.on_click = self.on_medium
        btn_hard.on_click = self.on_hard

        self.v_box.add(btn_easy)
        self.v_box.add(btn_med)
        self.v_box.add(btn_hard)

        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=350)
        back_btn.on_click = self.on_back_click
        self.v_box.add(arcade.gui.UILabel(text="", height=10))
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_easy(self, event): self.select_diff("EASY")
    def on_medium(self, event): self.select_diff("MEDIUM")
    def on_hard(self, event): self.select_diff("HARD")

    def select_diff(self, diff):
        self.manager.disable()
        self.window.show_view(CharacterSelectionView(self.party_size, diff))

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(ModeSelectionView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 4. LAYAR PEMILIHAN KARAKTER (UPDATE: INFO STATS, PASIF & ULTIMATE)
# ==========================================
class CharacterSelectionView(arcade.View):
    def __init__(self, party_size, difficulty):
        super().__init__()
        self.party_size = party_size
        self.difficulty = difficulty
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.available_characters = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]
        
        # Peta Elemen Karakter untuk UI
        self.element_map = {
            "Emperor": "🔴", "Mage": "🔴",       
            "Gladiator": "🔵", "Knight": "🔵",     
            "Assassin": "🌿", "Valkyrie": "🌿"    
        }

        # DATABASE INFORMASI KARAKTER LENGKAP
        self.char_info = {
            "Emperor": {"stats": "HP: 120 | ATK: 15 | DEF: 10", "role": "Counter-Attacker", "passive": "Heavenly Defense (Pantulkan DMG jika HP < 50%)", "ulti": "Absolute Decree (AoE + Pecah Zirah musuh)"},
            "Gladiator": {"stats": "HP: 115 | ATK: 14 | DEF: 4", "role": "Berserker", "passive": "Bloodlust (+10% ATK tiap turn)", "ulti": "Arena Execution (Burst DMG + Lifesteal 15% jika kill)"},
            "Assassin": {"stats": "HP: 90 | ATK: 25 | DEF: 5", "role": "Burst Assassin", "passive": "Shadow Stance (100% Crit jika tak tersentuh)", "ulti": "Fatal Strike (Mengabaikan 100% DEF musuh)"},
            "Mage": {"stats": "HP: 80 | ATK: 30 | DEF: 4", "role": "Magic Nuke", "passive": "Mana Shield (-25% DMG diterima jika Mana > 50%)", "ulti": "Meteor Swarm (AoE masif + efek Burn)"},
            "Knight": {"stats": "HP: 180 | ATK: 10 | DEF: 20", "role": "Pure Tank", "passive": "Aegis Aura (+15% DEF untuk seluruh Tim)", "ulti": "Holy Judgement (DMG dihitung dari 2x DEF)"},
            "Valkyrie": {"stats": "HP: 90 | ATK: 15 | DEF: 4", "role": "Glass Support", "passive": "Holy Aura (Regen 10 Mana tiap giliran)", "ulti": "Hymn of Valhalla (Heal area 25% HP tanpa Kebal)"}
        }

        self.player_party = []
        self.enemy_party = []

        self.last_player_char = None
        self.last_enemy_char = None

        self.build_ui()

    def get_synergy(self, party):
        if self.party_size != 3:
            return "Mode ini tidak mendukung sinergi", arcade.color.GRAY
        if len(party) < 3:
            return "Butuh 3 Karakter", arcade.color.DARK_GRAY
            
        elements = [self.element_map[char] for char in party]
        counts = {e: elements.count(e) for e in set(elements)}
        
        if counts.get("🔴", 0) == 3: return "🔥 INFERNO (+20% ATK)", arcade.color.RED
        if counts.get("🔵", 0) == 3: return "🌊 OCEANIC (Regen 5% HP)", arcade.color.LIGHT_BLUE
        if counts.get("🌿", 0) == 3: return "🍃 NATURE (+20% DEF)", arcade.color.LIGHT_GREEN
        if len(counts) == 3: return "✨ TRINITY (Kebal Debuff)", arcade.color.GOLD
        
        return "❌ Tidak Ada Sinergi", arcade.color.LIGHT_GRAY

    def build_ui(self):
        self.manager.clear()
        main_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        # ========================================
        # PANEL KIRI: PEMAIN
        # ========================================
        left_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        left_panel.add(arcade.gui.UILabel(text=f"TIM ANDA ({len(self.player_party)}/{self.party_size})", font_size=18, bold=True, text_color=arcade.color.LIGHT_BLUE))

        p_grid = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        p_col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
        p_col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)

        for i, char in enumerate(self.available_characters):
            element_icon = self.element_map[char]
            btn = arcade.gui.UIFlatButton(text=f"{char[:3].upper()} {element_icon}", width=80, height=40)
            btn.on_click = self.make_select_action(char, is_player=True)
            if i % 2 == 0: p_col1.add(btn)
            else: p_col2.add(btn)
            
        p_grid.add(p_col1)
        p_grid.add(p_col2)
        left_panel.add(p_grid)

        left_panel.add(arcade.gui.UILabel(text="", height=5))
        
        # Area Gambar Portrait & Info Detail Pemain
        if self.last_player_char:
            # Tinggi kotak diperkecil agar teks muat
            left_panel.add(arcade.gui.UISpace(width=150, height=100, color=arcade.color.DARK_BLUE))
            char_display = f"{self.element_map[self.last_player_char]} {self.last_player_char}"
            left_panel.add(arcade.gui.UILabel(text=char_display, font_size=16, bold=True, text_color=arcade.color.WHITE))
            
            # --- TEKS INFORMASI KARAKTER (BARU) ---
            info = self.char_info[self.last_player_char]
            info_text = f"🛡️ {info['role']}\n📊 {info['stats']}\n\n🌟 Pasif: {info['passive']}\n🔥 Ulti: {info['ulti']}"
            left_panel.add(arcade.gui.UILabel(text=info_text, font_size=11, text_color=arcade.color.LIGHT_GRAY, multiline=True, width=300))
            
            left_panel.add(arcade.gui.UILabel(text="", height=5))
            undo_p_btn = arcade.gui.UIFlatButton(text="↩️ Batal", width=150, height=30)
            undo_p_btn.on_click = self.on_undo_player
            left_panel.add(undo_p_btn)
        else:
            left_panel.add(arcade.gui.UISpace(width=150, height=100, color=arcade.color.DARK_GRAY))
            left_panel.add(arcade.gui.UILabel(text="Pilih Karakter", font_size=14, text_color=arcade.color.GRAY))

        # Tampilan Sinergi Pemain
        left_panel.add(arcade.gui.UILabel(text="", height=10))
        syn_name_p, syn_color_p = self.get_synergy(self.player_party)
        left_panel.add(arcade.gui.UILabel(text="Sinergi Aktif:", font_size=12, text_color=arcade.color.WHITE))
        left_panel.add(arcade.gui.UILabel(text=syn_name_p, font_size=14, bold=True, text_color=syn_color_p))


        # ========================================
        # PANEL TENGAH: KONTROL (UPDATE INFO ELEMEN)
        # ========================================
        center_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        center_panel.add(arcade.gui.UILabel(text="VS", font_size=36, bold=True, text_color=arcade.color.CRIMSON))

        rand_btn = arcade.gui.UIFlatButton(text="🎲 RANDOM", width=150)
        rand_btn.on_click = self.on_random
        center_panel.add(rand_btn)

        # --- INFO KELEMAHAN ELEMEN ---
        element_info = arcade.gui.UIBoxLayout(vertical=True, space_between=2)
        element_info.add(arcade.gui.UILabel(text="Rantai Elemen:", font_size=12, text_color=arcade.color.WHITE))
        element_info.add(arcade.gui.UILabel(text="🔴 Api > 🌿 Daun", font_size=12, bold=True))
        element_info.add(arcade.gui.UILabel(text="🌿 Daun > 🔵 Air", font_size=12, text_color=arcade.color.LIGHT_GREEN, bold=True))
        element_info.add(arcade.gui.UILabel(text="🔵 Air > 🔴 Api", font_size=12, text_color=arcade.color.LIGHT_BLUE, bold=True))
        center_panel.add(element_info)
        # ----------------------------

        if len(self.player_party) == self.party_size and len(self.enemy_party) == self.party_size:
            ready_btn = arcade.gui.UIFlatButton(text="✅ SELESAI", width=150)
            ready_btn.on_click = self.on_ready
            center_panel.add(ready_btn)
        else:
            wait_btn = arcade.gui.UIFlatButton(text="Pilih Karakter...", width=150)
            center_panel.add(wait_btn)

        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=150)
        back_btn.on_click = self.on_back_click
        center_panel.add(back_btn)


        # ========================================
        # PANEL KANAN: MUSUH
        # ========================================
        right_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        right_panel.add(arcade.gui.UILabel(text=f"TIM LAWAN ({len(self.enemy_party)}/{self.party_size})", font_size=18, bold=True, text_color=arcade.color.CRIMSON))

        e_grid = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        e_col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
        e_col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)

        for i, char in enumerate(self.available_characters):
            element_icon = self.element_map[char]
            btn = arcade.gui.UIFlatButton(text=f"{char[:3].upper()} {element_icon}", width=80, height=40)
            btn.on_click = self.make_select_action(char, is_player=False)
            if i % 2 == 0: e_col1.add(btn)
            else: e_col2.add(btn)
            
        e_grid.add(e_col1)
        e_grid.add(e_col2)
        right_panel.add(e_grid)

        right_panel.add(arcade.gui.UILabel(text="", height=5))
        
        # Area Gambar Portrait & Info Detail Musuh
        if self.last_enemy_char:
            right_panel.add(arcade.gui.UISpace(width=150, height=100, color=arcade.color.DARK_RED))
            char_display = f"{self.element_map[self.last_enemy_char]} {self.last_enemy_char}"
            right_panel.add(arcade.gui.UILabel(text=char_display, font_size=16, bold=True, text_color=arcade.color.WHITE))
            
            # --- TEKS INFORMASI KARAKTER (BARU) ---
            info = self.char_info[self.last_enemy_char]
            info_text = f"🛡️ {info['role']}\n📊 {info['stats']}\n\n🌟 Pasif: {info['passive']}\n🔥 Ulti: {info['ulti']}"
            right_panel.add(arcade.gui.UILabel(text=info_text, font_size=11, text_color=arcade.color.LIGHT_GRAY, multiline=True, width=300))
            
            right_panel.add(arcade.gui.UILabel(text="", height=5))
            undo_e_btn = arcade.gui.UIFlatButton(text="↩️ Batal", width=150, height=30)
            undo_e_btn.on_click = self.on_undo_enemy
            right_panel.add(undo_e_btn)
        else:
            right_panel.add(arcade.gui.UISpace(width=150, height=100, color=arcade.color.DARK_GRAY))
            right_panel.add(arcade.gui.UILabel(text="Pilih Karakter", font_size=14, text_color=arcade.color.GRAY))

        # Tampilan Sinergi Musuh
        right_panel.add(arcade.gui.UILabel(text="", height=10))
        syn_name_e, syn_color_e = self.get_synergy(self.enemy_party)
        right_panel.add(arcade.gui.UILabel(text="Sinergi Aktif:", font_size=12, text_color=arcade.color.WHITE))
        right_panel.add(arcade.gui.UILabel(text=syn_name_e, font_size=14, bold=True, text_color=syn_color_e))


        main_layout.add(left_panel)
        main_layout.add(center_panel)
        main_layout.add(right_panel)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=main_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def make_select_action(self, char_name, is_player):
        def action(event):
            if is_player and len(self.player_party) < self.party_size:
                self.player_party.append(char_name)
                self.last_player_char = char_name
            elif not is_player and len(self.enemy_party) < self.party_size:
                self.enemy_party.append(char_name)
                self.last_enemy_char = char_name
            self.build_ui() 
        return action

    def on_undo_player(self, event):
        if self.player_party:
            self.player_party.pop() 
            self.last_player_char = self.player_party[-1] if self.player_party else None
            self.build_ui()

    def on_undo_enemy(self, event):
        if self.enemy_party:
            self.enemy_party.pop() 
            self.last_enemy_char = self.enemy_party[-1] if self.enemy_party else None
            self.build_ui()

    def on_random(self, event):
        import random
        while len(self.player_party) < self.party_size:
            self.player_party.append(random.choice(self.available_characters))
        while len(self.enemy_party) < self.party_size:
            self.enemy_party.append(random.choice(self.available_characters))

        self.last_player_char = self.player_party[-1]
        self.last_enemy_char = self.enemy_party[-1]
        self.build_ui()

    def on_ready(self, event):
        self.manager.disable()
        from gui.views import EquipmentSelectionView
        self.window.show_view(EquipmentSelectionView(self.player_party, self.enemy_party, self.difficulty))

    def on_back_click(self, event):
        self.manager.disable()
        from gui.views import DifficultySelectionView
        self.window.show_view(DifficultySelectionView(self.party_size))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 4.5 LAYAR PERSIAPAN EQUIPMENT (PERBAIKAN BUG STOK & UI MODERN)
# ==========================================
class EquipmentSelectionView(arcade.View):
    def __init__(self, player_types: list, enemy_types: list, difficulty: str):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.player_types = player_types
        self.enemy_types = enemy_types
        self.difficulty = difficulty

        # 1. Hitung jumlah sebenarnya dari setiap item di Inventory
        raw_inventory = SaveManager.get_inventory()
        self.inventory_counts = {"Tangan Kosong": 999} # Tangan kosong tak terbatas
        for item in raw_inventory:
            self.inventory_counts[item] = self.inventory_counts.get(item, 0) + 1
        
        # 2. Catat item apa yang sedang dipakai oleh masing-masing karakter
        self.equipped_items = ["Tangan Kosong"] * len(self.player_types)

        # Bangun UI Utama
        self.build_main_ui()

    def build_main_ui(self):
        self.manager.clear()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        # JUDUL: Perbesar dan buat sangat kontras
        title = arcade.gui.UILabel(text="🛡️ PERSIAPAN EQUIPMENT ⚔️", text_color=arcade.color.GOLD, font_size=28, bold=True)
        self.v_box.add(title)
        
        # SUB-JUDUL: Gunakan putih agar kontras
        self.v_box.add(arcade.gui.UILabel(text="Klik tombol di samping nama untuk membuka daftar equipment", text_color=arcade.color.WHITE, font_size=14, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        # DAFTAR KARAKTER
        for i, char_type in enumerate(self.player_types):
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
            
            # LABEL NAMA KARAKTER: Putih, Tebal, dan lebih besar
            lbl = arcade.gui.UILabel(text=f"{char_type}", width=150, font_size=16, bold=True, text_color=arcade.color.WHITE)
            
            current_item = self.equipped_items[i]
            btn = arcade.gui.UIFlatButton(text=current_item, width=350, height=50)
            btn.on_click = self.make_open_picker_action(i)
            
            row.add(lbl)
            row.add(btn)
            self.v_box.add(row)

        self.v_box.add(arcade.gui.UILabel(text="", height=20))
        start_btn = arcade.gui.UIFlatButton(text="🔥 Masuk ke Arena 🔥", width=380)
        start_btn.on_click = self.on_start_battle
        self.v_box.add(start_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def make_open_picker_action(self, char_idx):
        def action(event):
            self.open_item_picker(char_idx)
        return action

    def open_item_picker(self, char_idx):
        """Membuat layar pop-up/overlay ala Select Field untuk memilih item"""
        self.manager.clear()
        picker_box = arcade.gui.UIBoxLayout(space_between=10)
        
        picker_box.add(arcade.gui.UILabel(text=f"Pilih Equipment untuk {self.player_types[char_idx]}", font_size=20, text_color=arcade.color.GOLD, bold=True))
        picker_box.add(arcade.gui.UILabel(text="", height=10))

        from engine.gacha_system import GachaSystem
        import os
        
        # Loop semua item unik yang kita punya
        for item_name, count in self.inventory_counts.items():
            # Sembunyikan item yang stoknya habis (kecuali sedang dipakai orang lain)
            if count <= 0 and item_name != "Tangan Kosong":
                continue 
                
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
            
            # RENDER GAMBAR ITEM JIKA ADA
            if item_name != "Tangan Kosong":
                item_data = GachaSystem.ITEM_POOL.get(item_name)
                img_path = item_data.get("img", "") if item_data else ""
                
                if os.path.exists(img_path):
                    tex = arcade.load_texture(img_path)
                    tex_widget = arcade.gui.UITextureRectangle(texture=tex, width=40, height=40)
                    row.add(tex_widget)
                else:
                    placeholder = arcade.gui.UISpace(width=40, height=40, color=arcade.color.GRAY)
                    row.add(placeholder)
            else:
                placeholder = arcade.gui.UISpace(width=40, height=40, color=arcade.color.DARK_GRAY)
                row.add(placeholder)

            # RENDER TOMBOL & TEKS INFORMASI
            if item_name == "Tangan Kosong":
                btn_text = "Tangan Kosong (Lepas Equipment)"
            else:
                desc = item_data["desc"] if item_data else "Tidak ada deskripsi"
                btn_text = f"[{item_data['rarity']}] {item_name} (Sisa: {count})\nEfek: {desc}"

            # PERBAIKAN: Tombol diperlebar (width=650) dan ditinggikan (height=60) agar teks lega
            btn = arcade.gui.UIFlatButton(text=btn_text, width=650, height=60)
            btn.on_click = self.make_select_item_action(char_idx, item_name)
            
            row.add(btn)
            picker_box.add(row)
            
        picker_box.add(arcade.gui.UILabel(text="", height=10))
        back_btn = arcade.gui.UIFlatButton(text="Batal", width=200)
        back_btn.on_click = lambda e: self.build_main_ui()
        picker_box.add(back_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=picker_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def make_select_item_action(self, char_idx, item_name):
        def action(event):
            # 1. Kembalikan item lama ke inventory (jika bukan Tangan Kosong)
            old_item = self.equipped_items[char_idx]
            if old_item != "Tangan Kosong":
                self.inventory_counts[old_item] += 1
            
            # 2. Kurangi stok item baru (jika bukan Tangan Kosong)
            if item_name != "Tangan Kosong":
                self.inventory_counts[item_name] -= 1
                
            # 3. Pasangkan ke karakter
            self.equipped_items[char_idx] = item_name
            
            # 4. Kembali ke UI Utama
            self.build_main_ui()
        return action

    def on_start_battle(self, event):
        self.manager.disable()
        from models.equipment import Equipment 
        from models.synergy import SynergyBuff # IMPORT DECORATOR BARU KITA
        from engine.gacha_system import GachaSystem
        
        # Fungsi pembantu untuk menentukan nama sinergi
        element_map = {
            "Emperor": "🔴", "Mage": "🔴",
            "Gladiator": "🔵", "Knight": "🔵",
            "Assassin": "🌿", "Valkyrie": "🌿"
        }
        
        def get_synergy_type(party):
            if len(party) < 3: return None
            elements = [element_map[char] for char in party]
            counts = {e: elements.count(e) for e in set(elements)}
            if counts.get("🔴", 0) == 3: return "INFERNO"
            if counts.get("🔵", 0) == 3: return "OCEANIC"
            if counts.get("🌿", 0) == 3: return "NATURE"
            if len(counts) == 3: return "TRINITY"
            return None

        # Hitung sinergi kedua tim
        p_synergy = get_synergy_type(self.player_types)
        e_synergy = get_synergy_type(self.enemy_types)
        
        # 1. SETUP TIM PEMAIN 
        player_party = []
        player_levels = []
        for i, char_type in enumerate(self.player_types):
            char = CharacterFactory.create_character(char_type, f"{char_type} (P{i+1})")
            level = SaveManager.get_character_data(char_type)["level"]
            char.apply_scaling(level=level, stat_multiplier=1.0)
            player_levels.append(level)
            
            # LAPISAN 1: Bungkus karakter dengan Equipment Gacha
            eq_name = self.equipped_items[i]
            if eq_name != "Tangan Kosong":
                eq_data = GachaSystem.ITEM_POOL[eq_name]
                char = Equipment(char, item_name=eq_name, bonus_atk=eq_data["bonus_atk"], bonus_def=eq_data["bonus_def"])
            
            # LAPISAN 2: Bungkus lagi dengan Sinergi (Hanya jika aktif)
            if p_synergy:
                char = SynergyBuff(char, synergy_type=p_synergy)
                    
            player_party.append(char)
            
        # 2. SETUP TIM MUSUH
        avg_level = max(1, sum(player_levels) // len(player_levels))
        diff_settings = DIFFICULTY_SETTINGS[self.difficulty]
        enemy_level = min(avg_level, diff_settings["enemy_cap"])
        all_items = list(GachaSystem.ITEM_POOL.keys())
        
        enemy_party = []
        for i, char_type in enumerate(self.enemy_types):
            char = CharacterFactory.create_character(char_type, f"{char_type} (Musuh {i+1})")
            char.apply_scaling(level=enemy_level, stat_multiplier=diff_settings["stat_mult"])
            
            import random
            random_eq = random.choice(all_items)
            eq_data = GachaSystem.ITEM_POOL[random_eq]
            
            # LAPISAN 1: Musuh pakai Equipment acak
            char = Equipment(char, item_name=random_eq, bonus_atk=eq_data["bonus_atk"], bonus_def=eq_data["bonus_def"])
            
            # LAPISAN 2: Sinergi Musuh (Awas kalau musuh dapat Inferno!)
            if e_synergy:
                char = SynergyBuff(char, synergy_type=e_synergy)
                
            enemy_party.append(char)

        # 3. LEMPAR KE ARENA
        from gui.views import BattleView
        
        # Cek apakah ini mode Endless untuk menentukan lantai awal
        start_floor = 1 if self.difficulty == "Endless" else 0
        battle_view = BattleView(player_party, enemy_party, self.difficulty, self.player_types, endless_floor=start_floor)
        self.window.show_view(battle_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()


# ==========================================
# 5. LAYAR GAME OVER (UPDATE HADIAH EXP)
# ==========================================
class GameOverView(arcade.View):
    def __init__(self, winner_name: str, loser_name: str, winner_hp: int, is_player_win: bool, difficulty: str, player_types: list):
        super().__init__()
        
        HistoryManager.save_match(winner_name, loser_name, winner_hp)
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Cek apakah pemain menang, lalu bagikan EXP
        exp_text = ""
        if is_player_win:
            title_text = "🏆 TIM ANDA MENANG! 🏆"
            title_color = arcade.color.LIGHT_GREEN
            
            party_size = len(player_types)
            base_exp = 50 if party_size == 1 else (75 if party_size == 2 else 100)
            multiplier = DIFFICULTY_SETTINGS[difficulty]["exp_mult"]
            total_exp = int(base_exp * multiplier)
            
            # --- PENAMBAHAN HADIAH GOLD ---
            # Gold dikali jumlah karakter yang hidup/dibawa agar sepadan
            gold_reward = DIFFICULTY_SETTINGS[difficulty]["gold_reward"] * party_size
            current_gold = SaveManager.add_gold(gold_reward)
            
            # Update teks antarmuka untuk menampilkan uang
            exp_text = f"Memperoleh +{total_exp} EXP & 💰 {gold_reward} Gold!\nTotal Uang: {current_gold} Gold\n\n"
            
            for char_type in player_types:
                new_lvl, leveled_up = SaveManager.add_exp(char_type, total_exp)
                if leveled_up:
                    exp_text += f"⭐ {char_type} NAIK KE LEVEL {new_lvl}! ⭐\n"
                else:
                    exp_text += f"✔️ {char_type} (Lv.{new_lvl})\n"
        else:
            title_text = "💀 TIM ANDA KALAH 💀"
            title_color = arcade.color.CRIMSON
            exp_text = "Game Over.\nTidak ada EXP maupun Gold yang diperoleh."

        # RENDER UI
        winner_label = arcade.gui.UILabel(text=title_text, text_color=title_color, font_size=30, bold=True)
        exp_label = arcade.gui.UILabel(text=exp_text, text_color=arcade.color.YELLOW, font_size=16, multiline=True, width=500, align="center")
        
        menu_button = arcade.gui.UIFlatButton(text="Kembali ke Menu", width=250)
        menu_button.on_click = self.on_menu_click

        self.v_box.add(winner_label)
        self.v_box.add(exp_label)
        self.v_box.add(menu_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_menu_click(self, event):
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# LAYAR INVENTORY (REDESAIN: GRID & DETAILS PANE)
# ==========================================
class InventoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        # Ambil data dari penyimpanan
        raw_inventory = SaveManager.get_inventory()
        self.item_counts = {}
        for item in raw_inventory:
            self.item_counts[item] = self.item_counts.get(item, 0) + 1
            
        # Tentukan item yang sedang dipilih pertama kali (jika ada)
        self.selected_item = list(self.item_counts.keys())[0] if self.item_counts else None
        
        # Panggil fungsi perakit UI
        self.build_ui()

    def build_ui(self):
        self.manager.clear()
        
        main_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=40)

        # ========================================
        # PANEL KIRI: GRID KOTAK ITEM
        # ========================================
        left_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        left_panel.add(arcade.gui.UILabel(text="🎒 DAFTAR EQUIPMENT", text_color=arcade.color.GOLD, font_size=20, bold=True))
        left_panel.add(arcade.gui.UILabel(text="", height=10))

        if not self.item_counts:
            # UBAH: Warna dari LIGHT_GRAY ke WHITE agar jelas
            left_panel.add(arcade.gui.UILabel(text="Inventory Anda kosong.", text_color=arcade.color.WHITE, font_size=16, bold=True))
        else:
            from engine.gacha_system import GachaSystem
            import os
            
            items_per_row = 4
            current_row = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
            
            for i, (item_name, count) in enumerate(self.item_counts.items()):
                if i % items_per_row == 0 and i != 0:
                    left_panel.add(current_row)
                    current_row = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
                
                item_data = GachaSystem.ITEM_POOL.get(item_name)
                img_path = item_data.get("img", "") if item_data else ""
                
                if os.path.exists(img_path):
                    tex = arcade.load_texture(img_path)
                    btn = arcade.gui.UITextureButton(texture=tex, width=80, height=80)
                else:
                    btn_text = f"{item_name[:6]}..\nx{count}"
                    btn = arcade.gui.UIFlatButton(text=btn_text, width=80, height=80)
                
                btn.on_click = self.make_select_action(item_name)
                current_row.add(btn)
                
            left_panel.add(current_row)

        left_panel.add(arcade.gui.UILabel(text="", height=20))
        back_btn = arcade.gui.UIFlatButton(text="Kembali ke Menu", width=250)
        back_btn.on_click = self.on_back_click
        left_panel.add(back_btn)

        # ========================================
        # PANEL KANAN: DETAIL ITEM
        # ========================================
        right_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        if self.selected_item:
            item_data = GachaSystem.ITEM_POOL.get(self.selected_item)
            if item_data:
                img_path = item_data.get("img", "")
                if os.path.exists(img_path):
                    tex = arcade.load_texture(img_path)
                    right_panel.add(arcade.gui.UITextureRectangle(texture=tex, width=200, height=200))
                else:
                    right_panel.add(arcade.gui.UISpace(width=200, height=200, color=arcade.color.DARK_GRAY))
                
                color = arcade.color.WHITE
                rarity = item_data["rarity"]
                if rarity == "Mythic": color = arcade.color.RED
                elif rarity == "Legendary": color = arcade.color.GOLD
                elif rarity == "Rare": color = arcade.color.LIGHT_BLUE
                
                # UBAH: Font diperbesar, menggunakan WHITE untuk teks biasa, dan bold=True
                right_panel.add(arcade.gui.UILabel(text=f"{self.selected_item}", text_color=color, font_size=28, bold=True))
                right_panel.add(arcade.gui.UILabel(text=f"Rank: {rarity} | Dimiliki: {self.item_counts[self.selected_item]}x", text_color=arcade.color.WHITE, font_size=14, bold=True))
                
                right_panel.add(arcade.gui.UILabel(text="Atribut:", text_color=arcade.color.GOLD, font_size=18, bold=True))
                right_panel.add(arcade.gui.UILabel(text=f"👉 {item_data['desc']}", text_color=arcade.color.LIGHT_GREEN, font_size=16, bold=True))
                
                right_panel.add(arcade.gui.UILabel(text="", height=10)) 
                right_panel.add(arcade.gui.UILabel(text="Kisah Item:", text_color=arcade.color.GOLD, font_size=18, bold=True))
                # UBAH: Dari GRAY (samar) menjadi WHITE (terang) dengan ukuran 14
                right_panel.add(arcade.gui.UILabel(text=f'"{item_data["lore"]}"', text_color=arcade.color.WHITE, font_size=14, multiline=True, width=400))

        main_layout.add(left_panel)
        main_layout.add(arcade.gui.UISpace(width=50, height=10)) 
        main_layout.add(right_panel)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=main_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def make_select_action(self, item_name):
        def action(event):
            # Update state item yang dipilih dan gambar ulang (refresh) UI-nya
            self.selected_item = item_name
            self.build_ui()
        return action

    def on_back_click(self, event):
        self.manager.disable()
        # Menggunakan lazy import agar tidak circular
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 6. LAYAR PERTEMPURAN (FINAL: ANIMASI SPRITE & IKON STATUS)
# ==========================================
class BattleView(arcade.View):
    def __init__(self, player_party: list, enemy_party: list, difficulty: str, player_types: list, endless_floor=0):
        super().__init__()
        self.endless_floor = endless_floor
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.difficulty = difficulty
        self.player_types = player_types 
        
        self.p1_idx = 0
        self.p2_idx = 0
        self.p1_active = self.player_party[self.p1_idx]
        self.p2_active = self.enemy_party[self.p2_idx]
        self.current_turn = self.p1_active
        
        self.p1_log = "Pertempuran Dimulai!\nGiliran Anda."
        self.p2_log = ""
        self.is_player_turn = True
        self.enemy_delay_timer = 0.0
        
        # --- VARIABEL ANIMASI BARU ---
        self.time_elapsed = 0.0
        self.attack_anim_timer = 0.0
        self.attacking_side = 0 # 1 untuk P1, 2 untuk P2
        
        self.shake_timer = 0.0
        self.flash_timer = 0.0
        self.flash_duration = 0.0
        self.flash_color = arcade.color.WHITE

        self.character_sprites = arcade.SpriteList()
        self.p1_sprite = None
        self.p2_sprite = None
        
        self.floating_texts = []
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        self.update_layout() 
        self.build_ui()
        
        self.p1_active.on_turn_start()
        if self.p1_active.passive_logs:
            self.p1_log += f"\n{self.p1_active.passive_logs}"

    # --- FUNGSI BARU: MEMUAT SPRITE GAMBAR ---
    def _load_character_sprite(self, char_name, is_player):
        """Memuat gambar PNG jika ada, jika tidak pakai kotak warna default"""
        file_path = f"assets/{char_name.lower()}.png"
        if os.path.exists(file_path):
            # Memuat gambar asli (Anda mungkin perlu mengatur 'scale' jika gambarnya terlalu besar)
            sprite = arcade.Sprite(file_path, scale=1.0)
        else:
            # Fallback jika gambar belum ada
            color = arcade.color.CRIMSON if is_player else arcade.color.ROYAL_BLUE
            sprite = arcade.SpriteSolidColor(150, 220, color=color)
        return sprite

    def build_ui(self):
        self.manager.clear()
        
        # PANEL ROSTER PEMAIN (KIRI)
        left_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        for i, char in enumerate(self.player_party):
            if char.current_hp <= 0:
                text = f"💀 {char.name[:6]}..\nDEAD"
                btn = arcade.gui.UIFlatButton(text=text, width=120, height=60) 
            elif i == self.p1_idx:
                text = f"▶️ {char.name[:6]}..\nAktif"
                btn = arcade.gui.UIFlatButton(text=text, width=120, height=60) 
            else:
                text = f"🔄 {char.name[:6]}..\nHP: {int(char.current_hp)}"
                btn = arcade.gui.UIFlatButton(text=text, width=120, height=60)
                btn.on_click = self.make_swap_action(i) 
            left_box.add(btn)
            
        anchor_left = arcade.gui.UIAnchorLayout()
        anchor_left.add(child=left_box, anchor_x="left", anchor_y="center", align_x=20)
        self.manager.add(anchor_left)

        # PANEL ROSTER MUSUH (KANAN) 
        right_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        for i, char in enumerate(self.enemy_party):
            if char.current_hp <= 0:
                text = f"💀 {char.name[:6]}..\nDEAD"
            elif i == self.p2_idx:
                text = f"▶️ {char.name[:6]}..\nAktif"
            else:
                text = f"⏳ {char.name[:6]}..\nMenunggu"
            btn = arcade.gui.UIFlatButton(text=text, width=120, height=60)
            right_box.add(btn)
            
        anchor_right = arcade.gui.UIAnchorLayout()
        anchor_right.add(child=right_box, anchor_x="right", anchor_y="center", align_x=-20)
        self.manager.add(anchor_right)

        # TOMBOL AKSI UTAMA (BAWAH)
        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        
        attack_button = arcade.gui.UIFlatButton(text="⚔️ Attack", width=120)
        skill_button = arcade.gui.UIFlatButton(text="🔥 Skill", width=120)
        item_button = arcade.gui.UIFlatButton(text="🎒 Heal", width=120)
        
        ulti_text = f"⏳ Ulti ({self.p1_active.current_ulti_cd})" if self.p1_active.current_ulti_cd > 0 else "🌟 Ultimate"
        self.ulti_button = arcade.gui.UIFlatButton(text=ulti_text, width=150)
        
        attack_button.on_click = self.on_attack_click
        skill_button.on_click = self.on_skill_click
        item_button.on_click = self.on_item_click
        self.ulti_button.on_click = self.on_ultimate_click

        self.h_box.add(attack_button)
        self.h_box.add(skill_button)
        self.h_box.add(item_button)
        self.h_box.add(self.ulti_button)

        anchor_bottom = arcade.gui.UIAnchorLayout()
        anchor_bottom.add(child=self.h_box, anchor_x="center", anchor_y="bottom", align_y=40)
        self.manager.add(anchor_bottom)

    def make_swap_action(self, target_idx):
        def action(event):
            if not self.is_player_turn: return
            old_char = self.p1_active
            target_char = self.player_party[target_idx]
            
            self.p1_idx = target_idx
            self.p1_active = target_char
            self.update_layout() # Akan memuat gambar karakter yang baru
            
            self.p1_log = f"🔄 {old_char.name} mundur!\n{target_char.name} maju ke garis depan!"
            self.p2_log = ""
            self.spawn_floating_text("SWITCH!", self.p1_base_x, self.base_y, arcade.color.CYAN)
            self.shake_timer = 0.2
            
            self.check_game_state()
            self.build_ui()
        return action

    def trigger_flash(self, color, duration=0.15):
        self.flash_color = color
        self.flash_timer = duration
        self.flash_duration = duration

    def update_layout(self):
        sw = self.window.width
        sh = self.window.height
        self.p1_base_x = sw * 0.35
        self.p2_base_x = sw * 0.65
        self.base_y = sh * 0.50
        
        # --- UPDATE SPRITE KETIKA SWAP / START ---
        self.character_sprites.clear()
        self.p1_sprite = self._load_character_sprite(self.p1_active.name, is_player=True)
        self.p2_sprite = self._load_character_sprite(self.p2_active.name, is_player=False)
        self.character_sprites.append(self.p1_sprite)
        self.character_sprites.append(self.p2_sprite)

        self.p1_sprite.center_x = self.p1_base_x
        self.p1_sprite.center_y = self.base_y
        self.p2_sprite.center_x = self.p2_base_x
        self.p2_sprite.center_y = self.base_y

        self.p1_hp_bar = StatusBar(self.p1_active, x=self.p1_base_x - 125, y=self.base_y + 140, width=250, height=20, is_mana=False)
        self.p1_mana_bar = StatusBar(self.p1_active, x=self.p1_base_x - 100, y=self.base_y + 110, width=200, height=15, is_mana=True)
        self.p2_hp_bar = StatusBar(self.p2_active, x=self.p2_base_x - 125, y=self.base_y + 140, width=250, height=20, is_mana=False)
        self.p2_mana_bar = StatusBar(self.p2_active, x=self.p2_base_x - 100, y=self.base_y + 110, width=200, height=15, is_mana=True)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.update_layout()
        self.build_ui()

    def spawn_floating_text(self, text, x, y, color):
        adjusted_y = y
        for f_text in self.floating_texts:
            if abs(f_text.x - x) < 50 and abs(f_text.y - adjusted_y) < 30:
                adjusted_y += 30
        self.floating_texts.append(FloatingText(text, x, adjusted_y, color))

    def check_and_spawn_element_text(self, attacker, target, base_x, base_y):
        if not attacker or not target: return
        atk_el = attacker.element
        def_el = target.element
        
        if (atk_el == "Api" and def_el == "Daun") or (atk_el == "Daun" and def_el == "Air") or (atk_el == "Air" and def_el == "Api"):
            self.spawn_floating_text("WEAKNESS!", base_x, base_y + 40, arcade.color.ORANGE)
        elif (atk_el == "Api" and def_el == "Air") or (atk_el == "Air" and def_el == "Daun") or (atk_el == "Daun" and def_el == "Api"):
            self.spawn_floating_text("RESIST!", base_x, base_y + 40, arcade.color.GRAY)

    def handle_death(self) -> bool:
        if self.p2_active.current_hp <= 0:
            alive_enemies = [i for i, c in enumerate(self.enemy_party) if c.current_hp > 0]
            if not alive_enemies:
                self.manager.disable()
                if self.endless_floor > 0:
                    self.window.show_view(EndlessRewardView(self.player_party, self.endless_floor, self.player_types))
                else:
                    self.window.show_view(GameOverView("Tim Pemain", "Tim Musuh", self.p1_active.current_hp, True, self.difficulty, self.player_types))
                return True
            else:
                self.p2_idx = alive_enemies[0] 
                self.p2_active = self.enemy_party[self.p2_idx]
                self.p2_log = f"Musuh gugur! {self.p2_active.name} melompat ke arena!"
                self.update_layout()
                self.build_ui()
                self.current_turn = self.p1_active
                self.is_player_turn = True
                self.p1_active.on_turn_start()
                return True

        if self.p1_active.current_hp <= 0:
            alive_players = [i for i, c in enumerate(self.player_party) if c.current_hp > 0]
            if not alive_players:
                self.manager.disable()
                self.window.show_view(GameOverView("Tim Musuh", "Tim Pemain", self.p2_active.current_hp, False, self.difficulty, self.player_types))
                return True
            else:
                self.p1_idx = alive_players[0]
                self.p1_active = self.player_party[self.p1_idx]
                self.p1_log = f"Rekanmu gugur! {self.p1_active.name} otomatis maju!\nGiliran Anda."
                self.update_layout()
                self.build_ui()
                self.current_turn = self.p1_active
                self.is_player_turn = True
                self.p1_active.on_turn_start()
                return True
        return False

    def on_attack_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            self.attack_anim_timer = 0.3 # Memicu Animasi Serangan
            self.attacking_side = 1
            
            from engine.commands import BasicAttackCommand
            command = BasicAttackCommand()
            status = command.execute(self.p1_active, self.p2_active)
            self.p2_log = ""
            
            passive_msg = f"\n{self.p1_active.passive_logs}" if self.p1_active.passive_logs else ""
            
            if status == "DODGE":
                self.p1_log = "Serangan Meleset!" + passive_msg
                self.spawn_floating_text("MISS!", self.p2_base_x, self.base_y, arcade.color.GRAY)
            elif status == "CRIT":
                self.p1_log = "CRITICAL HIT!" + passive_msg
                self.spawn_floating_text("CRITICAL!", self.p2_base_x, self.base_y, arcade.color.GOLD)
                self.check_and_spawn_element_text(self.p1_active, self.p2_active, self.p2_base_x, self.base_y)
                self.shake_timer = 0.3
                self.trigger_flash(arcade.color.WHITE)
            else:
                self.p1_log = "Melancarkan Basic Attack!" + passive_msg
                self.spawn_floating_text("BAM!", self.p2_base_x, self.base_y, arcade.color.RED)
                self.check_and_spawn_element_text(self.p1_active, self.p2_active, self.p2_base_x, self.base_y)
            
            self.check_game_state()
            self.build_ui()

    def on_skill_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            self.attack_anim_timer = 0.4 
            self.attacking_side = 1
            
            from engine.commands import SpecialSkillCommand
            command = SpecialSkillCommand()
            command.execute(self.p1_active, self.p2_active)
            passive_msg = f"\n{self.p1_active.passive_logs}" if self.p1_active.passive_logs else ""
            self.p1_log = "Menggunakan Special Skill!" + passive_msg
            self.p2_log = ""
            self.spawn_floating_text("SKILL!", self.p2_base_x, self.base_y, arcade.color.ORANGE)
            self.check_and_spawn_element_text(self.p1_active, self.p2_active, self.p2_base_x, self.base_y)
            self.shake_timer = 0.5
            self.trigger_flash(arcade.color.LIGHT_BLUE)
            
            self.check_game_state()
            self.build_ui()

    def on_item_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            from engine.commands import UseItemCommand
            from models.item import HealthPotion
            potion = HealthPotion()
            command = UseItemCommand(potion)
            command.execute(self.p1_active, self.p2_active)
            self.p1_log = f"Meminum {potion.name}!"
            self.p2_log = ""
            self.spawn_floating_text("+40 HP", self.p1_base_x, self.base_y, arcade.color.LIGHT_GREEN)
            
            self.check_game_state()
            self.build_ui()

    def on_ultimate_click(self, event):
        if not self.is_player_turn: return
        if self.current_turn == self.p1_active:
            from engine.commands import UltimateCommand
            command = UltimateCommand()
            status, log_msg = command.execute(self.p1_active, self.p2_active, self.enemy_party, self.player_party)
            
            if status == "FAIL":
                self.p1_log = log_msg 
                self.spawn_floating_text("NOT READY!", self.p1_base_x, self.base_y, arcade.color.GRAY)
            else:
                self.attack_anim_timer = 0.6 
                self.attacking_side = 1
                self.p1_log = log_msg
                self.p2_log = ""
                self.spawn_floating_text("ULTIMATE!", self.p1_base_x, self.base_y + 50, arcade.color.MAGENTA)
                self.shake_timer = 0.8
                self.trigger_flash(arcade.color.MAGENTA, 0.4)
                
                self.check_game_state()
                self.build_ui()

    def check_game_state(self):
        if self.handle_death(): return
        self.current_turn = self.p2_active
        self.is_player_turn = False 
        
        self.p2_active.on_turn_start()
        effect_logs = self.p2_active.process_effects()
        
        combined_log = ""
        if self.p2_active.passive_logs:
            combined_log += f"{self.p2_active.passive_logs}\n"
        if effect_logs:
            combined_log += effect_logs
            self.spawn_floating_text("RACUN!", self.p2_base_x, self.base_y, arcade.color.PURPLE)
            
        if combined_log:
            self.p2_log = combined_log
            
        if self.handle_death(): return
        self.enemy_delay_timer = 1.5

    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time
        
        for f_text in self.floating_texts:
            f_text.update()
        self.floating_texts = [f for f in self.floating_texts if not f.is_dead()]

        self.p1_hp_bar.update(delta_time)
        self.p1_mana_bar.update(delta_time)
        self.p2_hp_bar.update(delta_time)
        self.p2_mana_bar.update(delta_time)

        if self.flash_timer > 0:
            self.flash_timer -= delta_time

        # --- SISTEM ANIMASI SPRITE ---
        # 1. Idle Breathing (Bernapas / Membesar Mengecil)
        idle_scale = 1.0 + math.sin(self.time_elapsed * 3) * 0.02
        self.p1_sprite.scale = idle_scale
        self.p2_sprite.scale = idle_scale
        
        base_x1, base_x2 = self.p1_base_x, self.p2_base_x
        
        # 2. Attack Lunge (Melompat Serang)
        if self.attack_anim_timer > 0:
            self.attack_anim_timer -= delta_time
            # Rumus matematika untuk lompatan cepat ke depan lalu mundur
            lunge_dist = 60 * math.sin(self.attack_anim_timer * math.pi / 0.3)
            
            if self.attacking_side == 1:
                base_x1 += max(0, lunge_dist)
            elif self.attacking_side == 2:
                base_x2 -= max(0, lunge_dist)

        # 3. Layar Guncang (Screen Shake)
        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            offset_x, offset_y = random.randint(-8, 8), random.randint(-8, 8)
            self.p1_sprite.center_x = base_x1 + offset_x
            self.p1_sprite.center_y = self.base_y + offset_y
            self.p2_sprite.center_x = base_x2 + offset_x
            self.p2_sprite.center_y = self.base_y + offset_y
        else:
            self.p1_sprite.center_x = base_x1
            self.p1_sprite.center_y = self.base_y
            self.p2_sprite.center_x = base_x2
            self.p2_sprite.center_y = self.base_y

        # AI Musuh
        if not self.is_player_turn and self.enemy_delay_timer > 0:
            self.enemy_delay_timer -= delta_time
            if self.enemy_delay_timer <= 0:
                self.enemy_turn()

    def enemy_turn(self):
        from engine.commands import BasicAttackCommand, SpecialSkillCommand, UltimateCommand
        import random
        
        self.attacking_side = 2
        
        if self.p2_active.current_ulti_cd <= 0:
            self.attack_anim_timer = 0.6
            command = UltimateCommand()
            status, log_msg = command.execute(self.p2_active, self.p1_active, self.player_party, self.enemy_party)
            self.p2_log = log_msg
            self.spawn_floating_text("ULTIMATE!", self.p2_base_x, self.base_y + 50, arcade.color.RED)
            self.shake_timer = 0.8
            self.trigger_flash(arcade.color.RED, 0.4)
            
        else:
            chance = random.randint(1, 100)
            if chance <= 30 and self.p2_active.current_mana >= 20:
                self.attack_anim_timer = 0.4
                command = SpecialSkillCommand()
                command.execute(self.p2_active, self.p1_active)
                self.p2_log = "Musuh menggunakan Special Skill!"
                self.spawn_floating_text("SKILL!", self.p1_base_x, self.base_y, arcade.color.ORANGE)
                self.check_and_spawn_element_text(self.p2_active, self.p1_active, self.p1_base_x, self.base_y)
                self.shake_timer = 0.5
                self.trigger_flash(arcade.color.RED)
            else:
                self.attack_anim_timer = 0.3
                command = BasicAttackCommand()
                status = command.execute(self.p2_active, self.p1_active)
                if status == "DODGE":
                    self.p2_log = "Serangan Musuh Meleset!"
                    self.spawn_floating_text("MISS!", self.p1_base_x, self.base_y, arcade.color.GRAY)
                elif status == "CRIT":
                    self.p2_log = "MUSUH CRITICAL HIT!"
                    self.spawn_floating_text("CRITICAL!", self.p1_base_x, self.base_y, arcade.color.GOLD)
                    self.check_and_spawn_element_text(self.p2_active, self.p1_active, self.p1_base_x, self.base_y)
                    self.shake_timer = 0.3
                    self.trigger_flash(arcade.color.RED)
                else:
                    self.p2_log = "Musuh Menyerang!"
                    self.spawn_floating_text("BAM!", self.p1_base_x, self.base_y, arcade.color.RED)
                    self.check_and_spawn_element_text(self.p2_active, self.p1_active, self.p1_base_x, self.base_y)

        if self.handle_death(): return
        
        self.current_turn = self.p1_active
        self.is_player_turn = True 
        self.p1_active.on_turn_start()
        
        effect_logs = self.p1_active.process_effects()
        combined_log = ""
        if self.p1_active.passive_logs:
            combined_log += f"{self.p1_active.passive_logs}\n"
        if effect_logs:
            combined_log += f"{effect_logs}\n"
            
        combined_log += "\nGiliran Anda!"
        self.p1_log = combined_log
        self.build_ui()
        if self.handle_death(): return

    # --- FUNGSI BARU: MENGGAMBAR IKON BUFF/DEBUFF ---
    def draw_status_icons(self, char, x, y):
        icons = []
        if getattr(char, 'is_invincible', False): icons.append("🌟")
        if getattr(char, 'shadow_stance', False): icons.append("💨")
        
        # Mengekstrak atribut dari Decorator jika ada
        bloodlust = getattr(char, 'bloodlust_stacks', 0)
        aegis = getattr(char, 'aegis_stacks', 0)
        
        if bloodlust > 0: icons.append(f"⚔️x{bloodlust}")
        if aegis > 0: icons.append(f"🛡️x{aegis}")
        
        icon_str = " ".join(icons)
        if icon_str:
            arcade.draw_text(icon_str, x, y, arcade.color.YELLOW, 14, anchor_x="center", bold=True)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.character_sprites.draw()
        
        # Nama Karakter
        arcade.Text(self.p1_active.name, x=self.p1_base_x, y=self.base_y + 180, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        arcade.Text(self.p2_active.name, x=self.p2_base_x, y=self.base_y + 180, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        
        self.p1_hp_bar.draw()
        self.p1_mana_bar.draw()
        self.p2_hp_bar.draw()
        self.p2_mana_bar.draw()
        
        # --- GAMBAR IKON STATUS DI BAWAH MANA BAR ---
        self.draw_status_icons(self.p1_active, self.p1_base_x - 100, self.base_y + 85)
        self.draw_status_icons(self.p2_active, self.p2_base_x - 100, self.base_y + 85)
        
        arcade.Text(
            self.p1_log, x=self.p1_base_x, y=self.base_y - 140, 
            color=arcade.color.WHITE, font_size=18, bold=True, 
            anchor_x="center", anchor_y="top", multiline=True, width=380, align="center"
        ).draw()
        
        arcade.Text(
            self.p2_log, x=self.p2_base_x, y=self.base_y - 140, 
            color=arcade.color.WHITE, font_size=18, bold=True, 
            anchor_x="center", anchor_y="top", multiline=True, width=380, align="center"
        ).draw()
        
        for f_text in self.floating_texts:
            f_text.draw()
            
        self.manager.draw()

        if self.flash_timer > 0 and self.flash_duration > 0:
            alpha = int(255 * (self.flash_timer / self.flash_duration))
            alpha = max(0, min(255, alpha)) 
            current_flash_color = (*self.flash_color[:3], alpha)
            sw = self.window.width
            sh = self.window.height
            points = ((0, 0), (sw, 0), (sw, sh), (0, sh))
            arcade.draw_polygon_filled(points, current_flash_color)

# ==========================================
# LAYAR PEMILIHAN KARAKTER KHUSUS ENDLESS (3v3)
# ==========================================
class EndlessCharacterSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.party_size = 3
        self.difficulty = "Endless"
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.available_characters = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]
        
        self.element_map = {
            "Emperor": "🔴", "Mage": "🔴",       
            "Gladiator": "🔵", "Knight": "🔵",     
            "Assassin": "🌿", "Valkyrie": "🌿"    
        }

        self.char_info = {
            "Emperor": {"stats": "HP: 120 | ATK: 15 | DEF: 10", "role": "Counter-Attacker", "passive": "Heavenly Defense (Pantulkan DMG jika HP < 50%)", "ulti": "Absolute Decree (AoE + Pecah Zirah musuh)"},
            "Gladiator": {"stats": "HP: 115 | ATK: 14 | DEF: 4", "role": "Berserker", "passive": "Bloodlust (+10% ATK tiap turn)", "ulti": "Arena Execution (Burst DMG + Lifesteal 15% jika kill)"},
            "Assassin": {"stats": "HP: 90 | ATK: 25 | DEF: 5", "role": "Burst Assassin", "passive": "Shadow Stance (100% Crit jika tak tersentuh)", "ulti": "Fatal Strike (Mengabaikan 100% DEF musuh)"},
            "Mage": {"stats": "HP: 80 | ATK: 30 | DEF: 4", "role": "Magic Nuke", "passive": "Mana Shield (-25% DMG diterima jika Mana > 50%)", "ulti": "Meteor Swarm (AoE masif + efek Burn)"},
            "Knight": {"stats": "HP: 180 | ATK: 10 | DEF: 20", "role": "Pure Tank", "passive": "Aegis Aura (+15% DEF untuk seluruh Tim)", "ulti": "Holy Judgement (DMG dihitung dari 2x DEF)"},
            "Valkyrie": {"stats": "HP: 90 | ATK: 15 | DEF: 4", "role": "Glass Support", "passive": "Holy Aura (Regen 10 Mana tiap giliran)", "ulti": "Hymn of Valhalla (Heal area 25% HP tanpa Kebal)"}
        }

        self.player_party = []
        self.last_player_char = None
        self.preview_sprite = None # Untuk menyimpan gambar besar

        self.build_ui()

    def get_synergy(self, party):
        if len(party) < 3:
            return "Butuh 3 Karakter", arcade.color.DARK_GRAY
        elements = [self.element_map[char] for char in party]
        counts = {e: elements.count(e) for e in set(elements)}
        if counts.get("🔴", 0) == 3: return "🔥 INFERNO (+20% ATK)", arcade.color.RED
        if counts.get("🔵", 0) == 3: return "🌊 OCEANIC (Regen 5% HP)", arcade.color.LIGHT_BLUE
        if counts.get("🌿", 0) == 3: return "🍃 NATURE (+20% DEF)", arcade.color.LIGHT_GREEN
        if len(counts) == 3: return "✨ TRINITY (Kebal Debuff)", arcade.color.GOLD
        return "❌ Tidak Ada Sinergi", arcade.color.LIGHT_GRAY

    def build_ui(self):
        self.manager.clear()
        
        # 1. PANEL KIRI: PEMILIHAN TIM PEMAIN
        left_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        left_panel.add(arcade.gui.UILabel(text=f"TIM ENDLESS ANDA ({len(self.player_party)}/3)", font_size=18, bold=True, text_color=arcade.color.LIGHT_BLUE))

        p_grid = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        p_col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
        p_col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)

        for i, char in enumerate(self.available_characters):
            btn = arcade.gui.UIFlatButton(text=f"{char[:3].upper()} {self.element_map[char]}", width=80, height=40)
            btn.on_click = self.make_select_action(char)
            if i % 2 == 0: p_col1.add(btn)
            else: p_col2.add(btn)
            
        p_grid.add(p_col1)
        p_grid.add(p_col2)
        left_panel.add(p_grid)

        left_panel.add(arcade.gui.UILabel(text="", height=20))
        
        if self.player_party:
            undo_btn = arcade.gui.UIFlatButton(text="↩️ Batal Pilihan Terakhir", width=200, height=40)
            undo_btn.on_click = self.on_undo
            left_panel.add(undo_btn)
            
        left_panel.add(arcade.gui.UILabel(text="", height=20))
        syn_name, syn_color = self.get_synergy(self.player_party)
        left_panel.add(arcade.gui.UILabel(text="Sinergi Aktif:", font_size=14, text_color=arcade.color.WHITE))
        left_panel.add(arcade.gui.UILabel(text=syn_name, font_size=16, bold=True, text_color=syn_color))

        anchor_left = arcade.gui.UIAnchorLayout()
        anchor_left.add(child=left_panel, anchor_x="left", anchor_y="center", align_x=40)
        self.manager.add(anchor_left)

        # 2. PANEL TENGAH: KONTROL
        center_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        title = arcade.gui.UILabel(text="ENDLESS TOWER", font_size=32, bold=True, text_color=arcade.color.CRIMSON)
        center_panel.add(title)
        center_panel.add(arcade.gui.UILabel(text="Hadapi musuh tanpa batas!", font_size=14, text_color=arcade.color.LIGHT_GRAY))
        center_panel.add(arcade.gui.UILabel(text="", height=20))

        if len(self.player_party) == 3:
            ready_btn = arcade.gui.UIFlatButton(text="⚔️ MASUK KE MENARA", width=200, height=50)
            ready_btn.on_click = self.on_ready
            center_panel.add(ready_btn)
        else:
            center_panel.add(arcade.gui.UIFlatButton(text="Pilih 3 Karakter...", width=200, height=50))

        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=200)
        back_btn.on_click = self.on_back_click
        center_panel.add(back_btn)

        anchor_center = arcade.gui.UIAnchorLayout()
        anchor_center.add(child=center_panel, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_center)

        # 3. PANEL KANAN: INFO DETAIL (Sprite akan digambar di on_draw)
        right_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
        if self.last_player_char:
            info = self.char_info[self.last_player_char]
            right_panel.add(arcade.gui.UILabel(text=f"{self.element_map[self.last_player_char]} {self.last_player_char}", font_size=24, bold=True, text_color=arcade.color.GOLD))
            right_panel.add(arcade.gui.UILabel(text=f"Role: {info['role']}", font_size=14, text_color=arcade.color.WHITE))
            right_panel.add(arcade.gui.UILabel(text=f"Stats: {info['stats']}", font_size=12, text_color=arcade.color.LIGHT_GRAY))
            right_panel.add(arcade.gui.UILabel(text="", height=10))
            
            # Text area untuk Pasif dan Ultimate
            desc_text = f"🌟 Pasif:\n{info['passive']}\n\n🔥 Ultimate:\n{info['ulti']}"
            right_panel.add(arcade.gui.UILabel(text=desc_text, font_size=12, text_color=arcade.color.WHITE, multiline=True, width=300))
            
            # Load Sprite Besar
            import os
            file_path = f"assets/{self.last_player_char.lower()}.png"
            if os.path.exists(file_path):
                self.preview_sprite = arcade.Sprite(file_path, scale=2.0) # Ukuran dibesarkan 2x lipat
            else:
                self.preview_sprite = arcade.SpriteSolidColor(250, 350, arcade.color.CRIMSON)

        anchor_right = arcade.gui.UIAnchorLayout()
        anchor_right.add(child=right_panel, anchor_x="right", anchor_y="bottom", align_x=-40, align_y=40)
        self.manager.add(anchor_right)

    def make_select_action(self, char_name):
        def action(event):
            if len(self.player_party) < self.party_size:
                self.player_party.append(char_name)
                self.last_player_char = char_name
                self.build_ui()
        return action

    def on_undo(self, event):
        if self.player_party:
            self.player_party.pop()
            self.last_player_char = self.player_party[-1] if self.player_party else None
            self.preview_sprite = None
            self.build_ui()

    def on_ready(self, event):
        import random
        self.manager.disable()
        
        # GENERATE MUSUH ACAK UNTUK AWALAN ENDLESS
        enemy_party = []
        for _ in range(3):
            enemy_party.append(random.choice(self.available_characters))
            
        from gui.views import EquipmentSelectionView
        # Lempar ke Equipment Selection, dengan difficulty "Endless"
        self.window.show_view(EquipmentSelectionView(self.player_party, enemy_party, "Endless"))

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(ModeSelectionView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        self.clear()
        
        # Gambar siluet/sprite besar di kanan atas
        if self.preview_sprite:
            self.preview_sprite.center_x = self.window.width * 0.85
            self.preview_sprite.center_y = self.window.height * 0.65
            self.preview_sprite.draw()
            
        self.manager.draw()

# ==========================================
# 7. LAYAR RIWAYAT PERTANDINGAN
# ==========================================
class HistoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        title_label = arcade.gui.UILabel(
            text="📜 RIWAYAT PERTANDINGAN", text_color=arcade.color.GOLD, font_size=24, bold=True
        )
        self.v_box.add(title_label)

        history_data = HistoryManager.get_history()

        if not history_data:
            empty_label = arcade.gui.UILabel(text="Belum ada riwayat pertandingan.", text_color=arcade.color.WHITE)
            self.v_box.add(empty_label)
        else:
            recent_matches = list(reversed(history_data))[:5]
            for match in recent_matches:
                match_text = f"[{match['waktu']}] 🏆 {match['pemenang']} (Sisa HP: {match['sisa_hp_pemenang']}) mengalahkan {match['kalah']}"
                row_label = arcade.gui.UILabel(text=match_text, text_color=arcade.color.LIGHT_GRAY, font_size=12)
                self.v_box.add(row_label)

        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=200)
        back_btn.on_click = self.on_back_click
        self.v_box.add(arcade.gui.UILabel(text="", height=20)) 
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EIGHTEEN_PERCENT_GREY if hasattr(arcade.color, 'EIGHTEEN_PERCENT_GREY') else arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# LAYAR REWARD ENDLESS TOWER
# ==========================================
class EndlessRewardView(arcade.View):
    def __init__(self, surviving_party, cleared_floor, player_types):
        super().__init__()
        self.surviving_party = surviving_party
        self.cleared_floor = cleared_floor
        self.player_types = player_types
        
        # Hadiah bertambah seiring tingginya lantai
        self.gold_reward = 100 * self.cleared_floor
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.build_ui()

    def build_ui(self):
        self.manager.clear()
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        
        v_box.add(arcade.gui.UILabel(text=f"LANTAI {self.cleared_floor} DITAKLUKKAN!", font_size=32, bold=True, text_color=arcade.color.GOLD))
        v_box.add(arcade.gui.UILabel(text=f"Hadiah Sementara: {self.gold_reward} Gold", font_size=18, text_color=arcade.color.YELLOW))
        v_box.add(arcade.gui.UILabel(text="Hati-hati! Jika Anda kalah di lantai berikutnya, semua hadiah hilang!", font_size=12, text_color=arcade.color.LIGHT_GRAY))
        v_box.add(arcade.gui.UILabel(text="", height=20))
        
        btn_next = arcade.gui.UIFlatButton(text=f"⚔️ Lanjut Lantai {self.cleared_floor + 1}", width=250)
        btn_next.on_click = self.on_next_floor
        
        btn_home = arcade.gui.UIFlatButton(text="💰 Ambil Gold & Pulang", width=250)
        btn_home.on_click = self.on_home
        
        v_box.add(btn_next)
        v_box.add(btn_home)
        
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_next_floor(self, event):
        import random
        from engine.factory import CharacterFactory
        from models.equipment import Equipment
        from engine.gacha_system import GachaSystem
        from models.synergy import SynergyBuff

        # BANGUN MUSUH YANG LEBIH KUAT
        new_floor = self.cleared_floor + 1
        available_chars = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]
        enemy_party = []
        
        # Scaling brutal (Level musuh naik tajam tiap lantai)
        enemy_level = max(1, new_floor // 2)
        stat_mult = 1.0 + (new_floor * 0.15) 
        
        for i in range(3):
            char_type = random.choice(available_chars)
            char = CharacterFactory.create_character(char_type, f"Lantai {new_floor} {char_type}")
            char.apply_scaling(level=enemy_level, stat_multiplier=stat_mult)
            
            # Musuh selalu pakai equipment Legendary/Mythic jika lantai tinggi
            random_eq = random.choice(list(GachaSystem.ITEM_POOL.keys()))
            eq_data = GachaSystem.ITEM_POOL[random_eq]
            char = Equipment(char, random_eq, eq_data["bonus_atk"], eq_data["bonus_def"])
            
            enemy_party.append(char)

        # Berangkat ke arena lagi dengan TIM YANG SAMA (HP tidak di-reset)
        self.manager.disable()
        self.window.show_view(BattleView(self.surviving_party, enemy_party, "Endless", self.player_types, endless_floor=new_floor))

    def on_home(self, event):
        # Simpan uang ke Save Data
        from engine.save_manager import SaveManager
        SaveManager.add_gold(self.gold_reward)
        
        from gui.views import MainMenuView
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()