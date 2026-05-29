# gui/views.py
import arcade
import arcade.gui
import random
from models.character import Character
from gui.widgets import StatusBar, FloatingText
from engine.commands import BasicAttackCommand, SpecialSkillCommand, UseItemCommand
from models.item import HealthPotion
from engine.factory import CharacterFactory 
from engine.history_manager import HistoryManager
from engine.save_manager import SaveManager, DIFFICULTY_SETTINGS
from engine.gacha_system import GachaSystem

# ==========================================
# 1. LAYAR MAIN MENU (UPDATE TOMBOL GACHA)
# ==========================================
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        title_label = arcade.gui.UILabel(
            text="EPIC TURN-BASED ARENA", text_color=arcade.color.GOLD, font_size=36, bold=True
        )
        
        start_button = arcade.gui.UIFlatButton(text="⚔️ Mulai Permainan", width=200)
        gacha_button = arcade.gui.UIFlatButton(text="🎲 Tarik Gacha", width=200) # TOMBOL BARU
        history_button = arcade.gui.UIFlatButton(text="📜 Lihat Riwayat", width=200) 
        quit_button = arcade.gui.UIFlatButton(text="❌ Keluar", width=200)

        start_button.on_click = self.on_start_click
        gacha_button.on_click = self.on_gacha_click # EVENT BARU
        history_button.on_click = self.on_history_click 
        quit_button.on_click = self.on_quit_click

        self.v_box.add(title_label)
        self.v_box.add(start_button)
        self.v_box.add(gacha_button) # MASUKKAN KE LAYOUT
        self.v_box.add(history_button) 
        self.v_box.add(quit_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_start_click(self, event):
        self.manager.disable()
        self.window.show_view(ModeSelectionView())
        
    def on_gacha_click(self, event):
        self.manager.disable()
        self.window.show_view(GachaView())

    def on_history_click(self, event):
        self.manager.disable()
        self.window.show_view(HistoryView())

    def on_quit_click(self, event):
        arcade.exit()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 1.5 LAYAR GACHA EQUIPMENT (BARU)
# ==========================================
class GachaView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)
        
        self.current_gold = SaveManager.get_gold()
        self.pull_result_text = "Klik tombol di bawah untuk menarik Gacha!"
        self.result_color = arcade.color.WHITE

        # Label Informasi UI
        self.title_label = arcade.gui.UILabel(text="🎲 GACHA EQUIPMENT 🎲", text_color=arcade.color.GOLD, font_size=28, bold=True)
        self.gold_label = arcade.gui.UILabel(text=f"Uang Anda: 💰 {self.current_gold} Gold", text_color=arcade.color.YELLOW, font_size=16)
        
        # Teks Hasil Tarikan (Dinamis)
        self.result_label = arcade.gui.UILabel(text=self.pull_result_text, text_color=self.result_color, font_size=18, bold=True)

        self.pull_btn = arcade.gui.UIFlatButton(text=f"Tarik 1x ({GachaSystem.COST_PER_PULL} Gold)", width=250)
        self.pull_btn.on_click = self.on_pull_click
        
        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=250)
        back_btn.on_click = self.on_back_click

        self.v_box.add(self.title_label)
        self.v_box.add(self.gold_label)
        self.v_box.add(arcade.gui.UILabel(text="", height=20)) # Spasi
        self.v_box.add(self.result_label)
        self.v_box.add(arcade.gui.UILabel(text="", height=20)) # Spasi
        self.v_box.add(self.pull_btn)
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_pull_click(self, event):
        # 1. Cek apakah uang cukup
        if self.current_gold >= GachaSystem.COST_PER_PULL:
            # Potong uang
            self.current_gold -= GachaSystem.COST_PER_PULL
            SaveManager.add_gold(-GachaSystem.COST_PER_PULL) # Minus uang di save data
            
            # 2. Lakukan Tarikan Gacha
            item_name, rarity = GachaSystem.pull_item()
            
            # 3. Simpan item ke tas (Inventory)
            SaveManager.add_item_to_inventory(item_name)
            
            # 4. Beri teks sesuai tingkat kelangkaan (Tanpa ganti warna agar tidak error)
            if rarity == "Legendary":
                self.pull_result_text = f"🌟 JACKPOT! Anda mendapat {item_name} (Legendary)!"
            elif rarity == "Rare":
                self.pull_result_text = f"✨ Anda mendapat {item_name} (Rare)!"
            else:
                self.pull_result_text = f"Anda mendapat {item_name} (Common)."
                
            # Update Tampilan UI (Hanya teksnya saja)
            self.gold_label.text = f"Uang Anda: 💰 {self.current_gold} Gold"
            self.result_label.text = self.pull_result_text
            
        else:
            self.result_label.text = "❌ Uang Anda tidak cukup untuk menarik Gacha!"

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 2. LAYAR PILIH MODE PERTANDINGAN
# ==========================================
class ModeSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        self.v_box.add(arcade.gui.UILabel(text="PILIH MODE PERTANDINGAN", text_color=arcade.color.GOLD, font_size=24, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        btn_1v1 = arcade.gui.UIFlatButton(text="Duel (1 vs 1)", width=250)
        btn_2v2 = arcade.gui.UIFlatButton(text="Tag Team (2 vs 2)", width=250)
        btn_3v3 = arcade.gui.UIFlatButton(text="Party (3 vs 3)", width=250)

        btn_1v1.on_click = self.on_click_1v1
        btn_2v2.on_click = self.on_click_2v2
        btn_3v3.on_click = self.on_click_3v3

        self.v_box.add(btn_1v1)
        self.v_box.add(btn_2v2)
        self.v_box.add(btn_3v3)

        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=250)
        back_btn.on_click = self.on_back_click
        self.v_box.add(arcade.gui.UILabel(text="", height=10))
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_click_1v1(self, event): self.select_mode(1)
    def on_click_2v2(self, event): self.select_mode(2)
    def on_click_3v3(self, event): self.select_mode(3)

    def select_mode(self, party_size):
        self.manager.disable()
        self.window.show_view(DifficultySelectionView(party_size))

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
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

        self.v_box.add(arcade.gui.UILabel(text="PILIH TINGKAT KESULITAN", text_color=arcade.color.GOLD, font_size=24, bold=True))
        self.v_box.add(arcade.gui.UILabel(text="Semakin sulit, semakin banyak EXP yang didapat!", text_color=arcade.color.LIGHT_GRAY, font_size=12))
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
# 4. LAYAR PEMILIHAN KARAKTER (UPDATE SCALING)
# ==========================================
class CharacterSelectionView(arcade.View):
    def __init__(self, party_size, difficulty):
        super().__init__()
        self.party_size = party_size
        self.difficulty = difficulty
        self.player_party = []

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=10)

        self.title_label = arcade.gui.UILabel(
            text=f"⚔️ PILIH KARAKTER ({self.difficulty}) (0/{self.party_size}) ⚔️",
            text_color=arcade.color.GOLD, font_size=24, bold=True
        )
        self.v_box.add(self.title_label)
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        self.available_characters = ["Emperor", "Gladiator", "Assassin", "Mage", "Knight", "Valkyrie"]

        for char_type in self.available_characters:
            btn = arcade.gui.UIFlatButton(text=f"Tambah {char_type}", width=350)
            btn.on_click = self.create_character_action(char_type)
            self.v_box.add(btn)

        self.v_box.add(arcade.gui.UILabel(text="", height=10))
        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=350)
        back_btn.on_click = self.on_back_click
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def create_character_action(self, char_type):
        def action(event):
            self.player_party.append(char_type)
            self.title_label.text = f"⚔️ PILIH KARAKTER ({self.difficulty}) ({len(self.player_party)}/{self.party_size}) ⚔️"
            if len(self.player_party) == self.party_size:
                enemy_party = [random.choice(self.available_characters) for _ in range(self.party_size)]
                self.start_battle(self.player_party, enemy_party)
        return action

    # TImpa fungsi ini di dalam CharacterSelectionView
    def start_battle(self, player_party_types, enemy_party_types):
        self.manager.disable()
        # Jangan langsung ke BattleView, lempar datanya ke Layar Equipment dulu!
        eq_view = EquipmentSelectionView(player_party_types, enemy_party_types, self.difficulty)
        self.window.show_view(eq_view)

    def on_back_click(self, event):
        self.manager.disable()
        self.window.show_view(ModeSelectionView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# 4.5 LAYAR PERSIAPAN EQUIPMENT (BARU)
# ==========================================
class EquipmentSelectionView(arcade.View):
    def __init__(self, player_types: list, enemy_types: list, difficulty: str):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        self.player_types = player_types
        self.enemy_types = enemy_types
        self.difficulty = difficulty

        # Ambil inventory dari Save Data (hapus duplikat dengan set)
        raw_inventory = SaveManager.get_inventory()
        self.inventory = ["Tangan Kosong"] + list(set(raw_inventory))
        
        # Simpan indeks pilihan item untuk masing-masing karakter
        self.selected_eq_indices = [0] * len(self.player_types)

        title = arcade.gui.UILabel(text="🛡️ PERSIAPAN EQUIPMENT ⚔️", text_color=arcade.color.GOLD, font_size=24, bold=True)
        self.v_box.add(title)
        self.v_box.add(arcade.gui.UILabel(text="Klik kotak di samping nama untuk mengganti senjata/zirah", text_color=arcade.color.LIGHT_GRAY, font_size=12))
        self.v_box.add(arcade.gui.UILabel(text="", height=10))

        # Buat Baris Tombol untuk setiap Karakter
        for i, char_type in enumerate(self.player_types):
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
            
            lbl = arcade.gui.UILabel(text=f"{char_type}", width=120, font_size=14, bold=True)
            
            # Tombol yang bisa diklik untuk mengganti item (Cycle)
            btn = arcade.gui.UIFlatButton(text=self.inventory[0], width=250)
            btn.on_click = self.make_cycle_action(i, btn)
            
            row.add(lbl)
            row.add(btn)
            self.v_box.add(row)

        self.v_box.add(arcade.gui.UILabel(text="", height=20))
        
        start_btn = arcade.gui.UIFlatButton(text="🔥 Masuk ke Arena 🔥", width=380)
        start_btn.on_click = self.on_start_battle
        self.v_box.add(start_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def make_cycle_action(self, char_index, button_widget):
        """Fungsi Closure untuk memutar pilihan item di tombol"""
        def action(event):
            # Geser indeks ke item berikutnya
            current_idx = self.selected_eq_indices[char_index]
            next_idx = (current_idx + 1) % len(self.inventory)
            self.selected_eq_indices[char_index] = next_idx
            
            # Perbarui teks tombol
            button_widget.text = self.inventory[next_idx]
        return action

    def on_start_battle(self, event):
        self.manager.disable()
        from models.equipment import Weapon, Armor
        from engine.gacha_system import GachaSystem
        
        # 1. SETUP TIM PEMAIN (Terapkan Equipment Pilihan)
        player_party = []
        player_levels = []
        for i, char_type in enumerate(self.player_types):
            char = CharacterFactory.create_character(char_type, f"{char_type} (P{i+1})")
            
            # Terapkan Level
            level = SaveManager.get_character_data(char_type)["level"]
            char.apply_scaling(level=level, stat_multiplier=1.0)
            player_levels.append(level)
            
            # Terapkan Equipment (Decorator)
            eq_name = self.inventory[self.selected_eq_indices[i]]
            if eq_name != "Tangan Kosong":
                eq_data = GachaSystem.ITEM_POOL[eq_name]
                if eq_data["type"] == "Weapon":
                    char = Weapon(char, weapon_name=eq_name, bonus_attack=eq_data["bonus"])
                elif eq_data["type"] == "Armor":
                    char = Armor(char, armor_name=eq_name, bonus_defense=eq_data["bonus"])
                    
            player_party.append(char)
            
        # 2. SETUP TIM MUSUH (Auto-Equip Random Item)
        avg_level = max(1, sum(player_levels) // len(player_levels))
        diff_settings = DIFFICULTY_SETTINGS[self.difficulty]
        enemy_level = min(avg_level, diff_settings["enemy_cap"])
        
        # Ambil daftar semua nama item dari sistem Gacha
        all_items = list(GachaSystem.ITEM_POOL.keys())
        
        enemy_party = []
        for i, char_type in enumerate(self.enemy_types):
            char = CharacterFactory.create_character(char_type, f"{char_type} (Musuh {i+1})")
            char.apply_scaling(level=enemy_level, stat_multiplier=diff_settings["stat_mult"])
            
            # Musuh mengambil item acak dari pool Gacha
            import random
            random_eq = random.choice(all_items)
            eq_data = GachaSystem.ITEM_POOL[random_eq]
            if eq_data["type"] == "Weapon":
                char = Weapon(char, weapon_name=random_eq, bonus_attack=eq_data["bonus"])
            elif eq_data["type"] == "Armor":
                char = Armor(char, armor_name=random_eq, bonus_defense=eq_data["bonus"])
                
            enemy_party.append(char)

        # 3. LEMPAR KE ARENA
        from gui.views import BattleView
        battle_view = BattleView(player_party, enemy_party, self.difficulty, self.player_types)
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
# 6. LAYAR PERTEMPURAN (UPDATE PENERUSAN DATA)
# ==========================================
class BattleView(arcade.View):
    def __init__(self, player_party: list, enemy_party: list, difficulty: str, player_types: list):
        super().__init__()
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.difficulty = difficulty
        self.player_types = player_types # Disimpan untuk hadiah EXP
        
        self.p1_idx = 0
        self.p2_idx = 0
        self.p1_active = self.player_party[self.p1_idx]
        self.p2_active = self.enemy_party[self.p2_idx]
        self.current_turn = self.p1_active
        self.p1_log = "Pertempuran Dimulai!\nGiliran Anda."
        self.p2_log = ""
        self.is_player_turn = True
        self.enemy_delay_timer = 0.0
        self.shake_timer = 0.0

        self.character_sprites = arcade.SpriteList()
        self.p1_sprite = arcade.SpriteSolidColor(150, 220, color=arcade.color.CRIMSON)
        self.character_sprites.append(self.p1_sprite)
        self.p2_sprite = arcade.SpriteSolidColor(150, 220, color=arcade.color.ROYAL_BLUE)
        self.character_sprites.append(self.p2_sprite)
        self.floating_texts = []
        self.update_layout() 

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        
        attack_button = arcade.gui.UIFlatButton(text="⚔️ Attack", width=150)
        skill_button = arcade.gui.UIFlatButton(text="🔥 Skill", width=150)
        item_button = arcade.gui.UIFlatButton(text="🎒 Heal", width=150)
        attack_button.on_click = self.on_attack_click
        skill_button.on_click = self.on_skill_click
        item_button.on_click = self.on_item_click

        self.h_box.add(attack_button)
        self.h_box.add(skill_button)
        self.h_box.add(item_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.h_box, anchor_x="center", anchor_y="bottom", align_y=40)
        self.manager.add(anchor_layout)

    def update_layout(self):
        sw = self.window.width
        sh = self.window.height
        self.p1_base_x = sw * 0.25
        self.p2_base_x = sw * 0.75
        self.base_y = sh * 0.50
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

    def spawn_floating_text(self, text, x, y, color):
        adjusted_y = y
        for f_text in self.floating_texts:
            if abs(f_text.x - x) < 50 and abs(f_text.y - adjusted_y) < 30:
                adjusted_y += 30
        self.floating_texts.append(FloatingText(text, x, adjusted_y, color))

    def handle_death(self) -> bool:
        # MUSUH MATI
        if self.p2_active.current_hp <= 0:
            self.p2_idx += 1
            if self.p2_idx >= len(self.enemy_party):
                self.manager.disable()
                # PANGGIL GAME OVER (Pemain Menang = True)
                self.window.show_view(GameOverView("Tim Pemain", "Tim Musuh", self.p1_active.current_hp, True, self.difficulty, self.player_types))
                return True
            else:
                self.p2_active = self.enemy_party[self.p2_idx]
                self.p2_log = f"Musuh gugur! {self.p2_active.name} melompat ke arena!"
                self.update_layout()
                self.current_turn = self.p1_active
                self.is_player_turn = True
                return True

        # PEMAIN MATI
        if self.p1_active.current_hp <= 0:
            self.p1_idx += 1
            if self.p1_idx >= len(self.player_party):
                self.manager.disable()
                # PANGGIL GAME OVER (Pemain Menang = False)
                self.window.show_view(GameOverView("Tim Musuh", "Tim Pemain", self.p2_active.current_hp, False, self.difficulty, self.player_types))
                return True
            else:
                self.p1_active = self.player_party[self.p1_idx]
                self.p1_log = f"Rekanmu gugur! {self.p1_active.name} melompat ke arena!\nGiliran Anda."
                self.update_layout()
                self.current_turn = self.p1_active
                self.is_player_turn = True
                return True
        return False

    def on_attack_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            command = BasicAttackCommand()
            status = command.execute(self.p1_active, self.p2_active)
            self.p2_log = ""
            if status == "DODGE":
                self.p1_log = "Serangan Meleset!"
                self.spawn_floating_text("MISS!", self.p2_base_x, self.base_y, arcade.color.GRAY)
            elif status == "CRIT":
                self.p1_log = "CRITICAL HIT!"
                self.spawn_floating_text("CRITICAL!", self.p2_base_x, self.base_y, arcade.color.GOLD)
                self.shake_timer = 0.3
            else:
                self.p1_log = "Melancarkan Basic Attack!"
                self.spawn_floating_text("BAM!", self.p2_base_x, self.base_y, arcade.color.RED)
            self.check_game_state()

    def on_skill_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            command = SpecialSkillCommand()
            command.execute(self.p1_active, self.p2_active)
            self.p1_log = "Menggunakan Special Skill!"
            self.p2_log = ""
            self.spawn_floating_text("SKILL!", self.p2_base_x, self.base_y, arcade.color.ORANGE)
            self.shake_timer = 0.5
            self.check_game_state()

    def on_item_click(self, event):
        if not self.is_player_turn: return 
        if self.current_turn == self.p1_active:
            potion = HealthPotion()
            command = UseItemCommand(potion)
            command.execute(self.p1_active, self.p2_active)
            self.p1_log = f"Meminum {potion.name}!"
            self.p2_log = ""
            self.spawn_floating_text("+40 HP", self.p1_base_x, self.base_y, arcade.color.LIGHT_GREEN)
            self.check_game_state()

    def check_game_state(self):
        if self.handle_death(): return
        self.current_turn = self.p2_active
        self.is_player_turn = False 
        effect_logs = self.p2_active.process_effects()
        if effect_logs:
            self.p2_log = effect_logs
            self.spawn_floating_text("RACUN!", self.p2_base_x, self.base_y, arcade.color.PURPLE)
        if self.handle_death(): return
        self.enemy_delay_timer = 1.5

    def on_update(self, delta_time: float):
        for f_text in self.floating_texts:
            f_text.update()
        self.floating_texts = [f for f in self.floating_texts if not f.is_dead()]

        if not self.is_player_turn and self.enemy_delay_timer > 0:
            self.enemy_delay_timer -= delta_time
            if self.enemy_delay_timer <= 0:
                self.enemy_turn()

        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            self.p1_sprite.center_x = self.p1_base_x + offset_x
            self.p1_sprite.center_y = self.base_y + offset_y
            self.p2_sprite.center_x = self.p2_base_x + offset_x
            self.p2_sprite.center_y = self.base_y + offset_y
        else:
            self.p1_sprite.center_x = self.p1_base_x
            self.p1_sprite.center_y = self.base_y
            self.p2_sprite.center_x = self.p2_base_x
            self.p2_sprite.center_y = self.base_y

    def enemy_turn(self):
        if hasattr(self.p2_active, 'ai_strategy'):
            command, log_msg = self.p2_active.ai_strategy.decide_action(self.p2_active)
        else:
            command = BasicAttackCommand()
            log_msg = "Menyerang!"
            
        status = command.execute(self.p2_active, self.p1_active)
        self.p1_log = ""
        
        if status == "DODGE":
            self.p2_log = "Serangan Meleset!"
            self.spawn_floating_text("MISS!", self.p1_base_x, self.base_y, arcade.color.GRAY)
        elif status == "CRIT":
            self.p2_log = "CRITICAL HIT!"
            self.spawn_floating_text("CRITICAL!", self.p1_base_x, self.base_y, arcade.color.GOLD)
            self.shake_timer = 0.3
        elif status == "SKILL":
            self.p2_log = log_msg.capitalize()
            self.spawn_floating_text("SKILL!", self.p1_base_x, self.base_y, arcade.color.ORANGE)
            self.shake_timer = 0.5
        else:
            self.p2_log = log_msg.capitalize()
            self.spawn_floating_text("BAM!", self.p1_base_x, self.base_y, arcade.color.RED)

        if self.handle_death(): return
        self.current_turn = self.p1_active
        self.is_player_turn = True 
        
        effect_logs = self.p1_active.process_effects()
        if effect_logs:
            self.p1_log = f"{effect_logs}\n\nGiliran Anda!"
        else:
            self.p1_log = "Giliran Anda!"

        if self.handle_death(): return

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.character_sprites.draw()
        p1_remaining = len(self.player_party) - self.p1_idx
        p2_remaining = len(self.enemy_party) - self.p2_idx

        arcade.Text(
            f"Tim Anda: {p1_remaining}/{len(self.player_party)} Bertahan", 
            x=self.p1_base_x, y=self.base_y + 210, color=arcade.color.YELLOW, font_size=12, bold=True, anchor_x="center"
        ).draw()
        arcade.Text(
            f"Tim Musuh: {p2_remaining}/{len(self.enemy_party)} Bertahan", 
            x=self.p2_base_x, y=self.base_y + 210, color=arcade.color.YELLOW, font_size=12, bold=True, anchor_x="center"
        ).draw()

        arcade.Text(self.p1_active.name, x=self.p1_base_x, y=self.base_y + 180, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        arcade.Text(self.p2_active.name, x=self.p2_base_x, y=self.base_y + 180, color=arcade.color.WHITE, font_size=16, bold=True, anchor_x="center").draw()
        
        self.p1_hp_bar.draw()
        self.p1_mana_bar.draw()
        self.p2_hp_bar.draw()
        self.p2_mana_bar.draw()
        
        arcade.Text(self.p1_log, x=self.p1_base_x, y=self.base_y - 140, color=arcade.color.LIGHT_BLUE, font_size=16, anchor_x="center", anchor_y="top", multiline=True, width=350, align="center").draw()
        arcade.Text(self.p2_log, x=self.p2_base_x, y=self.base_y - 140, color=arcade.color.LIGHT_RED_OCHRE, font_size=16, anchor_x="center", anchor_y="top", multiline=True, width=350, align="center").draw()
        
        for f_text in self.floating_texts:
            f_text.draw()
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