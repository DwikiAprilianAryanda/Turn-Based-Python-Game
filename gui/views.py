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

class BGMManager:
    player = None
    current_track = None
    target_vol = 1.0
    current_vol = 1.0
    fade_speed = 0.5  # Kecepatan transisi volume
    sfx_vol = 0.5

    @classmethod
    def play_sfx(cls, sound):
        """Gunakan ini untuk semua play_sound SFX di seluruh game"""
        if sound:
            arcade.play_sound(sound, volume=cls.sfx_vol)

    @classmethod
    def play(cls, track_name):
        # PASTIKAN FILE AUDIO INI ADA DI FOLDER ANDA
        tracks = {
            "MENU": "assets/bgm/menu_bgm.mp3",
            "SELECT": "assets/bgm/select_bgm.mp3",
            "BATTLE": "assets/bgm/battle_theme.mp3",
            "BATTLE_ENDLESS": "assets/bgm/endless_bgm.mp3"
        }
        
        # Jika lagu yang sama sedang diputar, biarkan berlanjut (jangan diulang)
        if cls.current_track == track_name and cls.player:
            return 
            
        # Hentikan lagu sebelumnya jika ada
        if cls.player:
            try:
                cls.player.pause()
            except:
                pass
            cls.player = None 
            
        cls.current_track = track_name
        cls.target_vol = 1.0
        cls.current_vol = 1.0
        
        path = tracks.get(track_name)
        if path and os.path.exists(path):
            sound = arcade.load_sound(path)
            try:
                cls.player = sound.play(volume=1.0, loop=True)
            except TypeError:
                # Jika 'loop' juga tidak dikenali, gunakan ini:
                cls.player = sound.play(volume=1.0)
            
    @classmethod
    def mute_for_sfx(cls):
        """Panggil ini saat animasi gacha dimulai"""
        cls.target_vol = 0.1  # Jangan 0 mutlak, 0.1 agar masih terdengar samar-samar
        
    @classmethod
    def restore_volume(cls):
        """Panggil ini saat hadiah gacha sudah muncul"""
        cls.target_vol = 1.0

    @classmethod
    def update(cls, delta_time):
        """Mengatur transisi suara agar mulus (fade in / fade out)"""
        if not cls.player:
            return
            
        if cls.current_vol < cls.target_vol:
            cls.current_vol = min(cls.target_vol, cls.current_vol + (cls.fade_speed * delta_time))
            cls.player.volume = cls.current_vol
        elif cls.current_vol > cls.target_vol:
            # Fade out sedikit lebih cepat dari fade in
            cls.current_vol = max(cls.target_vol, cls.current_vol - (cls.fade_speed * 3 * delta_time))
            cls.player.volume = cls.current_vol

class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.build_ui()

        import os
        click_path = "assets/sfx/click.mp3"
        self.sfx_click = arcade.load_sound(click_path) if os.path.exists(click_path) else None

    def build_ui(self):
        self.manager.clear()

        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 200))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        panel_width = 500
        panel_height = 550  # Diperbesar untuk SFX section
        panel_wrapper = arcade.gui.UIAnchorLayout(width=panel_width, height=panel_height, size_hint=(None, None))
        panel_bg = arcade.gui.UISpace(width=panel_width, height=panel_height, color=(15, 20, 30, 230))
        panel_wrapper.add(child=panel_bg)

        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        v_box.add(arcade.gui.UILabel(text="⚙️ PENGATURAN SUARA", font_size=26, bold=True, text_color=arcade.color.GOLD))
        v_box.add(arcade.gui.UILabel(text="", height=5))

        vol_btn_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
        }
        mute_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.MAROON, "border_color": arcade.color.WHITE, "border_width": 2}
        }

        # ==========================================
        # SECTION BGM
        # ==========================================
        bgm_vol_pct = int(BGMManager.target_vol * 100)
        v_box.add(arcade.gui.UILabel(text=f"🎵 Volume BGM: {bgm_vol_pct}%", font_size=18, text_color=arcade.color.WHITE, bold=True))

        bgm_row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        btn_bgm_down = arcade.gui.UIFlatButton(text="🔉 -10%", width=130, height=50, style=vol_btn_style)
        btn_bgm_mute = arcade.gui.UIFlatButton(text="🔇 MUTE", width=130, height=50, style=mute_style)
        btn_bgm_up   = arcade.gui.UIFlatButton(text="🔊 +10%", width=130, height=50, style=vol_btn_style)

        def on_bgm_down(event):
            BGMManager.target_vol = max(0.0, round(BGMManager.target_vol - 0.1, 1))
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        def on_bgm_up(event):
            BGMManager.target_vol = min(1.0, round(BGMManager.target_vol + 0.1, 1))
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        def on_bgm_mute(event):
            BGMManager.target_vol = 0.0 if BGMManager.target_vol > 0 else 1.0
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        btn_bgm_down.on_click = on_bgm_down
        btn_bgm_mute.on_click = on_bgm_mute
        btn_bgm_up.on_click   = on_bgm_up
        bgm_row.add(btn_bgm_down)
        bgm_row.add(btn_bgm_mute)
        bgm_row.add(btn_bgm_up)
        v_box.add(bgm_row)

        bgm_filled = int(BGMManager.target_vol * 10)
        bgm_bar = "█" * bgm_filled + "░" * (10 - bgm_filled)
        bgm_bar_color = arcade.color.LIME_GREEN if bgm_filled > 3 else arcade.color.RED
        v_box.add(arcade.gui.UILabel(text=bgm_bar, font_size=22, text_color=bgm_bar_color, bold=True))

        v_box.add(arcade.gui.UILabel(text="", height=5))

        # ==========================================
        # SECTION SFX
        # ==========================================
        sfx_vol_pct = int(BGMManager.sfx_vol * 100)
        v_box.add(arcade.gui.UILabel(text=f"🔔 Volume SFX & Klik: {sfx_vol_pct}%", font_size=18, text_color=arcade.color.WHITE, bold=True))

        sfx_row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        btn_sfx_down = arcade.gui.UIFlatButton(text="🔉 -10%", width=130, height=50, style=vol_btn_style)
        btn_sfx_mute = arcade.gui.UIFlatButton(text="🔇 MUTE", width=130, height=50, style=mute_style)
        btn_sfx_up   = arcade.gui.UIFlatButton(text="🔊 +10%", width=130, height=50, style=vol_btn_style)

        def on_sfx_down(event):
            BGMManager.sfx_vol = max(0.0, round(BGMManager.sfx_vol - 0.1, 1))
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        def on_sfx_up(event):
            BGMManager.sfx_vol = min(1.0, round(BGMManager.sfx_vol + 0.1, 1))
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        def on_sfx_mute(event):
            BGMManager.sfx_vol = 0.0 if BGMManager.sfx_vol > 0 else 0.5
            BGMManager.play_sfx(self.sfx_click)
            self.build_ui()

        btn_sfx_down.on_click = on_sfx_down
        btn_sfx_mute.on_click = on_sfx_mute
        btn_sfx_up.on_click   = on_sfx_up
        sfx_row.add(btn_sfx_down)
        sfx_row.add(btn_sfx_mute)
        sfx_row.add(btn_sfx_up)
        v_box.add(sfx_row)

        sfx_filled = int(BGMManager.sfx_vol * 10)
        sfx_bar = "█" * sfx_filled + "░" * (10 - sfx_filled)
        sfx_bar_color = arcade.color.CYAN if sfx_filled > 3 else arcade.color.RED
        v_box.add(arcade.gui.UILabel(text=sfx_bar, font_size=22, text_color=sfx_bar_color, bold=True))

        v_box.add(arcade.gui.UILabel(text="", height=10))

        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        back_btn = arcade.gui.UIFlatButton(text="❌ Kembali ke Menu", width=300, height=50, style=cancel_style)

        def on_back(event):
            BGMManager.play_sfx(self.sfx_click)
            self.manager.disable()
            self.window.show_view(MainMenuView())

        back_btn.on_click = on_back
        v_box.add(back_btn)

        panel_wrapper.add(child=v_box, anchor_x="center", anchor_y="center")
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=panel_wrapper, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_update(self, delta_time):
        BGMManager.update(delta_time)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 1. LAYAR PEMILIHAN MODE (UPDATE: FITUR RESUME)
# ==========================================
class ModeSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/standart_menu_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
        self.build_ui()

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

    def build_ui(self):
        self.manager.clear()
        from engine.save_manager import SaveManager
        
        # ==========================================
        # 1. JURUS DIMMER GLOBAL
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 180))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        # ==========================================
        # 2. PANEL KACA GELAP (WADAH MENU)
        # ==========================================
        panel_width = 550
        panel_height = 420
        panel_wrapper = arcade.gui.UIAnchorLayout(width=panel_width, height=panel_height, size_hint=(None, None))
        panel_bg = arcade.gui.UISpace(width=panel_width, height=panel_height, color=(15, 20, 30, 230))
        panel_wrapper.add(child=panel_bg)

        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        # Header
        v_box.add(arcade.gui.UILabel(text="⛩️ JALUR PERTANDINGAN ⛩️", font_size=26, bold=True, text_color=arcade.color.GOLD))
        v_box.add(arcade.gui.UILabel(text="Pilih mode permainan untuk menguji taktik Anda", font_size=13, text_color=arcade.color.LIGHT_GRAY))
        v_box.add(arcade.gui.UILabel(text="", height=15))
        
        # ==========================================
        # 3. GAYA TOMBOL DINAMIS
        # ==========================================
        resume_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_ORANGE, "border_color": arcade.color.ORANGE, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ORANGE, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ORANGE_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        std_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 2}
        }
        
        endl_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.PURPLE, "border_color": arcade.color.MAGENTA, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_VIOLET, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.INDIGO, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }

        # Cek apakah ada progress Endless yang tersimpan
        endless_state = SaveManager.get_endless_state()
        if endless_state:
            btn_resume = arcade.gui.UIFlatButton(text=f"▶️ Lanjutkan Endless (Lantai {endless_state['floor']})", width=400, height=50, style=resume_style)
            btn_resume.on_click = self.on_resume_click
            v_box.add(btn_resume)
            panel_height += 65 # Ekspansi ukuran panel otomatis
        
        # FIX: Teks 1v1/2v2 Dihapus!
        btn_standard = arcade.gui.UIFlatButton(text="⚔️ Standard Mode (Pertarungan 3v3)", width=400, height=50, style=std_style)
        btn_standard.on_click = self.on_standard_click
        
        btn_endless = arcade.gui.UIFlatButton(text="♾️ Endless Tower (Mulai Perjalanan Baru)", width=400, height=50, style=endl_style)
        btn_endless.on_click = self.on_endless_click
        
        btn_back = arcade.gui.UIFlatButton(text="❌ Kembali ke Menu Utama", width=400, height=45, style=cancel_style)
        btn_back.on_click = self.on_back_click
        
        v_box.add(btn_standard)
        v_box.add(btn_endless)
        v_box.add(arcade.gui.UILabel(text="", height=10)) # Spacer sebelum tombol kembali
        v_box.add(btn_back)
        
        panel_wrapper.add(child=v_box, anchor_x="center", anchor_y="center")
        
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=panel_wrapper, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_resume_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from engine.save_manager import SaveManager
        from engine.factory import CharacterFactory
        from models.equipment import Equipment
        from engine.gacha_system import GachaSystem
        from models.synergy import SynergyBuff
        import random
        
        state = SaveManager.get_endless_state()
        start_floor = state["floor"]
        party_names = state["party"]
        equipments = state.get("equipments", ["Tangan Kosong"] * len(party_names))

        # --- CEK SINERGI UNTUK RESUME ---
        element_map = {
            "Emperor": "🔴", "Mage": "🔴",
            "Gladiator": "🔵", "Knight": "🔵",
            "Assassin": "🌿", "Valkyrie": "🌿"
        }
        def get_synergy_type(party):
            if len(party) < 3: return None
            elements = [element_map.get(char, "") for char in party]
            counts = {e: elements.count(e) for e in set(elements) if e}
            if counts.get("🔴", 0) == 3: return "INFERNO"
            if counts.get("🔵", 0) == 3: return "OCEANIC"
            if counts.get("🌿", 0) == 3: return "NATURE"
            if len(counts) == 3: return "TRINITY"
            return None
            
        p_synergy = get_synergy_type(party_names)

        # --- BANGUN ULANG TIM PEMAIN ---
        player_party = []
        for i, char_type in enumerate(party_names):
            char = CharacterFactory.create_character(char_type, f"{char_type} (P{i+1})")
            
            # Pakaikan Equipment yang benar
            eq_name = equipments[i]
            if eq_name != "Tangan Kosong" and eq_name in GachaSystem.ITEM_POOL:
                eq_data = GachaSystem.ITEM_POOL[eq_name]
                char = Equipment(char, item_name=eq_name, bonus_atk=eq_data["bonus_atk"], bonus_def=eq_data["bonus_def"])
                
            # Kembalikan efek Sinergi
            if p_synergy:
                char = SynergyBuff(char, synergy_type=p_synergy)
                
            # FIX BUG: TEMPELKAN LABEL LAGI SAAT RESUME!
            char.equipped_name = eq_name
            
            player_party.append(char)

        # --- BANGUN MUSUH (Sesuai Scaling Lantai) ---
        available_chars = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]
        enemy_party = []
        enemy_level = max(1, start_floor // 2)
        stat_mult = 1.0 + ((start_floor - 1) * 0.1) 
        
        for i in range(3):
            e_type = random.choice(available_chars)
            char = CharacterFactory.create_character(e_type, f"Lantai {start_floor} {e_type}")
            if hasattr(char, 'apply_scaling'):
                char.apply_scaling(level=enemy_level, stat_multiplier=stat_mult)
            char.level = enemy_level 
            
            # Musuh tetap dapat equipment sesuai kasta lantainya
            random_eq = GachaSystem.get_enemy_equipment("Endless", start_floor)
            eq_data = GachaSystem.ITEM_POOL[random_eq]
            char = Equipment(char, item_name=random_eq, bonus_atk=eq_data["bonus_atk"], bonus_def=eq_data["bonus_def"])
            char.level = enemy_level
            enemy_party.append(char)

        from gui.views import BattleView
        self.window.show_view(BattleView(player_party, enemy_party, "Endless", party_names, endless_floor=start_floor))

    def on_standard_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from gui.views import DifficultySelectionView 
        self.window.show_view(DifficultySelectionView(party_size=3)) 

    def on_endless_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        from engine.save_manager import SaveManager
        SaveManager.clear_endless_state() # Hapus save lama jika mulai baru
        self.manager.disable()
        from gui.views import EndlessCharacterSelectionView
        self.window.show_view(EndlessCharacterSelectionView())

    def on_back_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# 2. LAYAR MENU UTAMA (UPDATE: AAA STYLE & BGM)
# ==========================================
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/menu_bg.jpg" 
        
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2 
            self.bg_sprite.center_y = self.window.height / 2 
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
            
        self.build_ui()

        click_path = "assets/sfx/click.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

    def build_ui(self):
        self.manager.clear()

        # ==========================================
        # PANEL KIRI (FROSTED GLASS RATA KIRI)
        # ==========================================
        left_panel_width = 500
        left_bg = arcade.gui.UISpace(width=left_panel_width, height=self.window.height, color=(10, 15, 20, 220))
        left_anchor = arcade.gui.UIAnchorLayout()
        left_anchor.add(child=left_bg, anchor_x="left", anchor_y="center")
        self.manager.add(left_anchor)

        # Kontainer VBox dengan align="left"
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=12, align="left")

        # HEADER GAME (Typo Diperbaiki!)
        title_box = arcade.gui.UIBoxLayout(vertical=True, space_between=2, align="left")
        title_box.add(arcade.gui.UILabel(text="WELCOME TO", font_size=16, text_color=arcade.color.CYAN, bold=True))
        title_box.add(arcade.gui.UILabel(text="FIGHTING ARENA", font_size=42, text_color=arcade.color.GOLD, bold=True))
        title_box.add(arcade.gui.UILabel(text="Epic Turn-Based Battle", font_size=14, text_color=arcade.color.LIGHT_GRAY))
        
        v_box.add(title_box)
        v_box.add(arcade.gui.UILabel(text="", height=40)) 

        # ==========================================
        # GAYA TOMBOL MODERN (Transparan -> Menyala)
        # ==========================================
        menu_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": (255, 255, 255, 15), "border_color": (0,0,0,0), "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 2}
        }
        
        exit_style = {
            "normal": {"font_color": arcade.color.LIGHT_GRAY, "bg_color": (255, 255, 255, 10), "border_color": (0,0,0,0), "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.RED, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }

        def create_menu_btn(text, icon, action_func, is_exit=False):
            style = exit_style if is_exit else menu_style
            btn = arcade.gui.UIFlatButton(text=f"{icon}   {text}", width=360, height=55, style=style)
            
            def action_wrapper(event):
                if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
                action_func(event)
                
            btn.on_click = action_wrapper
            return btn

        v_box.add(create_menu_btn("Mulai Bermain", "⚔️", self.on_start_click))
        v_box.add(create_menu_btn("Inventory Equipment", "🎒", self.on_inv_click))
        v_box.add(create_menu_btn("Gacha Terminal", "✨", self.on_gacha_click))
        v_box.add(create_menu_btn("Riwayat Pertandingan", "📜", self.on_hist_click))
        v_box.add(create_menu_btn("Pengaturan Suara", "⚙️", self.on_settings_click))
        
        v_box.add(arcade.gui.UILabel(text="", height=30)) 
        v_box.add(create_menu_btn("Keluar Permainan", "❌", self.on_quit_click, is_exit=True))

        content_anchor = arcade.gui.UIAnchorLayout()
        content_anchor.add(child=v_box, anchor_x="left", anchor_y="center", align_x=45)
        self.manager.add(content_anchor)

        # Footer Versi
        footer_anchor = arcade.gui.UIAnchorLayout()
        footer_anchor.add(child=arcade.gui.UILabel(text="v1.0.0 | Epic Arena Project", font_size=11, text_color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom", align_x=-20, align_y=20)
        self.manager.add(footer_anchor)

    # AKSI TOMBOL
    def on_settings_click(self, event):
        self.manager.disable()
        from gui.views import SettingsView
        self.window.show_view(SettingsView())

    def on_start_click(self, event):
        self.manager.disable()
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
        # PASTIKAN MUSIK MENU UTAMA DIPUTAR!
        BGMManager.play("MENU")

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# LAYAR GACHA (UPDATE: PRO UI & RGBA FIX)
# ==========================================
class GachaView(arcade.View):
    def __init__(self):
        super().__init__()
        from engine.save_manager import SaveManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/gacha_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
        
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
        
        self.build_ui()

        # MUAT SFX
        import os
        click_path = "assets/sfx/gacha.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

        click_path2 = "assets/sfx/click.mp3"
        if os.path.exists(click_path2):
            self.sfx_click2 = arcade.load_sound(click_path2)
        else:
            self.sfx_click2 = None

    # ==========================================
    # UI STATE: IDLE (BANNER UTAMA ALA GAME AAA)
    # ==========================================
    def build_ui(self):
        from engine.save_manager import SaveManager
        from engine.gacha_system import GachaSystem
        self.manager.clear()

        # Tentukan "Hadiah Utama" (Featured Item) untuk Banner ini
        featured_item = "Mahkota Raja Iblis" 
        item_data = GachaSystem.ITEM_POOL.get(featured_item, {})

        # 1. TOMBOL KEMBALI (KIRI ATAS)
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": (0,0,0,150), "border_color": arcade.color.GRAY, "border_width": 1},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": (50,50,50,200), "border_color": arcade.color.WHITE, "border_width": 1},
            "press": {"font_color": arcade.color.WHITE, "bg_color": (20,20,20,200), "border_color": arcade.color.WHITE, "border_width": 1}
        }
        back_btn = arcade.gui.UIFlatButton(text="< Kembali", width=120, height=40, style=cancel_style)
        
        def on_back_sfx(event):
            if hasattr(self, 'sfx_click2') and self.sfx_click2: BGMManager.play_sfx(self.sfx_click)
            self.on_back_click(event)
            
        back_btn.on_click = on_back_sfx
        anchor_tl = arcade.gui.UIAnchorLayout()
        anchor_tl.add(child=back_btn, anchor_x="left", anchor_y="top", align_x=30, align_y=-30)
        self.manager.add(anchor_tl)

        # 2. SALDO GOLD (KANAN ATAS)
        gold_anchor = arcade.gui.UIAnchorLayout()
        gold_bg = arcade.gui.UISpace(width=200, height=40, color=(0, 0, 0, 180))
        gold_label = arcade.gui.UILabel(text=f"🪙 {SaveManager.get_gold()}", font_size=18, bold=True, text_color=arcade.color.YELLOW)
        
        gold_box = arcade.gui.UIAnchorLayout(width=200, height=40, size_hint=(None, None))
        gold_box.add(child=gold_bg)
        gold_box.add(child=gold_label, anchor_x="center", anchor_y="center")
        
        gold_anchor.add(child=gold_box, anchor_x="right", anchor_y="top", align_x=-30, align_y=-30)
        self.manager.add(gold_anchor)

        # 3. SISI KIRI: INFORMASI BANNER & LORE
        left_anchor = arcade.gui.UIAnchorLayout()
        left_box = arcade.gui.UIBoxLayout(vertical=True, space_between=8)
        
        # Latar belakang gelap bergradasi (semu) untuk teks kiri agar terbaca di atas background
        text_bg = arcade.gui.UISpace(width=450, height=400, color=(10, 15, 25, 180))
        text_bg_wrapper = arcade.gui.UIAnchorLayout(width=450, height=400, size_hint=(None, None))
        text_bg_wrapper.add(child=text_bg)
        
        left_box.add(arcade.gui.UILabel(text="Banner Equipment Spesial", font_size=16, text_color=arcade.color.GOLD, bold=True))
        left_box.add(arcade.gui.UILabel(text=featured_item.upper(), font_size=34, text_color=arcade.color.RED, bold=True))
        
        left_box.add(arcade.gui.UILabel(text="", height=10))
        left_box.add(arcade.gui.UILabel(text="⏱️ Sisa Waktu: Permanen", font_size=12, text_color=arcade.color.LIGHT_GREEN))
        
        # Info Pity / Aturan
        pity_text = "Setiap 10 tarikan menjamin item [Rare] atau lebih tinggi.\nItem [Mythic] dijamin dalam 80 tarikan."
        left_box.add(arcade.gui.UILabel(text=pity_text, font_size=12, text_color=arcade.color.WHITE, multiline=True, width=400))
        left_box.add(arcade.gui.UILabel(text="", height=15))
        
        # Lore Item
        lore = item_data.get("lore", "Senjata misterius dari zaman kuno.")
        left_box.add(arcade.gui.UILabel(text="Tentang Hadiah Utama:", font_size=14, text_color=arcade.color.GOLD, bold=True))
        left_box.add(arcade.gui.UILabel(text=f'"{lore}"', font_size=12, text_color=arcade.color.LIGHT_GRAY, multiline=True, width=400))
        
        if self.error_msg:
            left_box.add(arcade.gui.UILabel(text="", height=10))
            left_box.add(arcade.gui.UILabel(text=self.error_msg, font_size=14, text_color=arcade.color.RED, bold=True))

        text_bg_wrapper.add(child=left_box, anchor_x="center", anchor_y="center")
        left_anchor.add(child=text_bg_wrapper, anchor_x="left", anchor_y="center", align_x=50)
        self.manager.add(left_anchor)

        # 4. SISI KANAN: GAMBAR FEATURED ITEM (RGBA FIX)
        right_anchor = arcade.gui.UIAnchorLayout()
        
        import os
        from PIL import Image as PILImage
        clean_name = featured_item.split('(')[0].split('+')[0].strip()
        safe_name = clean_name.lower().replace(" ", "_")
        
        img_widget = None
        for ext in ['.png', '.jpg', '.jpeg']:
            path = f"assets/{safe_name}{ext}"
            if os.path.exists(path):
                try:
                    pil_img = PILImage.open(path).convert("RGBA")
                    tex = arcade.Texture(name=f"banner_{safe_name}", image=pil_img)
                    
                    # Ukuran sangat besar ala karakter gacha
                    scaled_height = 450
                    scaled_width = int(tex.width * (scaled_height / tex.height))
                    
                    try:
                        img_widget = arcade.gui.UIImage(texture=tex, width=scaled_width, height=scaled_height)
                    except AttributeError:
                        sprite = arcade.Sprite()
                        sprite.texture = tex
                        sprite.scale = scaled_height / tex.height
                        img_widget = arcade.gui.UISpriteWidget(sprite=sprite, width=scaled_width, height=scaled_height)
                        
                    img_widget = img_widget.with_background(color=(0, 0, 0, 0))
                except Exception as e:
                    print(f"⚠️ Gagal load banner image: {e}")
                break
                
        if not img_widget:
            img_widget = arcade.gui.UISpace(width=300, height=300, color=(0,0,0,0))

        right_anchor.add(child=img_widget, anchor_x="right", anchor_y="center", align_x=-100)
        self.manager.add(right_anchor)

        # ==========================================
        # 5. POJOK KANAN BAWAH: TOMBOL TARIK GACHA
        # ==========================================
        btn_anchor = arcade.gui.UIAnchorLayout()
        
        # STYLE BARU: Biru Elektrik Terang dengan Teks Putih
        gacha_btn_style = {
            "normal": {
                "font_color": arcade.color.WHITE, 
                "bg_color": arcade.color.DODGER_BLUE,  # Biru terang menyala
                "border_color": arcade.color.CYAN,     # Pinggiran neon
                "border_width": 2
            },
            "hover": {
                "font_color": arcade.color.WHITE, 
                "bg_color": arcade.color.DEEP_SKY_BLUE, # Semakin terang saat kursor mendekat
                "border_color": arcade.color.WHITE, 
                "border_width": 3
            },
            "press": {
                "font_color": arcade.color.WHITE, 
                "bg_color": arcade.color.ROYAL_BLUE,    # Menggelap saat ditekan
                "border_color": arcade.color.CYAN, 
                "border_width": 2
            }
        }
        
        pull_box = arcade.gui.UIBoxLayout(vertical=True, space_between=8)
        
        # Membuat latar belakang kapsul gelap kecil untuk teks harga agar terlihat lebih rapi
        price_bg = arcade.gui.UISpace(width=140, height=30, color=(0, 0, 0, 150))
        price_label = arcade.gui.UILabel(text=f"🪙 Harga: {GachaSystem.COST_PER_PULL}", font_size=14, bold=True, text_color=arcade.color.WHITE)
        
        price_wrapper = arcade.gui.UIAnchorLayout(width=140, height=30, size_hint=(None, None))
        price_wrapper.add(child=price_bg)
        price_wrapper.add(child=price_label, anchor_x="center", anchor_y="center")
        pull_box.add(price_wrapper)
        
        # Tombol Gacha yang dipermak dengan ikon kilauan
        pull_btn = arcade.gui.UIFlatButton(text="✨ Tarik 1x ✨", width=240, height=60, style=gacha_btn_style)
        
        # Membungkus aksi klik dengan SFX
        def on_pull_sfx(event):
            if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
            self.on_pull_click(event)
            
        pull_btn.on_click = on_pull_sfx
        pull_box.add(pull_btn)
        
        btn_anchor.add(child=pull_box, anchor_x="right", anchor_y="bottom", align_x=-60, align_y=50)
        self.manager.add(btn_anchor)

        # 6. POJOK KIRI BAWAH: TOMBOL INFO DROP RATE
        info_anchor = arcade.gui.UIAnchorLayout()
        info_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": (0,0,0,150), "border_color": arcade.color.GRAY, "border_width": 1},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": (50,50,50,200), "border_color": arcade.color.WHITE, "border_width": 1},
            "press": {"font_color": arcade.color.WHITE, "bg_color": (20,20,20,200), "border_color": arcade.color.WHITE, "border_width": 1}
        }
        info_btn = arcade.gui.UIFlatButton(text="ℹ️ Rincian Drop Rate", width=200, height=45, style=info_style)
        
        def on_info_click(event):
            if hasattr(self, 'sfx_click2') and self.sfx_click2: BGMManager.play_sfx(self.sfx_click)
            self.build_info_ui() # Memanggil layar info!
            
        info_btn.on_click = on_info_click
        info_anchor.add(child=info_btn, anchor_x="left", anchor_y="bottom", align_x=50, align_y=50)
        self.manager.add(info_anchor)


    # ==========================================
    # UI STATE: INFO DROP RATE (POPUP LAYAR)
    # ==========================================
    def build_info_ui(self):
        self.manager.clear()
        
        # Background Dimmer Total
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 240))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)
        
        # Box Utama
        main_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        main_box.add(arcade.gui.UILabel(text="📊 RINCIAN DROP RATE BANNER", font_size=28, text_color=arcade.color.GOLD, bold=True))
        main_box.add(arcade.gui.UILabel(text="", height=10))
        
        # List Drop Rate (Bisa disesuaikan dengan persentase GachaSystem Anda)
        rates = [
            ("🔴 Mythic (1.0%)", "Mahkota Raja Iblis, Aegis Shield", arcade.color.RED),
            ("🟡 Legendary (5.0%)", "Pedang Iblis, Zirah Duri Beracun", arcade.color.GOLD),
            ("🔵 Rare (20.0%)", "Tombak Ksatria, Zirah Baja", arcade.color.LIGHT_BLUE),
            ("⚪ Common (74.0%)", "Pedang Kayu, Zirah Kain", arcade.color.WHITE)
        ]
        
        for title, items, color in rates:
            row = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
            row.add(arcade.gui.UILabel(text=title, font_size=20, text_color=color, bold=True))
            row.add(arcade.gui.UILabel(text=items, font_size=14, text_color=arcade.color.LIGHT_GRAY))
            main_box.add(row)
            main_box.add(arcade.gui.UILabel(text="", height=10))

        # Tombol Kembali ke Banner
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        back_btn = arcade.gui.UIFlatButton(text="Tutup & Kembali", width=250, height=50, style=cancel_style)
        
        def on_close_info(event):
            if hasattr(self, 'sfx_click2') and self.sfx_click2: BGMManager.play_sfx(self.sfx_click)
            self.build_ui() # Kembali ke layar Banner utama
            
        back_btn.on_click = on_close_info
        main_box.add(back_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=main_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    # ==========================================
    # UI STATE: REVEAL (SAAT ITEM DIDAPATKAN)
    # ==========================================
    def build_reveal_ui(self):
        self.manager.clear()
        
        # 1. Dimmer Layar Gelap
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 210))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        main_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        # Header Kemenangan
        main_box.add(arcade.gui.UILabel(text="✨ SELAMAT! ANDA MENDAPATKAN ✨", font_size=24, text_color=arcade.color.GOLD, bold=True))
        main_box.add(arcade.gui.UILabel(text="", height=10))

        # 2. Gambar RGBA Bebas Kotak
        import os
        from PIL import Image as PILImage
        clean_name = self.pulled_item_name.split('(')[0].split('+')[0].strip()
        safe_name = clean_name.lower().replace(" ", "_")
        
        img_widget = None
        for ext in ['.png', '.jpg', '.jpeg']:
            path = f"assets/{safe_name}{ext}"
            if os.path.exists(path):
                try:
                    pil_img = PILImage.open(path).convert("RGBA")
                    tex = arcade.Texture(name=f"gacha_{safe_name}", image=pil_img)
                    
                    scaled_height = 200
                    scaled_width = int(tex.width * (scaled_height / tex.height))
                    
                    try:
                        img_widget = arcade.gui.UIImage(texture=tex, width=scaled_width, height=scaled_height)
                    except AttributeError:
                        sprite = arcade.Sprite()
                        sprite.texture = tex
                        sprite.scale = scaled_height / tex.height
                        img_widget = arcade.gui.UISpriteWidget(sprite=sprite, width=scaled_width, height=scaled_height)
                        
                    img_widget = img_widget.with_background(color=(0, 0, 0, 0))
                except Exception as e:
                    print(f"⚠️ Gagal load image: {e}")
                break
                
        if not img_widget:
            img_widget = arcade.gui.UISpace(width=200, height=200, color=(30, 35, 50))

        img_anchor = arcade.gui.UIAnchorLayout(width=300, height=220, size_hint=(None, None))
        img_anchor.add(child=img_widget, anchor_x="center", anchor_y="center")
        main_box.add(img_anchor)

        # 3. Info Detail
        main_box.add(arcade.gui.UILabel(text=self.pulled_item_name, font_size=36, text_color=self.rarity_color, bold=True))
        main_box.add(arcade.gui.UILabel(text=self.pulled_item_stats, font_size=16, text_color=arcade.color.LIGHT_GREEN, bold=True))
        main_box.add(arcade.gui.UILabel(text="", height=30))

        # 4. Tombol Lanjutkan
        rpg_btn_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
        }
        btn = arcade.gui.UIFlatButton(text="Lanjutkan", width=300, height=60, style=rpg_btn_style)
        
        def on_continue_sfx(event):
            if hasattr(self, 'sfx_click2') and self.sfx_click2: BGMManager.play_sfx(self.sfx_click)
            self.on_continue_click(event)
            
        btn.on_click = on_continue_sfx
        main_box.add(btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=main_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    # ==========================================
    # LOGIKA & UPDATE
    # ==========================================
    def get_rarity_color(self, rarity):
        if rarity == "Mythic": return arcade.color.RED
        elif rarity == "Legendary": return arcade.color.GOLD
        elif rarity == "Rare": return arcade.color.LIGHT_BLUE # SUDAH DIPERBAIKI!
        else: return arcade.color.WHITE

    def on_pull_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
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
        
        SaveManager.add_equipment(self.pulled_item_name)
        
        self.manager.clear()
        BGMManager.mute_for_sfx() 
        self.state = "SHAKING"
        self.anim_timer = 2.0 
        self.chest_scale = 1.0
        self.error_msg = ""

    def on_back_click(self, event):
        if hasattr(self, 'sfx_click2') and self.sfx_click2:
            BGMManager.play_sfx(self.sfx_click)
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_continue_click(self, event):
        self.state = "IDLE"
        self.build_ui()

    def on_update(self, delta_time: float):
        self.time_elapsed += delta_time
        import math

        BGMManager.update(delta_time)
        
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
                self.build_reveal_ui() # Memanggil Antarmuka Megah!
                BGMManager.restore_volume()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def _draw_rect(self, center_x, center_y, width, height, color):
        hw, hh = width / 2, height / 2
        points = ((center_x - hw, center_y - hh), (center_x + hw, center_y - hh), 
                  (center_x + hw, center_y + hh), (center_x - hw, center_y + hh))
        arcade.draw_polygon_filled(points, color)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        sw, sh = self.window.width, self.window.height
        cx, cy = sw / 2, sh / 2

        # Animasi Peti Berguncang (Hanya saat SHAKING & FLASH)
        if self.state in ["SHAKING", "FLASH"]:
            chest_width = 100 * self.chest_scale
            chest_height = 80 * self.chest_scale
            self._draw_rect(cx + self.chest_shake_x, cy, chest_width, chest_height, arcade.color.GOLDENROD)
            self._draw_rect(cx + self.chest_shake_x, cy + 10, chest_width, 10, arcade.color.DARK_GOLDENROD) 
            arcade.draw_text("Membuka Peti...", cx, cy - 80, arcade.color.WHITE, 14, anchor_x="center")

        # Animasi Sinar Berputar (Di belakang UI REVEAL)
        elif self.state == "REVEAL":
            import math
            ray_length = 600
            ray_count = 12
            for i in range(ray_count):
                angle = self.time_elapsed + (i * (2 * math.pi / ray_count))
                end_x = cx + math.cos(angle) * ray_length
                end_y = cy + math.sin(angle) * ray_length
                # Sinar memudar cantik berkat nilai alpha 80 (transparan)
                ray_color = (*self.rarity_color[:3], 80) 
                arcade.draw_line(cx, cy, end_x, end_y, ray_color, 60)

        if self.state == "FLASH" and self.flash_alpha > 0:
            flash_color = (*self.rarity_color[:3], self.flash_alpha)
            points = ((0, 0), (sw, 0), (sw, sh), (0, sh))
            arcade.draw_polygon_filled(points, flash_color)

        # Gambar antarmuka tombol & teks dari UI Manager 
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# 3. LAYAR PILIH KESULITAN (UPDATE: FROSTED GLASS & REFACTORING)
# ==========================================
class DifficultySelectionView(arcade.View):
    def __init__(self, party_size):
        super().__init__()
        self.party_size = party_size
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        
        import os
        bg_path = "assets/bg/standart_menu_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
            
        # ==========================================
        # MUAT SFX KLIK
        # ==========================================
        click_path = "assets/sfx/click.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

        # Panggil pembuatan UI yang sudah dipisahkan agar rapi
        self.build_ui()

    def build_ui(self):
        self.manager.clear()
        
        # ==========================================
        # 1. JURUS DIMMER GLOBAL
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 190))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        # ==========================================
        # 2. PANEL KACA GELAP
        # ==========================================
        panel_width = 600
        panel_height = 420
        panel_wrapper = arcade.gui.UIAnchorLayout(width=panel_width, height=panel_height, size_hint=(None, None))
        panel_bg = arcade.gui.UISpace(width=panel_width, height=panel_height, color=(15, 20, 30, 230))
        panel_wrapper.add(child=panel_bg)

        self.v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        # Header
        self.v_box.add(arcade.gui.UILabel(text="🔥 TINGKAT KESULITAN 🔥", font_size=26, bold=True, text_color=arcade.color.GOLD))
        self.v_box.add(arcade.gui.UILabel(text="Semakin sulit, semakin banyak EXP & Gold yang didapat!", font_size=13, text_color=arcade.color.LIGHT_GRAY))
        self.v_box.add(arcade.gui.UILabel(text="", height=15))
        
        # ==========================================
        # 3. GAYA TOMBOL BERDASARKAN KESULITAN
        # ==========================================
        easy_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_GREEN, "border_color": arcade.color.LIME_GREEN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.FOREST_GREEN, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_OLIVE_GREEN, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        med_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.GOLD, "border_color": arcade.color.DARK_GOLDENROD, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.YELLOW, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_GOLDENROD, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        hard_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.MAROON, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": (50, 50, 60, 255), "border_color": arcade.color.GRAY, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": (70, 70, 80, 255), "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": (30, 30, 40, 255), "border_color": arcade.color.WHITE, "border_width": 2}
        }

        def create_diff_btn(text, style, action_func):
            btn = arcade.gui.UIFlatButton(text=text, width=480, height=50, style=style)
            btn.on_click = action_func
            return btn

        # Eksekusi Pembuatan Tombol (Suara sudah dihandle di on_easy dll)
        btn_easy = create_diff_btn("🟢 EASY (Musuh Max Lv 10  |  EXP x1.0)", easy_style, self.on_easy)
        btn_medium = create_diff_btn("🟡 MEDIUM (Musuh Max Lv 30  |  EXP x1.5)", med_style, self.on_medium)
        btn_hard = create_diff_btn("🔴 HARD (Musuh Max Lv 100  |  EXP x2.5)", hard_style, self.on_hard)
        
        # Tombol kembali butuh pembungkus SFX karena di fungsi on_back_click asli belum ada
        def on_back_wrapper(event):
            if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
            self.on_back_click(event)
            
        btn_back = create_diff_btn("Kembali ke Pemilihan Mode", cancel_style, on_back_wrapper)
        
        self.v_box.add(btn_easy)
        self.v_box.add(btn_medium)
        self.v_box.add(btn_hard)
        self.v_box.add(arcade.gui.UILabel(text="", height=10)) 
        self.v_box.add(btn_back)
        
        panel_wrapper.add(child=self.v_box, anchor_x="center", anchor_y="center")
        
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=panel_wrapper, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    # ==========================================
    # FUNGSI AKSI & LOGIKA
    # ==========================================
    def on_easy(self, event): 
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.select_diff("EASY")

    def on_medium(self, event): 
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.select_diff("MEDIUM")

    def on_hard(self, event): 
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.select_diff("HARD")

    def select_diff(self, diff):
        self.manager.disable()
        from gui.views import CharacterSelectionView # Pastikan import ada atau disesuaikan
        self.window.show_view(CharacterSelectionView(self.party_size, diff))

    def on_back_click(self, event):
        self.manager.disable()
        from gui.views import ModeSelectionView # Pastikan import ada atau disesuaikan
        self.window.show_view(ModeSelectionView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

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
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/select_standart_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None

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
            "Mage": {"stats": "HP: 80 | ATK: 20 | DEF: 4", "role": "Magic Nuke", "passive": "Mana Shield (-25% DMG diterima jika Mana > 50%)", "ulti": "Meteor Swarm (AoE masif + efek Burn)"},
            "Knight": {"stats": "HP: 160 | ATK: 10 | DEF: 12", "role": "Pure Tank", "passive": "Aegis Aura (+5% DEF tiap diserang, Max 5x)", "ulti": "Holy Judgement (DMG dari 1.5x DEF)"},
            "Valkyrie": {"stats": "HP: 90 | ATK: 15 | DEF: 4", "role": "Glass Support", "passive": "Holy Aura (Regen 10 Mana tiap giliran)", "ulti": "Hymn of Valhalla (Heal area 25% HP tanpa Kebal)"}
        }

        self.player_party = []
        self.enemy_party = []

        self.last_player_char = None
        self.last_enemy_char = None

        self.build_ui()

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_menu_standart.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

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

        # ==========================================
        # 1. JURUS DIMMER GLOBAL
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 25, 200))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        main_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=30)

        # ========================================
        # GAYA TOMBOL RPG MODERN
        # ========================================
        rpg_btn_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
        }
        
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }

        # ========================================
        # ALAT BANTU: PEMANGGIL GAMBAR (RGBA FIX)
        # ========================================
        def get_portrait_widget(char_name):
            import os
            from PIL import Image as PILImage
            if not char_name:
                return arcade.gui.UISpace(width=200, height=250, color=(0,0,0,0))
                
            clean_name = char_name.split('(')[0].split('+')[0].strip()
            safe_name = clean_name.lower().replace(" ", "_")
            
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f"assets/{safe_name}_menu{ext}"
                if not os.path.exists(path):
                    path = f"assets/{safe_name}{ext}" # Fallback
                    
                if os.path.exists(path):
                    try:
                        pil_img = PILImage.open(path).convert("RGBA")
                        tex = arcade.Texture(name=f"sel_{safe_name}", image=pil_img)
                        # Tinggi dikunci di 250px agar pas di layout tanpa merusak proporsi
                        scaled_height = 250 
                        scaled_width = int(tex.width * (scaled_height / tex.height))
                        
                        try:
                            widget = arcade.gui.UIImage(texture=tex, width=scaled_width, height=scaled_height)
                        except AttributeError:
                            sprite = arcade.Sprite()
                            sprite.texture = tex
                            sprite.scale = scaled_height / tex.height
                            widget = arcade.gui.UISpriteWidget(sprite=sprite, width=scaled_width, height=scaled_height)
                            
                        return widget.with_background(color=(0, 0, 0, 0))
                    except Exception as e:
                        print(f"⚠️ Gagal load image {path}: {e}")
                    break
            
            return arcade.gui.UISpace(width=200, height=250, color=(30, 35, 50))


        # ========================================
        # FUNGSI PEMBUAT PANEL KIRI/KANAN
        # ========================================
        def create_side_panel(is_player):
            panel_width = 340
            panel = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
            
            # 1. Header & Grid Pilihan
            party = self.player_party if is_player else self.enemy_party
            title_text = f"TIM ANDA ({len(party)}/{self.party_size})" if is_player else f"TIM LAWAN ({len(party)}/{self.party_size})"
            title_color = arcade.color.CYAN if is_player else arcade.color.CRIMSON
            
            panel.add(arcade.gui.UILabel(text=title_text, font_size=18, bold=True, text_color=title_color))
            
            grid = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
            col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
            col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=5)

            for i, char in enumerate(self.available_characters):
                btn = arcade.gui.UIFlatButton(text=f"{char[:3].upper()} {self.element_map[char]}", width=110, height=45, style=rpg_btn_style)
                btn.on_click = self.make_select_action(char, is_player=is_player)
                if i % 2 == 0: col1.add(btn)
                else: col2.add(btn)
                
            grid.add(col1)
            grid.add(col2)
            panel.add(grid)
            panel.add(arcade.gui.UILabel(text="", height=5))

            # 2. Gambar Karakter & Info Box
            last_char = self.last_player_char if is_player else self.last_enemy_char
            
            # Wadah untuk Gambar Karakter
            img_anchor = arcade.gui.UIAnchorLayout(width=panel_width, height=260, size_hint=(None, None))
            img_anchor.add(child=get_portrait_widget(last_char), anchor_x="center", anchor_y="bottom")
            panel.add(img_anchor)
            
            # Wadah Kaca Gelap untuk Teks Info (Agar selalu terbaca!)
            info_wrapper = arcade.gui.UIAnchorLayout(width=panel_width, height=140, size_hint=(None, None))
            info_bg = arcade.gui.UISpace(width=panel_width, height=140, color=(15, 20, 30, 220))
            info_wrapper.add(child=info_bg)
            
            info_box = arcade.gui.UIBoxLayout(vertical=True)
            if last_char:
                char_display = f"{self.element_map[last_char]} {last_char.upper()}"
                info_box.add(arcade.gui.UILabel(text=char_display, font_size=16, bold=True, text_color=arcade.color.WHITE))
                
                info = self.char_info[last_char]
                info_text = f"🛡️ {info['role']}  |  📊 {info['stats']}\n\n🌟 Pasif: {info['passive']}\n🔥 Ulti: {info['ulti']}"
                info_box.add(arcade.gui.UILabel(text=info_text, font_size=11, text_color=arcade.color.LIGHT_GRAY, multiline=True, width=panel_width - 20))
            else:
                info_box.add(arcade.gui.UILabel(text="Belum ada karakter dipilih", font_size=14, text_color=arcade.color.GRAY))
                
            info_wrapper.add(child=info_box, anchor_x="center", anchor_y="center")
            panel.add(info_wrapper)
            
            # 3. Sinergi & Tombol Batal
            syn_name, syn_color = self.get_synergy(party)
            syn_box = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
            
            syn_text_box = arcade.gui.UIBoxLayout(vertical=True)
            syn_text_box.add(arcade.gui.UILabel(text="Sinergi Aktif:", font_size=11, text_color=arcade.color.WHITE))
            syn_text_box.add(arcade.gui.UILabel(text=syn_name, font_size=12, bold=True, text_color=syn_color))
            
            syn_box.add(syn_text_box)
            
            if last_char:
                undo_btn = arcade.gui.UIFlatButton(text="↩️ Batal", width=100, height=35, style=cancel_style)
                undo_btn.on_click = self.on_undo_player if is_player else self.on_undo_enemy
                syn_box.add(undo_btn)
                
            panel.add(syn_box)
            return panel


        # ========================================
        # PEMBANGUNAN 3 PILAR LAYOUT
        # ========================================
        
        # PILAR KIRI
        main_layout.add(create_side_panel(is_player=True))

        # PILAR TENGAH (KONTROL)
        center_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=25)
        
        center_panel.add(arcade.gui.UILabel(text="VS", font_size=42, bold=True, text_color=arcade.color.CRIMSON))

        rand_btn = arcade.gui.UIFlatButton(text="🎲 RANDOM SEMUA", width=200, height=50, style=rpg_btn_style)
        rand_btn.on_click = self.on_random
        center_panel.add(rand_btn)

        # Papan Rantai Elemen dengan latar belakang kaca gelap mini
        element_wrapper = arcade.gui.UIAnchorLayout(width=200, height=110, size_hint=(None, None))
        element_bg = arcade.gui.UISpace(width=200, height=110, color=(15, 20, 30, 180))
        element_wrapper.add(child=element_bg)
        
        element_info = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
        element_info.add(arcade.gui.UILabel(text="⚔️ Rantai Elemen:", font_size=14, text_color=arcade.color.GOLD, bold=True))
        element_info.add(arcade.gui.UILabel(text="🔴 Api > 🌿 Daun", font_size=13, bold=True, text_color=arcade.color.WHITE))
        element_info.add(arcade.gui.UILabel(text="🌿 Daun > 🔵 Air", font_size=13, bold=True, text_color=arcade.color.LIGHT_GREEN))
        element_info.add(arcade.gui.UILabel(text="🔵 Air > 🔴 Api", font_size=13, bold=True, text_color=arcade.color.LIGHT_BLUE))
        
        element_wrapper.add(child=element_info, anchor_x="center", anchor_y="center")
        center_panel.add(element_wrapper)

        center_panel.add(arcade.gui.UILabel(text="", height=60)) # Spacer

        ready_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_GREEN, "border_color": arcade.color.LIME_GREEN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.FOREST_GREEN, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.DARK_OLIVE_GREEN, "border_color": arcade.color.GOLD, "border_width": 3}
        }

        if len(self.player_party) == self.party_size and len(self.enemy_party) == self.party_size:
            ready_btn = arcade.gui.UIFlatButton(text="✅ SELESAI", width=200, height=60, style=ready_style)
            ready_btn.on_click = self.on_ready
            center_panel.add(ready_btn)
        else:
            wait_btn = arcade.gui.UIFlatButton(text="Pilih Karakter...", width=200, height=60, style=rpg_btn_style)
            center_panel.add(wait_btn)

        back_btn = arcade.gui.UIFlatButton(text="❌ Kembali", width=200, height=45, style=cancel_style)
        back_btn.on_click = self.on_back_click
        center_panel.add(back_btn)

        main_layout.add(center_panel)

        # PILAR KANAN
        main_layout.add(create_side_panel(is_player=False))

        # Tempelkan triptych utama ke layar
        final_anchor = arcade.gui.UIAnchorLayout()
        final_anchor.add(child=main_layout, anchor_x="center", anchor_y="center")
        self.manager.add(final_anchor)

    def make_select_action(self, char_name, is_player):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
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
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        if self.player_party:
            self.player_party.pop() 
            self.last_player_char = self.player_party[-1] if self.player_party else None
            self.build_ui()

    def on_undo_enemy(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        if self.enemy_party:
            self.enemy_party.pop() 
            self.last_enemy_char = self.enemy_party[-1] if self.enemy_party else None
            self.build_ui()

    def on_random(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        import random
        while len(self.player_party) < self.party_size:
            self.player_party.append(random.choice(self.available_characters))
        while len(self.enemy_party) < self.party_size:
            self.enemy_party.append(random.choice(self.available_characters))

        self.last_player_char = self.player_party[-1]
        self.last_enemy_char = self.enemy_party[-1]
        self.build_ui()

    def on_ready(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from gui.views import EquipmentSelectionView
        self.window.show_view(EquipmentSelectionView(self.player_party, self.enemy_party, self.difficulty))

    def on_back_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from gui.views import DifficultySelectionView
        self.window.show_view(DifficultySelectionView(self.party_size))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        BGMManager.play("SELECT")

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# 4.5 LAYAR PERSIAPAN EQUIPMENT (PERBAIKAN BUG STOK & UI MODERN)
# ==========================================
class EquipmentSelectionView(arcade.View):
    def __init__(self, player_types: list, enemy_types: list, difficulty: str):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/select_standart_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None

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

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_choose_item.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

    def build_main_ui(self):
        self.manager.clear()

        # ==========================================
        # 1. JURUS DIMMER: Meredupkan Latar Belakang
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 180))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # JUDUL
        title = arcade.gui.UILabel(text="🛡️ PERSIAPAN EQUIPMENT ⚔️", text_color=arcade.color.GOLD, font_size=28, bold=True)
        self.v_box.add(title)
        
        self.v_box.add(arcade.gui.UILabel(text="Klik tombol equipment untuk mengganti perlengkapan karakter", text_color=arcade.color.LIGHT_GRAY, font_size=14, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        # ==========================================
        # ALAT BANTU: Pemanggil Gambar (Trik RGBA)
        # ==========================================
        def get_equip_thumbnail(equip_name):
            import os
            from PIL import Image as PILImage
            
            clean_name = equip_name.split('(')[0].split('+')[0].strip()
            safe_name = clean_name.lower().replace(" ", "_")
            
            widget = None
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f"assets/{safe_name}{ext}"
                if os.path.exists(path):
                    try:
                        pil_img = PILImage.open(path).convert("RGBA")
                        tex = arcade.Texture(name=path, image=pil_img)
                        scaled_width = int(tex.width * (55 / tex.height))
                        
                        try:
                            widget = arcade.gui.UIImage(texture=tex, width=scaled_width, height=55)
                        except AttributeError:
                            sprite = arcade.Sprite()
                            sprite.texture = tex
                            sprite.scale = 55 / tex.height
                            widget = arcade.gui.UISpriteWidget(sprite=sprite, width=scaled_width, height=55)
                            
                        widget = widget.with_background(color=(0, 0, 0, 0))
                        return widget
                    except Exception as e:
                        print(f"⚠️ Gagal load thumbnail {path}: {e}")
                    break
            
            if widget is None:
                widget = arcade.gui.UISpace(width=55, height=55, color=(30, 35, 50))
            return widget

        # ==========================================
        # 2. WADAH KARTU DAFTAR
        # ==========================================
        list_bg_width = 650
        list_bg_height = max(100, len(self.player_types) * 75 + 40)
        
        list_wrapper = arcade.gui.UIAnchorLayout(width=list_bg_width, height=list_bg_height, size_hint=(None, None))
        list_bg = arcade.gui.UISpace(width=list_bg_width, height=list_bg_height, color=(15, 20, 30, 220))
        list_wrapper.add(child=list_bg)
        
        list_content = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        # Ambil GachaSystem untuk mengecek Rarity
        from engine.gacha_system import GachaSystem

        # DAFTAR KARAKTER DENGAN ZONASI PRESISI
        for i, char_type in enumerate(self.player_types):
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
            current_item = self.equipped_items[i]
            
            # --- ZONA 1: LABEL NAMA KARAKTER ---
            # Dikunci di lebar 120px, teks diratakan ke KANAN agar selalu dekat dengan ikon
            lbl_zone = arcade.gui.UIAnchorLayout(width=120, height=60, size_hint=(None, None))
            lbl = arcade.gui.UILabel(text=f"{char_type}", font_size=17, bold=True, text_color=arcade.color.CYAN)
            lbl_zone.add(child=lbl, anchor_x="right", anchor_y="center")
            
            # --- ZONA 2: IKON ---
            icon_zone = arcade.gui.UIAnchorLayout(width=60, height=60, size_hint=(None, None))
            icon_zone = icon_zone.with_background(color=(0,0,0,0))
            thumbnail = get_equip_thumbnail(current_item)
            icon_zone.add(child=thumbnail, anchor_x="center", anchor_y="center")
            
            # --- MENCARI WARNA BERDASARKAN RARITY ---
            item_text_color = arcade.color.WHITE
            if current_item != "Tangan Kosong":
                item_data = GachaSystem.ITEM_POOL.get(current_item)
                if item_data:
                    rarity = item_data.get("rarity", "Common")
                    if rarity == "Mythic": item_text_color = arcade.color.RED
                    elif rarity == "Legendary": item_text_color = arcade.color.GOLD
                    elif rarity == "Rare": item_text_color = arcade.color.LIGHT_BLUE

            # --- ZONA 3: TOMBOL EQUIPMENT (WARNA DINAMIS) ---
            # Setiap tombol sekarang memiliki warnanya sendiri berdasarkan rarity item!
            rpg_btn_style = {
                "normal": {"font_color": item_text_color, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
                "hover": {"font_color": item_text_color, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
                "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
            }
            
            btn_zone = arcade.gui.UIAnchorLayout(width=320, height=60, size_hint=(None, None))
            btn = arcade.gui.UIFlatButton(text=current_item, width=320, height=55, style=rpg_btn_style)
            
            def create_open_action(index):
                original_action = self.make_open_picker_action(index)
                def wrapper(event):
                    if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
                    original_action(event)
                return wrapper
                
            btn.on_click = create_open_action(i)
            btn_zone.add(child=btn, anchor_x="center", anchor_y="center")
            
            # Masukkan zona-zona yang sudah presisi ke dalam baris
            row.add(lbl_zone)
            row.add(icon_zone)
            row.add(btn_zone)
            list_content.add(row)
            
        # Gabungkan daftar ke dalam alas kartu gelap
        list_wrapper.add(child=list_content, anchor_x="center", anchor_y="center")
        self.v_box.add(list_wrapper)

        self.v_box.add(arcade.gui.UILabel(text="", height=20))
        
        # ==========================================
        # 3. TOMBOL START PREMIUM
        # ==========================================
        ready_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_GREEN, "border_color": arcade.color.LIME_GREEN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.FOREST_GREEN, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.DARK_OLIVE_GREEN, "border_color": arcade.color.GOLD, "border_width": 3}
        }
        
        start_btn = arcade.gui.UIFlatButton(text="🔥 MASUK KE ARENA 🔥", width=400, height=60, style=ready_style)
        
        def on_start_sfx(event):
            if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
            self.on_start_battle(event)
            
        start_btn.on_click = on_start_sfx
        self.v_box.add(start_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def make_open_picker_action(self, char_idx):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        def action(event):
            self.open_item_picker(char_idx)
        return action

    def open_item_picker(self, char_idx):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
            
        self.manager.clear()
        
        # ==========================================
        # 1. DIMMER LAYAR UTAMA
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 200))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)
        
        main_window = arcade.gui.UIBoxLayout(vertical=True, space_between=25)
        
        title_text = f"✨ PERLENGKAPAN : {self.player_types[char_idx].upper()} ✨"
        main_window.add(arcade.gui.UILabel(text=title_text, font_size=24, text_color=arcade.color.GOLD, bold=True))

        from engine.gacha_system import GachaSystem
        import os
        
        grid_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=40)
        col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        valid_items = [(name, count) for name, count in self.inventory_counts.items() if count > 0 or name == "Tangan Kosong"]
            
        for i, (item_name, count) in enumerate(valid_items):
            item_data = GachaSystem.ITEM_POOL.get(item_name) if item_name != "Tangan Kosong" else None
            
            # ==========================================
            # 2. PEMBUATAN KARTU (ANTI HOVER-BUG!)
            # ==========================================
            card_width = 440
            card_height = 85
            
            card_wrapper = arcade.gui.UIAnchorLayout(width=card_width, height=card_height, size_hint=(None, None))
            
            # --- TRIK BARU: BORDER PALSU DENGAN UISpace ---
            # Layer 1 (Paling Bawah): Kotak luar warna terang sebagai "Border"
            border_bg = arcade.gui.UISpace(width=card_width, height=card_height, color=(60, 80, 110))
            card_wrapper.add(child=border_bg, anchor_x="center", anchor_y="center")
            
            # Layer 2 (Tengah): Kotak dalam warna gelap (Ukuran dikurangi 4px)
            inner_bg = arcade.gui.UISpace(width=card_width-4, height=card_height-4, color=(20, 25, 40))
            card_wrapper.add(child=inner_bg, anchor_x="center", anchor_y="center")
            
            # Layer 3 (Paling Atas): Laci Utama Konten Kartu
            card_content = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
            
           # --- ZONA 1: IKON ---
            icon_zone = arcade.gui.UIAnchorLayout(width=70, height=card_height, size_hint=(None, None))
            icon_zone = icon_zone.with_background(color=(0, 0, 0, 0))

            clean_name = item_name.split('(')[0].split('+')[0].strip()
            safe_name = clean_name.lower().replace(" ", "_")

            from PIL import Image as PILImage

            icon_widget = None
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f"assets/{safe_name}{ext}"
                if os.path.exists(path):
                    try:
                        pil_img = PILImage.open(path).convert("RGBA")
                        tex = arcade.Texture(name=path, image=pil_img)
                        
                        scaled_width = int(tex.width * (55 / tex.height))
                        
                        try:
                            icon_widget = arcade.gui.UIImage(
                                texture=tex,
                                width=scaled_width,
                                height=55
                            )
                        except AttributeError:
                            item_sprite = arcade.Sprite()
                            item_sprite.texture = tex
                            item_sprite.scale = 55 / tex.height
                            icon_widget = arcade.gui.UISpriteWidget(
                                sprite=item_sprite,
                                width=scaled_width,
                                height=55
                            )
                        
                        icon_widget = icon_widget.with_background(color=(0, 0, 0, 0))
                    except Exception as e:
                        print(f"⚠️ Gagal load icon {path}: {e}")
                    break

            if icon_widget is None:
                icon_widget = arcade.gui.UISpace(width=55, height=55, color=(30, 35, 50))

            icon_zone.add(child=icon_widget, anchor_x="center", anchor_y="center")
            card_content.add(icon_zone)
            
            # --- ZONA 2: TEKS ---
            text_zone = arcade.gui.UIAnchorLayout(width=230, height=card_height, size_hint=(None, None))
            info_box = arcade.gui.UIBoxLayout(vertical=True)
            info_box.add(arcade.gui.UISpace(height=8)) 
            
            if item_name == "Tangan Kosong":
                info_box.add(arcade.gui.UILabel(text="Tangan Kosong", font_size=15, text_color=arcade.color.WHITE, bold=True, width=230))
                info_box.add(arcade.gui.UILabel(text="Lepaskan perlengkapan", font_size=11, text_color=arcade.color.GRAY, width=230, multiline=True))
            else:
                rarity = item_data.get("rarity", "Common")
                color = arcade.color.WHITE
                if rarity == "Mythic": color = arcade.color.RED
                elif rarity == "Legendary": color = arcade.color.GOLD
                elif rarity == "Rare": color = arcade.color.LIGHT_BLUE
                
                info_box.add(arcade.gui.UILabel(text=f"{item_name}", font_size=15, text_color=color, bold=True, width=230))
                desc = item_data.get("desc", "Tanpa efek")
                info_box.add(arcade.gui.UILabel(text=desc, font_size=11, text_color=arcade.color.LIGHT_GREEN, width=230, multiline=True))
            
            text_zone.add(child=info_box, anchor_x="left", anchor_y="center")
            card_content.add(text_zone)
            
            # --- ZONA 3: TOMBOL PAKAI (TETAP INTERAKTIF) ---
            btn_zone = arcade.gui.UIAnchorLayout(width=100, height=card_height, size_hint=(None, None))
            btn_text = "Lepas" if item_name == "Tangan Kosong" else f"Pakai ({count})"
            
            rpg_button_style = {
                "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
                "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
                "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
            }
            
            btn = arcade.gui.UIFlatButton(text=btn_text, width=90, height=45, style=rpg_button_style)
            btn.on_click = self.make_select_item_action(char_idx, item_name)
            
            btn_zone.add(child=btn, anchor_x="center", anchor_y="center")
            card_content.add(btn_zone)
            
            # Tempel Konten (Layer 3) ke Wadah Utama
            card_wrapper.add(child=card_content, anchor_x="center", anchor_y="center")
            
            if i % 2 == 0:
                col1.add(card_wrapper)
            else:
                col2.add(card_wrapper)
                
        grid_layout.add(col1)
        grid_layout.add(col2)
        main_window.add(grid_layout)
        
        main_window.add(arcade.gui.UILabel(text="", height=10))
        
        # ==========================================
        # 3. TOMBOL BATAL BAWAH
        # ==========================================
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        back_btn = arcade.gui.UIFlatButton(text="❌ BATAL & KEMBALI", width=300, height=50, style=cancel_style)
        
        def on_back(event):
            if hasattr(self, 'sfx_click') and self.sfx_click:
                BGMManager.play_sfx(self.sfx_click)
            self.build_main_ui()
            
        back_btn.on_click = on_back
        main_window.add(back_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=main_window, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def make_select_item_action(self, char_idx, item_name):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
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
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
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
                
            # ==========================================
            # FIX BUG: TEMPELKAN LABEL NAMA SENJATA SECARA PAKSA!
            # ==========================================
            char.equipped_name = eq_name 
                    
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
            # Akan otomatis menyesuaikan dengan Easy / Normal / Hard!
            random_eq = GachaSystem.get_enemy_equipment(self.difficulty, 0)
            eq_data = GachaSystem.ITEM_POOL[random_eq]

            # LAPISAN 1: Musuh pakai Equipment acak
            char = Equipment(char, item_name=random_eq, bonus_atk=eq_data["bonus_atk"], bonus_def=eq_data["bonus_def"])
            
            # LAPISAN 2: Sinergi Musuh (Awas kalau musuh dapat Inferno!)
            if e_synergy:
                char = SynergyBuff(char, synergy_type=e_synergy)
                
            enemy_party.append(char)
            enemy_party[i] = char

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
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height


# ==========================================
# 5. LAYAR GAME OVER (UPDATE HADIAH EXP)
# ==========================================
class GameOverView(arcade.View):
    def __init__(self, winner_name: str, loser_name: str, winner_hp: int, is_player_win: bool, difficulty: str, player_types: list):
        super().__init__()
        
        HistoryManager.save_match(winner_name, loser_name, winner_hp)
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/game_over_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_game_over.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

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
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        BGMManager.play("MENU")
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# LAYAR INVENTORY (REDESAIN: GRID & DETAILS PANE)
# ==========================================
class InventoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/inventory_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
        
        # Ambil data dari penyimpanan
        raw_inventory = SaveManager.get_inventory()
        self.item_counts = {}
        for item in raw_inventory:
            self.item_counts[item] = self.item_counts.get(item, 0) + 1
            
        # Tentukan item yang sedang dipilih pertama kali (jika ada)
        self.selected_item = list(self.item_counts.keys())[0] if self.item_counts else None
        
        # Panggil fungsi perakit UI
        self.build_ui()

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_choose_item.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

    def build_ui(self):
        self.manager.clear()
        
        # ==========================================
        # 1. JURUS DIMMER: Menggelapkan Ruangan
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 180))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)
        
        main_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=40)

        from engine.gacha_system import GachaSystem
        import os
        from PIL import Image as PILImage

        # ==========================================
        # 2. PANEL KIRI: TAS INVENTORY (KOTAK GELAP)
        # ==========================================
        left_bg_width = 400
        left_bg_height = 550
        
        left_wrapper = arcade.gui.UIAnchorLayout(width=left_bg_width, height=left_bg_height, size_hint=(None, None))
        # Background panel kiri (Hitam Kebiruan Transparan)
        left_bg = arcade.gui.UISpace(width=left_bg_width, height=left_bg_height, color=(15, 20, 30, 230))
        left_wrapper.add(child=left_bg)
        
        left_content = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        left_content.add(arcade.gui.UILabel(text="🎒 DAFTAR EQUIPMENT", text_color=arcade.color.GOLD, font_size=22, bold=True))
        left_content.add(arcade.gui.UILabel(text="", height=10))

        if not self.item_counts:
            left_content.add(arcade.gui.UILabel(text="Inventory Anda kosong.", text_color=arcade.color.WHITE, font_size=16, bold=True))
        else:
            items_per_row = 4
            current_row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
            
            for i, (item_name, count) in enumerate(self.item_counts.items()):
                if i % items_per_row == 0 and i != 0:
                    left_content.add(current_row)
                    current_row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
                
                clean_name = item_name.split('(')[0].split('+')[0].strip()
                safe_name = clean_name.lower().replace(" ", "_")
                
                tex = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    path = f"assets/{safe_name}{ext}"
                    if os.path.exists(path):
                        try:
                            # Memuat RGBA untuk tombol grid
                            pil_img = PILImage.open(path).convert("RGBA")
                            tex = arcade.Texture(name=path, image=pil_img)
                        except Exception as e:
                            print(f"⚠️ Gagal load {path}: {e}")
                        break

                if tex:
                    # UITextureButton otomatis menangani transparansi RGBA
                    btn = arcade.gui.UITextureButton(texture=tex, width=70, height=70)
                else:
                    btn_text = f"{item_name[:5]}..\nx{count}"
                    btn = arcade.gui.UIFlatButton(text=btn_text, width=70, height=70)
                
                # Trik SFX saat memilih item di inventory
                def create_select_action(name):
                    original_action = self.make_select_action(name)
                    def wrapper(event):
                        if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
                        original_action(event)
                    return wrapper
                    
                btn.on_click = create_select_action(item_name)
                current_row.add(btn)
                
            left_content.add(current_row)

        left_content.add(arcade.gui.UILabel(text="", height=30))
        
        # Tombol Batal bergaya Premium
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        back_btn = arcade.gui.UIFlatButton(text="❌ KEMBALI KE MENU", width=320, height=50, style=cancel_style)
        
        def on_back_sfx(event):
            if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
            self.on_back_click(event)
            
        back_btn.on_click = on_back_sfx
        left_content.add(back_btn)

        left_wrapper.add(child=left_content, anchor_x="center", anchor_y="center")
        main_layout.add(left_wrapper)


        # ==========================================
        # 3. PANEL KANAN: DETAIL ITEM (KOTAK GELAP)
        # ==========================================
        right_bg_width = 500
        right_bg_height = 550
        
        right_wrapper = arcade.gui.UIAnchorLayout(width=right_bg_width, height=right_bg_height, size_hint=(None, None))
        right_bg = arcade.gui.UISpace(width=right_bg_width, height=right_bg_height, color=(15, 20, 30, 230))
        right_wrapper.add(child=right_bg)
        
        right_content = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        
        if self.selected_item:
            item_data = GachaSystem.ITEM_POOL.get(self.selected_item)
            
            if item_data:
                clean_name = self.selected_item.split('(')[0].split('+')[0].strip()
                safe_name = clean_name.lower().replace(" ", "_")
                
                # --- SIHIR GAMBAR TRANSPARAN ANDA ---
                img_widget = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    path = f"assets/{safe_name}{ext}"
                    if os.path.exists(path):
                        try:
                            pil_img = PILImage.open(path).convert("RGBA")
                            tex_large = arcade.Texture(name=f"{path}_large", image=pil_img)
                            
                            scaled_height = 180
                            scaled_width = int(tex_large.width * (scaled_height / tex_large.height))
                            
                            try:
                                img_widget = arcade.gui.UIImage(texture=tex_large, width=scaled_width, height=scaled_height)
                            except AttributeError:
                                preview_sprite = arcade.Sprite()
                                preview_sprite.texture = tex_large
                                preview_sprite.scale = scaled_height / tex_large.height
                                img_widget = arcade.gui.UISpriteWidget(sprite=preview_sprite, width=scaled_width, height=scaled_height)
                            
                            # Mematikan background agar tidak ada kotak putih!
                            img_widget = img_widget.with_background(color=(0, 0, 0, 0))
                        except Exception as e:
                            print(f"⚠️ Gagal load preview {path}: {e}")
                        break
                
                if img_widget:
                    right_content.add(img_widget)
                else:
                    right_content.add(arcade.gui.UISpace(width=180, height=180, color=(30, 35, 50)))
                
                # --- WARNA TEKS BERDASARKAN RARITY ---
                rarity = item_data["rarity"]
                color = arcade.color.WHITE
                if rarity == "Mythic": color = arcade.color.RED
                elif rarity == "Legendary": color = arcade.color.GOLD
                elif rarity == "Rare": color = arcade.color.LIGHT_BLUE
                
                right_content.add(arcade.gui.UILabel(text=f"{self.selected_item}", text_color=color, font_size=32, bold=True))
                right_content.add(arcade.gui.UILabel(text=f"Rank: {rarity} | Dimiliki: {self.item_counts[self.selected_item]}x", text_color=arcade.color.LIGHT_GRAY, font_size=14, bold=True))
                
                right_content.add(arcade.gui.UILabel(text="", height=15))
                
                right_content.add(arcade.gui.UILabel(text="Atribut:", text_color=arcade.color.GOLD, font_size=18, bold=True))
                # Menggunakan multiline=True agar atribut panjang tidak terpotong
                right_content.add(arcade.gui.UILabel(text=f"👉 {item_data['desc']}", text_color=arcade.color.LIGHT_GREEN, font_size=16, bold=True, multiline=True, width=450))
                
                right_content.add(arcade.gui.UILabel(text="", height=15)) 
                
                right_content.add(arcade.gui.UILabel(text="Kisah Item:", text_color=arcade.color.GOLD, font_size=18, bold=True))
                # Kisah item dibungkus dengan multiline=True agar tertata rapi seperti paragraf
                right_content.add(arcade.gui.UILabel(text=f'"{item_data["lore"]}"', text_color=arcade.color.WHITE, font_size=14, multiline=True, width=450))

        right_wrapper.add(child=right_content, anchor_x="center", anchor_y="center")
        main_layout.add(right_wrapper)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=main_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def make_select_action(self, item_name):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        def action(event):
            # Update state item yang dipilih dan gambar ulang (refresh) UI-nya
            self.selected_item = item_name
            self.build_ui()
        return action

    def on_back_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        # Menggunakan lazy import agar tidak circular
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

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
        
        self.bgm_player = None

        self.mode = "Endless" if endless_floor > 0 else "Normal"

        if self.mode == "Endless":
            BGMManager.play("BATTLE_ENDLESS")
        else:
            BGMManager.play("BATTLE")

        # --- PERSIAPAN BACKGROUND DINAMIS ---
        self.bg_sprite_list = arcade.SpriteList()
        import os
        
        # Cek Mode: Jika Endless, pakai gambar khusus Endless!
        if self.difficulty == "Endless":
            bg_path = "assets/bg/endless_arena.png"
        else:
            bg_path = "assets/bg/arena_bg.jpg" 
        
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None

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

        # --- TERAPKAN LEVEL & SCALING STATUS PEMAIN ---
        from engine.save_manager import SaveManager
        
        # FIX: Gunakan enumerate untuk mengambil char_type asli dari self.player_types
        for i, char in enumerate(self.player_party):
            inner_char = char
            while hasattr(inner_char, 'character'):
                inner_char = inner_char.character
                
            # Gunakan nama asli ("Emperor"), bukan nama display ("Emperor (P1)")
            base_name = self.player_types[i]
            
            # Ambil level dari file JSON
            inner_char.level = SaveManager.get_character_data(base_name).get("level", 1)
            
            if not getattr(inner_char, 'is_scaled', False):
                stat_mult = 1.0 + ((inner_char.level - 1) * 0.1) 
                if hasattr(inner_char, 'apply_scaling'):
                    inner_char.apply_scaling(level=inner_char.level, stat_multiplier=stat_mult)
                inner_char.is_scaled = True
            
        # --- ATUR LEVEL MUSUH ---
        for char in self.enemy_party:
            inner_enemy = char
            while hasattr(inner_enemy, 'character'):
                inner_enemy = inner_enemy.character
                
            if not hasattr(inner_enemy, 'level'):
                inner_enemy.level = max(1, self.endless_floor // 2) if self.endless_floor > 0 else 1
        
        # Muat gambar karakter untuk pertama kalinya
        self.refresh_sprites()

        # Fungsi pintar untuk memuat SFX
        def load_sfx(name):
            path = f"assets/sfx/{name}"
            return arcade.load_sound(path) if os.path.exists(path) else None

        self.sfx_attack = load_sfx("attack.mp3")
        self.sfx_skill = load_sfx("skill.mp3")
        self.sfx_heal = load_sfx("heal.mp3")
        self.sfx_ulti = load_sfx("ulti.mp3")
        self.sfx_click = load_sfx("roster.mp3")

    def refresh_sprites(self):
        """Memuat ulang gambar karakter yang sedang aktif di arena."""
        if not hasattr(self, 'battler_sprites'):
            self.battler_sprites = arcade.SpriteList()
            
        self.battler_sprites.clear()
        import os

        def get_base_name(char):
            full_name = char.name
            
            # Hapus suffix "(P1)", "(Musuh 1)" dll
            clean = full_name.split('(')[0].strip()
            
            # Jika format "Lantai X NamaKarakter", ambil kata TERAKHIR
            known_chars = ["emperor", "gladiator", "assassin", "mage", "knight", "valkyrie"]
            words = clean.lower().split()
            
            for word in reversed(words):  # Cari dari belakang
                if word in known_chars:
                    return word
    
            # Fallback: ambil kata pertama
            return words[0] if words else "emperor" 

        def find_image(name):
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f"assets/{name}{ext}"
                if os.path.exists(path):
                    return path
            return None

        # 1. SETUP GAMBAR PEMAIN (KIRI)
        p1_name = get_base_name(self.p1_active)
        p1_path = find_image(p1_name)
        
        if p1_path:
            self.p1_sprite = arcade.Sprite(p1_path)
            # Kunci tinggi karakter di 360 pixel
            self.p1_base_scale = 360 / self.p1_sprite.texture.height
            self.p1_sprite.scale = self.p1_base_scale
        else:
            self.p1_sprite = arcade.SpriteSolidColor(width=120, height=180, color=arcade.color.CYAN)
            self.p1_base_scale = 1.0 # Cadangan jika tidak ada gambar
            
        self.p1_sprite.center_x = self.p1_base_x
        self.p1_sprite.center_y = self.base_y + 130  
        self.battler_sprites.append(self.p1_sprite)

        # 2. SETUP GAMBAR MUSUH (KANAN)
        p2_name = get_base_name(self.p2_active)
        p2_path = find_image(p2_name)
        
        if p2_path:
            self.p2_sprite = arcade.Sprite(p2_path)
            self.p2_base_scale = 360 / self.p2_sprite.texture.height
            self.p2_sprite.scale = self.p2_base_scale
            self.p2_sprite.texture = self.p2_sprite.texture.flip_left_right()
        else:
            self.p2_sprite = arcade.SpriteSolidColor(width=120, height=180, color=arcade.color.RED)
            self.p2_base_scale = 1.0
            
        self.p2_sprite.center_x = self.p2_base_x
        self.p2_sprite.center_y = self.base_y + 130
        self.battler_sprites.append(self.p2_sprite)

    def build_ui(self):
        self.manager.clear()
        
        # ==========================================
        # FUNGSI KREATIF: Membuat Kartu Roster Wajah + Mini Bar
        # ==========================================
        def create_roster_card(char, status, click_action=None):
            card = arcade.gui.UIBoxLayout(vertical=False, space_between=8)
            
            # 1. Cari Gambar Wajah (Portrait)
            import os
            base_name = char.name.split()[0].lower()
            face_tex = None
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f"assets/{base_name}_menu{ext}"
                if os.path.exists(path):
                    face_tex = arcade.load_texture(path)
                    break
            
            # Buat Tombol Wajah
            if face_tex:
                btn = arcade.gui.UITextureButton(texture=face_tex, width=55, height=55)
            else:
                btn = arcade.gui.UIFlatButton(text=base_name[:3], width=55, height=55)
                
            if click_action and status != "DEAD":
                btn.on_click = click_action
            card.add(btn)
            
            # 2. Buat Info Status & Mini Bar Retro
            info = arcade.gui.UIBoxLayout(vertical=True)
            if status == "DEAD":
                info.add(arcade.gui.UILabel(text="💀 DEAD", text_color=arcade.color.GRAY, font_size=12, bold=True))
            else:
                prefix = "▶ " if status == "ACTIVE" else "🔄 "
                color = arcade.color.YELLOW if status == "ACTIVE" else arcade.color.WHITE
                info.add(arcade.gui.UILabel(text=f"{prefix}{char.name.split()[0]}", text_color=color, font_size=12, bold=True))
                
                # Mini Bar HP (Merah)
                hp_bars = int((max(0, char.current_hp) / char._max_hp) * 10)
                hp_str = "█" * hp_bars + "░" * (10 - hp_bars)
                info.add(arcade.gui.UILabel(text=hp_str, text_color=arcade.color.RED, font_size=10))
                
                # Mini Bar Mana (Biru)
                mp_bars = int((max(0, char.current_mana) / char._max_mana) * 10)
                mp_str = "█" * mp_bars + "░" * (10 - mp_bars)
                info.add(arcade.gui.UILabel(text=mp_str, text_color=arcade.color.ROYAL_BLUE, font_size=10))
                
            card.add(info)
            return card

        # ==========================================
        # PENERAPAN KE PANEL KIRI & KANAN
        # ==========================================
        # PANEL ROSTER PEMAIN (KIRI)
        left_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        for i, char in enumerate(self.player_party):
            status = "DEAD" if char.current_hp <= 0 else ("ACTIVE" if i == self.p1_idx else "WAIT")
            action = self.make_swap_action(i) if status == "WAIT" else None
            left_box.add(create_roster_card(char, status, action))
            
        anchor_left = arcade.gui.UIAnchorLayout()
        anchor_left.add(child=left_box, anchor_x="left", anchor_y="center", align_x=20)
        self.manager.add(anchor_left)

        # PANEL ROSTER MUSUH (KANAN) 
        right_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        for i, char in enumerate(self.enemy_party):
            status = "DEAD" if char.current_hp <= 0 else ("ACTIVE" if i == self.p2_idx else "WAIT")
            right_box.add(create_roster_card(char, status, None)) # Musuh tidak bisa diklik
            
        anchor_right = arcade.gui.UIAnchorLayout()
        anchor_right.add(child=right_box, anchor_x="right", anchor_y="center", align_x=-20)
        self.manager.add(anchor_right)

        # ==========================================
        # TOMBOL AKSI UTAMA (BAWAH)
        # ==========================================
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
            # Jika bukan giliran pemain, tombol tidak akan merespons
            if not self.is_player_turn: return
            
            # --- MAIN SFX UI KLIK ---
            if hasattr(self, 'sfx_click') and self.sfx_click:
                # Volume diset 0.5 agar tidak terlalu berisik
                BGMManager.play_sfx(self.sfx_click) 
            
            old_char = self.p1_active
            target_char = self.player_party[target_idx]
            
            self.p1_idx = target_idx
            self.p1_active = target_char
            self.update_layout() 
            
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
        
        # FIX PRESISI 1: Geser karakter agar lebih proporsional (28% dari Kiri, 72% dari Kanan)
        self.p1_base_x = sw * 0.28
        self.p2_base_x = sw * 0.72
        self.base_y = sh * 0.45
        
        self.refresh_sprites()

        # FIX PRESISI 2: Hapus "- 125". Gunakan koordinat base_x langsung agar benar-benar di tengah!
        # Ukuran bar juga kita rapikan.
        self.p1_hp_bar = StatusBar(self.p1_active, x=self.p1_base_x, y=self.base_y + 200, width=220, height=18, is_mana=False)
        self.p1_mana_bar = StatusBar(self.p1_active, x=self.p1_base_x, y=self.base_y + 175, width=180, height=12, is_mana=True)
        
        self.p2_hp_bar = StatusBar(self.p2_active, x=self.p2_base_x, y=self.base_y + 200, width=220, height=18, is_mana=False)
        self.p2_mana_bar = StatusBar(self.p2_active, x=self.p2_base_x, y=self.base_y + 175, width=180, height=12, is_mana=True)

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
        self.refresh_sprites()
        if self.p2_active.current_hp <= 0:
            alive_enemies = [i for i, c in enumerate(self.enemy_party) if c.current_hp > 0]
            if not alive_enemies:
                self.manager.disable()
                BGMManager.play("MENU")
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
                BGMManager.play("MENU")
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
            # --- MAIN SFX ATTACK ---
            if hasattr(self, 'sfx_attack') and self.sfx_attack:
                BGMManager.play_sfx(self.sfx_attack)
                
            self.attack_anim_timer = 0.3 
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
            # --- MAIN SFX SKILL ---
            if hasattr(self, 'sfx_skill') and self.sfx_skill:
                BGMManager.play_sfx(self.sfx_skill)
                
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
            # --- MAIN SFX HEAL ---
            if hasattr(self, 'sfx_heal') and self.sfx_heal:
                BGMManager.play_sfx(self.sfx_heal)
                
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
                # --- MAIN SFX ULTIMATE ---
                if hasattr(self, 'sfx_ulti') and self.sfx_ulti:
                    BGMManager.play_sfx(self.sfx_ulti)
                    
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
        # FIX: Tambahkan efek bernapas ke ukuran DASAR, bukan ke 1.0
        breath_effect = math.sin(self.time_elapsed * 3) * 0.02
        
        if hasattr(self, 'p1_base_scale'):
            self.p1_sprite.scale = self.p1_base_scale + (self.p1_base_scale * breath_effect)
        if hasattr(self, 'p2_base_scale'):
            self.p2_sprite.scale = self.p2_base_scale + (self.p2_base_scale * breath_effect)
        
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
        # MENGGAMBAR BACKGROUND ARENA
        if self.bg_sprite:
            self.bg_sprite_list.draw()
            
        # Gambar karakter petarung
        if hasattr(self, 'battler_sprites'):
            # FIX ANIMASI: Sinkronkan posisi gambar dengan koordinat animasi
            if hasattr(self, 'p1_sprite'):
                self.p1_sprite.center_x = self.p1_base_x
            if hasattr(self, 'p2_sprite'):
                self.p2_sprite.center_x = self.p2_base_x
                
            self.battler_sprites.draw()
        
        # ==========================================
        # FIX: MENGGALI KE KARAKTER INTI UNTUK MEMBACA LEVEL ASLI
        # ==========================================
        def get_real_level(c):
            inner = c
            while hasattr(inner, 'character'): # Tembus semua lapis equipment
                inner = inner.character
            return getattr(inner, 'level', 1)

        p1_lvl = get_real_level(self.p1_active)
        p2_lvl = get_real_level(self.p2_active)
        
        # Ubah posisi Y menjadi self.base_y + 230
        arcade.Text(f"{self.p1_active.name} (Lv.{p1_lvl})", x=self.p1_base_x, y=self.base_y + 230, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        arcade.Text(f"{self.p2_active.name} (Lv.{p2_lvl})", x=self.p2_base_x, y=self.base_y + 230, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        
        # INFO LANTAI ENDLESS (Muncul di atas tengah layar)
        if self.endless_floor > 0:
            arcade.Text(f"ENDLESS TOWER - LANTAI {self.endless_floor}", x=self.window.width/2, y=self.window.height - 40, color=arcade.color.GOLD, font_size=22, bold=True, anchor_x="center").draw()
        
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

    def on_resize(self, width: int, height: int):
        """Fungsi bawaan Arcade yang dipanggil saat layar berubah ukuran."""
        super().on_resize(width, height)
        
        # Paksa gambar background menyesuaikan ukuran layar baru
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

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

        # --- BACKGROUND KHUSUS MENU ENDLESS ---
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/endless_menu.jpg" # Nama gambar khusus menu endless
        
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None

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
            "Mage": {"stats": "HP: 80 | ATK: 20 | DEF: 4", "role": "Magic Nuke", "passive": "Mana Shield (-25% DMG diterima jika Mana > 50%)", "ulti": "Meteor Swarm (AoE masif + efek Burn)"},
            "Knight": {"stats": "HP: 160 | ATK: 10 | DEF: 12", "role": "Pure Tank", "passive": "Aegis Aura (+5% DEF tiap diserang, Max 5x)", "ulti": "Holy Judgement (DMG dari 1.5x DEF)"},
            "Valkyrie": {"stats": "HP: 90 | ATK: 15 | DEF: 4", "role": "Glass Support", "passive": "Holy Aura (Regen 10 Mana tiap giliran)", "ulti": "Hymn of Valhalla (Heal area 25% HP tanpa Kebal)"}
        }

        self.player_party = []
        self.last_player_char = None
        self.preview_sprite = None 
        
        # FIX ARCADE 3.0: Siapkan wadah untuk menggambar sprite
        self.sprite_list = arcade.SpriteList()

        self.build_ui()

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_endless_mode.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

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
        
        # Bersihkan sprite list lama (jika Anda masih memanggilnya di fungsi on_draw)
        # Karena sekarang gambar karakternya akan dikendalikan 100% oleh UI Manager!
        if hasattr(self, 'sprite_list'):
            self.sprite_list.clear()

        # ==========================================
        # 1. JURUS DIMMER: Menggelapkan Background Kuil
        # ==========================================
        dimmer = arcade.gui.UISpace(width=self.window.width, height=self.window.height, color=(10, 15, 20, 200))
        dimmer_anchor = arcade.gui.UIAnchorLayout()
        dimmer_anchor.add(child=dimmer, anchor_x="center", anchor_y="center")
        self.manager.add(dimmer_anchor)

        # ==========================================
        # PERSIAPAN GAYA TOMBOL RPG (DICTIONARY)
        # ==========================================
        rpg_btn_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_SLATE_BLUE, "border_color": arcade.color.CYAN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.ROYAL_BLUE, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.MIDNIGHT_BLUE, "border_color": arcade.color.GOLD, "border_width": 3}
        }
        
        cancel_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.CRIMSON, "border_color": arcade.color.DARK_RED, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.RED, "border_color": arcade.color.WHITE, "border_width": 2},
            "press": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_RED, "border_color": arcade.color.WHITE, "border_width": 2}
        }
        
        ready_style = {
            "normal": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.DARK_GREEN, "border_color": arcade.color.LIME_GREEN, "border_width": 2},
            "hover": {"font_color": arcade.color.WHITE, "bg_color": arcade.color.FOREST_GREEN, "border_color": arcade.color.GOLD, "border_width": 2},
            "press": {"font_color": arcade.color.GOLD, "bg_color": arcade.color.DARK_OLIVE_GREEN, "border_color": arcade.color.GOLD, "border_width": 3}
        }

        # ==========================================
        # 2. PANEL KIRI: PEMILIHAN TIM (DENGAN KARTU)
        # ==========================================
        # Background kartu agar daftar tim lebih elegan
        left_card_bg = arcade.gui.UISpace(width=280, height=450, color=(15, 20, 30, 220))
        left_card_anchor = arcade.gui.UIAnchorLayout(width=280, height=450, size_hint=(None, None))
        left_card_anchor.add(child=left_card_bg)
        
        left_content = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        left_content.add(arcade.gui.UILabel(text=f"🛡️ TIM ENDLESS ({len(self.player_party)}/3)", font_size=16, bold=True, text_color=arcade.color.GOLD))
        left_content.add(arcade.gui.UILabel(text="", height=5))

        p_grid = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        p_col1 = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        p_col2 = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        for i, char in enumerate(self.available_characters):
            btn = arcade.gui.UIFlatButton(text=f"{char[:3].upper()} {self.element_map[char]}", width=110, height=45, style=rpg_btn_style)
            
            # Trik memasukkan SFX ke dalam aksi tombol otomatis
            def create_click_action(char_name):
                original_action = self.make_select_action(char_name)
                def wrapper(event):
                    if hasattr(self, 'sfx_click') and self.sfx_click:
                        BGMManager.play_sfx(self.sfx_click)
                    original_action(event)
                return wrapper
                
            btn.on_click = create_click_action(char)
            
            if i % 2 == 0: p_col1.add(btn)
            else: p_col2.add(btn)
            
        p_grid.add(p_col1)
        p_grid.add(p_col2)
        left_content.add(p_grid)

        left_content.add(arcade.gui.UILabel(text="", height=20))
        
        if self.player_party:
            undo_btn = arcade.gui.UIFlatButton(text="↩️ Batal Pilihan", width=230, height=45, style=cancel_style)
            def on_undo_sfx(event):
                if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
                self.on_undo(event)
            undo_btn.on_click = on_undo_sfx
            left_content.add(undo_btn)
            
        left_content.add(arcade.gui.UILabel(text="", height=10))
        syn_name, syn_color = self.get_synergy(self.player_party)
        left_content.add(arcade.gui.UILabel(text="Sinergi Aktif:", font_size=13, text_color=arcade.color.LIGHT_GRAY))
        left_content.add(arcade.gui.UILabel(text=syn_name, font_size=15, bold=True, text_color=syn_color))

        left_card_anchor.add(child=left_content, anchor_x="center", anchor_y="center")

        anchor_left = arcade.gui.UIAnchorLayout()
        anchor_left.add(child=left_card_anchor, anchor_x="left", anchor_y="center", align_x=40)
        self.manager.add(anchor_left)

        # ==========================================
        # 3. PANEL TENGAH: KONTROL UTAMA
        # ==========================================
        center_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        title = arcade.gui.UILabel(text="ENDLESS TOWER", font_size=36, bold=True, text_color=arcade.color.CRIMSON)
        center_panel.add(title)
        center_panel.add(arcade.gui.UILabel(text="Hadapi musuh tanpa batas!", font_size=16, text_color=arcade.color.LIGHT_GRAY))
        center_panel.add(arcade.gui.UILabel(text="", height=40))

        if len(self.player_party) == 3:
            ready_btn = arcade.gui.UIFlatButton(text="⚔️ MASUK KE MENARA", width=250, height=60, style=ready_style)
            def on_ready_sfx(event):
                if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
                self.on_ready(event)
            ready_btn.on_click = on_ready_sfx
            center_panel.add(ready_btn)
        else:
            dummy_btn = arcade.gui.UIFlatButton(text="Pilih 3 Karakter...", width=250, height=60, style=rpg_btn_style)
            center_panel.add(dummy_btn)

        back_btn = arcade.gui.UIFlatButton(text="❌ Kembali", width=250, height=50, style=cancel_style)
        def on_back_sfx(event):
            if hasattr(self, 'sfx_click') and self.sfx_click: BGMManager.play_sfx(self.sfx_click)
            self.on_back_click(event)
        back_btn.on_click = on_back_sfx
        center_panel.add(back_btn)

        anchor_center = arcade.gui.UIAnchorLayout()
        anchor_center.add(child=center_panel, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_center)

        # ==========================================
        # 4. PANEL KANAN: PREVIEW KARAKTER RAKSASA (FIXED)
        # ==========================================
        # Kita menggunakan space_between=0 agar gambar karakter "berdiri" tepat di atas kotak infonya
        right_panel = arcade.gui.UIBoxLayout(vertical=True, space_between=0)
        
        if self.last_player_char:
            info = self.char_info[self.last_player_char]
            import os
            
            # --- ZONA FOTO KARAKTER (DENGAN PAWANG SKALA) ---
            def find_menu_image(name):
                for ext in ['.png', '.jpg', '.jpeg']:
                    path = f"assets/{name.lower()}_menu{ext}"
                    if os.path.exists(path): return path
                return None

            menu_path = find_menu_image(self.last_player_char)
            # ZONA FOTO KARAKTER — GANTI SELURUH BLOK INI
            menu_path = find_menu_image(self.last_player_char)
            if menu_path:
                from PIL import Image as PILImage
                
                pil_img = PILImage.open(menu_path).convert("RGBA")
                tex = arcade.Texture(name=menu_path, image=pil_img)
                
                scaled_height = 450
                scaled_width = int(tex.width * (scaled_height / tex.height))
                
                # Coba pakai UIImage (ada di beberapa versi Arcade)
                try:
                    img_widget = arcade.gui.UIImage(
                        texture=tex,
                        width=scaled_width,
                        height=scaled_height
                    )
                except AttributeError:
                    # Fallback ke UISpriteWidget
                    preview_sprite = arcade.Sprite()
                    preview_sprite.texture = tex
                    preview_sprite.scale = scaled_height / tex.height
                    img_widget = arcade.gui.UISpriteWidget(
                        sprite=preview_sprite,
                        width=scaled_width,
                        height=scaled_height
                    )
                
                img_widget = img_widget.with_background(color=(0, 0, 0, 0))
                
                img_anchor = arcade.gui.UIAnchorLayout(
                    width=350, height=450, size_hint=(None, None)
                )
                img_anchor = img_anchor.with_background(color=(0, 0, 0, 0))
                img_anchor.add(child=img_widget, anchor_x="center", anchor_y="bottom")
                
                right_panel.add(img_anchor)
            else:
                right_panel.add(arcade.gui.UISpace(width=350, height=450, color=(0, 0, 0, 0)))

            # --- ZONA KOTAK INFO DETAIL ---
            info_width = 350
            info_height = 180
            info_card_anchor = arcade.gui.UIAnchorLayout(width=info_width, height=info_height, size_hint=(None, None))
            
            # Latar Belakang Kartu Info (Gelap Transparan)
            info_bg = arcade.gui.UISpace(width=info_width, height=info_height, color=(15, 20, 30, 230))
            info_card_anchor.add(child=info_bg)
            
            info_content = arcade.gui.UIBoxLayout(vertical=True, space_between=5)
            
            # Header Teks Info
            header_row = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
            header_row.add(arcade.gui.UILabel(text=f"{self.element_map[self.last_player_char]}", font_size=24))
            header_row.add(arcade.gui.UILabel(text=f"{self.last_player_char}", font_size=22, bold=True, text_color=arcade.color.GOLD))
            info_content.add(header_row)
            
            # Sub-header Stats
            info_content.add(arcade.gui.UILabel(text=f"Role: {info['role']} | Stats: {info['stats']}", font_size=12, text_color=arcade.color.LIGHT_GRAY))
            info_content.add(arcade.gui.UILabel(text="", height=10))
            
            # Deskripsi Pasif & Ulti
            desc_text = f"🌟 Pasif:\n{info['passive']}\n\n🔥 Ultimate:\n{info['ulti']}"
            info_content.add(arcade.gui.UILabel(text=desc_text, font_size=11, text_color=arcade.color.WHITE, multiline=True, width=320))
            
            info_card_anchor.add(child=info_content, anchor_x="center", anchor_y="center")
            right_panel.add(info_card_anchor)

        # Menempelkan panel kanan ke layar (Rata Kanan)
        anchor_right = arcade.gui.UIAnchorLayout()
        anchor_right.add(child=right_panel, anchor_x="right", anchor_y="center", align_x=-40)
        self.manager.add(anchor_right)

    def make_select_action(self, char_name):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        def action(event):
            if len(self.player_party) < self.party_size:
                self.player_party.append(char_name)
                self.last_player_char = char_name
                self.build_ui()
        return action

    def on_undo(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        if self.player_party:
            self.player_party.pop()
            self.last_player_char = self.player_party[-1] if self.player_party else None
            self.preview_sprite = None
            self.sprite_list.clear()
            self.build_ui()

    def on_ready(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        import random
        self.manager.disable()
        
        enemy_party = []
        for _ in range(3):
            enemy_party.append(random.choice(self.available_characters))
            
        from gui.views import EquipmentSelectionView
        self.window.show_view(EquipmentSelectionView(self.player_party, enemy_party, "Endless"))

    def on_back_click(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        self.manager.disable()
        from gui.views import ModeSelectionView
        self.window.show_view(ModeSelectionView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)
        BGMManager.play("SELECT")

    def on_draw(self):
        self.clear()
        
        # Gambar background paling bawah
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        
        # FIX ARCADE 3.0: Menggambar menggunakan SpriteList
        if self.preview_sprite:
            self.preview_sprite.center_x = self.window.width * 0.85
            self.preview_sprite.center_y = self.window.height * 0.65
            self.sprite_list.draw() 
            
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# 7. LAYAR RIWAYAT PERTANDINGAN
# ==========================================
class HistoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/history_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
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
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height

# ==========================================
# 2. LAYAR REWARD ENDLESS (UPDATE: SCALING & SAVE)
# ==========================================
class EndlessRewardView(arcade.View):
    def __init__(self, surviving_party, cleared_floor, player_types):
        super().__init__()
        self.surviving_party = surviving_party
        self.cleared_floor = cleared_floor
        self.player_types = player_types
        self.gold_reward = 100 * self.cleared_floor
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.bg_sprite_list = arcade.SpriteList()
        import os
        bg_path = "assets/bg/game_over_endless_bg.jpg" # Tinggal ganti nama file sesuai selera
        if os.path.exists(bg_path):
            self.bg_sprite = arcade.Sprite(bg_path)
            self.bg_sprite.center_x = self.window.width / 2
            self.bg_sprite.center_y = self.window.height / 2
            self.bg_sprite.width = self.window.width
            self.bg_sprite.height = self.window.height
            self.bg_sprite_list.append(self.bg_sprite)
        else:
            self.bg_sprite = None
        self.build_ui()

        # ==========================================
        # MUAT SFX KLIK UNTUK MENU INI
        # ==========================================
        import os
        click_path = "assets/sfx/click_game_over.mp3"
        if os.path.exists(click_path):
            self.sfx_click = arcade.load_sound(click_path)
        else:
            self.sfx_click = None

    def build_ui(self):
        self.manager.clear()
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        
        v_box.add(arcade.gui.UILabel(text=f"LANTAI {self.cleared_floor} DITAKLUKKAN!", font_size=32, bold=True, text_color=arcade.color.GOLD))
        v_box.add(arcade.gui.UILabel(text=f"Hadiah Sementara: {self.gold_reward} Gold", font_size=18, text_color=arcade.color.YELLOW))
        v_box.add(arcade.gui.UILabel(text="Jika Anda kalah di lantai berikutnya, semua hadiah hilang!", font_size=12, text_color=arcade.color.LIGHT_GRAY))
        v_box.add(arcade.gui.UILabel(text="", height=10))
        
        btn_next = arcade.gui.UIFlatButton(text=f"⚔️ Lanjut Lantai {self.cleared_floor + 1}", width=300, height=45)
        btn_next.on_click = self.on_next_floor
        
        btn_save = arcade.gui.UIFlatButton(text="💾 Simpan Progress & Keluar", width=300, height=45)
        btn_save.on_click = self.on_save_quit
        
        btn_home = arcade.gui.UIFlatButton(text="💰 Ambil Gold & Pulang (Reset)", width=300, height=45)
        btn_home.on_click = self.on_home
        
        v_box.add(btn_next)
        v_box.add(btn_save)
        v_box.add(btn_home)
        
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def on_next_floor(self, event):
        import random
        from engine.factory import CharacterFactory
        from models.equipment import Equipment
        from engine.gacha_system import GachaSystem

        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)

        new_floor = self.cleared_floor + 1
        available_chars = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]
        enemy_party = []
        
        # SCALING SMOOTH: Level dan Status naik pelan-pelan tiap lantai
        enemy_level = max(1, new_floor // 2)
        stat_mult = 1.0 + ((new_floor - 1) * 0.1) # Lantai 1=1.0x, Lantai 5=1.4x
        
        for i in range(3):
            char_type = random.choice(available_chars)
            char = CharacterFactory.create_character(char_type, f"Lantai {new_floor} {char_type}")
            if hasattr(char, 'apply_scaling'):
                char.apply_scaling(level=enemy_level, stat_multiplier=stat_mult)
            char.level = enemy_level
            
            # KODE BARU (Scaling cerdas)
            random_eq = GachaSystem.get_enemy_equipment("Endless", new_floor)
            eq_data = GachaSystem.ITEM_POOL[random_eq]
            char = Equipment(char, random_eq, eq_data["bonus_atk"], eq_data["bonus_def"])
            char.level = enemy_level 
            enemy_party.append(char)

        self.manager.disable()
        from gui.views import BattleView
        self.window.show_view(BattleView(self.surviving_party, enemy_party, "Endless", self.player_types, endless_floor=new_floor))

    def on_save_quit(self, event):
        from engine.save_manager import SaveManager
        
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)

        equipments = []
        for char in self.surviving_party:
            # Tinggal baca label yang kita tempelkan tadi, jika tidak ada, beri "Tangan Kosong"
            eq_name = getattr(char, 'equipped_name', "Tangan Kosong")
            equipments.append(eq_name)
            
        # Simpan nama karakter DAN equipment-nya
        SaveManager.save_endless_state(self.cleared_floor + 1, self.player_types, equipments)
        
        self.manager.disable()
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_home(self, event):
        if hasattr(self, 'sfx_click') and self.sfx_click:
            BGMManager.play_sfx(self.sfx_click)
        from engine.save_manager import SaveManager
        SaveManager.add_gold(self.gold_reward)
        SaveManager.clear_endless_state() # Reset lantai ke 1
        
        self.manager.disable()
        from gui.views import MainMenuView
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        if self.bg_sprite:
            self.bg_sprite_list.draw()
        self.manager.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.center_x = width / 2
            self.bg_sprite.center_y = height / 2
            self.bg_sprite.width = width
            self.bg_sprite.height = height