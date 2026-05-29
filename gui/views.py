# gui/views.py
import arcade
import arcade.gui
from models.character import Character
from gui.widgets import StatusBar
from engine.commands import BasicAttackCommand, SpecialSkillCommand, UseItemCommand
from models.item import HealthPotion
from engine.factory import CharacterFactory 
from gui.widgets import FloatingText
from engine.history_manager import HistoryManager

# ==========================================
# 1. LAYAR MAIN MENU
# ==========================================
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Membuat tata letak vertikal untuk tombol menu
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Judul Game
        title_label = arcade.gui.UILabel(
            text="EPIC TURN-BASED ARENA",
            text_color=arcade.color.GOLD,
            font_size=36,
            bold=True
        )
        
        start_button = arcade.gui.UIFlatButton(text="Mulai Permainan", width=200)
        history_button = arcade.gui.UIFlatButton(text="Lihat Riwayat", width=200) # TOMBOL BARU
        quit_button = arcade.gui.UIFlatButton(text="Keluar", width=200)

        # Event Listener untuk tombol
        start_button.on_click = self.on_start_click
        history_button.on_click = self.on_history_click # EVENT BARU
        quit_button.on_click = self.on_quit_click

        self.v_box.add(title_label)
        self.v_box.add(start_button)
        self.v_box.add(history_button) # MASUKKAN KE LAYOUT
        self.v_box.add(quit_button)

        # Posisikan menu di tengah layar
# Posisikan menu di tengah layar
        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor_layout)

    def on_start_click(self, event):
        """Pindah ke layar pemilihan karakter saat tombol mulai diklik"""
        self.manager.disable() # Matikan UI Menu sebelum pindah layar
        
        # Pindah ke Character Selection
        selection_view = CharacterSelectionView()
        self.window.show_view(selection_view)

    def on_history_click(self, event):
        """Pindah ke layar riwayat saat tombol diklik"""
        self.manager.disable()
        history_view = HistoryView()
        self.window.show_view(history_view)

    def on_quit_click(self, event):
        arcade.exit()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()

# ==========================================
# LAYAR PEMILIHAN KARAKTER (BARU)
# ==========================================
class CharacterSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Judul Layar
        title_label = arcade.gui.UILabel(
            text="PILIH KARAKTER ANDA",
            text_color=arcade.color.WHITE,
            font_size=24,
            bold=True
        )

        # Tombol Pilihan Karakter
        btn_emperor = arcade.gui.UIFlatButton(text="Kaisar (HP & Defense Tinggi)", width=300)
        btn_gladiator = arcade.gui.UIFlatButton(text="Gladiator (Attack Tinggi)", width=300)

        # Event Listener
        btn_emperor.on_click = self.on_emperor_click
        btn_gladiator.on_click = self.on_gladiator_click

        self.v_box.add(title_label)
        self.v_box.add(btn_emperor)
        self.v_box.add(btn_gladiator)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor_layout)

    def on_emperor_click(self, event):
        # Jika memilih Emperor, musuhnya otomatis Gladiator
        self.start_battle("Emperor", "Qin Shi Huang", "Gladiator", "Spartacus (Musuh)")

    def on_gladiator_click(self, event):
        # Jika memilih Gladiator, musuhnya otomatis Emperor
        self.start_battle("Gladiator", "Spartacus", "Emperor", "Qin Shi Huang (Musuh)")

    def start_battle(self, p1_type, p1_name, p2_type, p2_name):
        self.manager.disable()
        
        # 1. Factory Pattern membuat Karakter Polos
        p1 = CharacterFactory.create_character(p1_type, p1_name)
        p2 = CharacterFactory.create_character(p2_type, p2_name)
        
        # 2. IMPLEMENTASI DECORATOR PATTERN (Membungkus Karakter)
        from models.equipment import Weapon, Armor
        
        # Kita pakaikan Pedang Excalibur ke Player 1 (+20 Attack)
        p1 = Weapon(p1, weapon_name="Pedang Excalibur", bonus_attack=20)
        
        # Kita pakaikan Zirah Baja ke Player 2 (+15 Defense)
        # Ingat, semakin tinggi Defense, damage musuh (Attack * 2) saat Critical akan semakin berkurang
        p2 = Armor(p2, armor_name="Zirah Baja", bonus_defense=15)
        
        # 3. Masukkan ke arena pertarungan
        battle_view = BattleView(p1, p2)
        self.window.show_view(battle_view)

    def on_show_view(self):
        # Latar belakang biru gelap agar beda dengan Main Menu
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()


# ==========================================
# 2. LAYAR GAME OVER
# ==========================================
class GameOverView(arcade.View):
    def __init__(self, winner: Character, loser: Character):
        super().__init__()
        self.winner = winner
        self.loser = loser
        
        # --- EKSEKUSI PENYIMPANAN DATA DI SINI ---
        HistoryManager.save_match(self.winner.name, self.loser.name, self.winner.current_hp)
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        winner_label = arcade.gui.UILabel(
            text=f"🏆 {self.winner.name} MENANG! 🏆",
            text_color=arcade.color.LIGHT_GREEN,
            font_size=30,
            bold=True
        )
        
        menu_button = arcade.gui.UIFlatButton(text="Kembali ke Menu", width=200)
        menu_button.on_click = self.on_menu_click

        self.v_box.add(winner_label)
        self.v_box.add(menu_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_menu_click(self, event):
        self.manager.disable()
        # Gunakan import lokal untuk menghindari error Circular Import
        from gui.views import MainMenuView 
        menu_view = MainMenuView()
        self.window.show_view(menu_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.manager.draw()


# ==========================================
# 3. LAYAR PERTEMPURAN (UPDATE UI LOG TERPISAH)
# ==========================================
class BattleView(arcade.View):
    def __init__(self, player1: Character, player2: Character):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_turn = self.player1
        
        # --- PERUBAHAN UI LOG ---
        # Memisahkan log menjadi dua agar tidak menumpuk di tengah
        self.p1_log = "Pertempuran Dimulai!\nGiliran Anda."
        self.p2_log = ""

        self.is_player_turn = True
        self.enemy_delay_timer = 0.0
        self.shake_timer = 0.0

        self.character_sprites = arcade.SpriteList()

        self.p1_sprite = arcade.SpriteSolidColor(120, 180, arcade.color.CRIMSON)
        self.p1_sprite.center_x = 200
        self.p1_sprite.center_y = 320
        self.character_sprites.append(self.p1_sprite)

        self.p2_sprite = arcade.SpriteSolidColor(120, 180, arcade.color.ROYAL_BLUE)
        self.p2_sprite.center_x = 600
        self.p2_sprite.center_y = 320
        self.character_sprites.append(self.p2_sprite)

        self.floating_texts = []

        self.p1_hp_bar = StatusBar(self.player1, x=50, y=480, width=200, height=20, is_mana=False)
        self.p1_mana_bar = StatusBar(self.player1, x=50, y=450, width=150, height=15, is_mana=True)
        self.p2_hp_bar = StatusBar(self.player2, x=550, y=480, width=200, height=20, is_mana=False)
        self.p2_mana_bar = StatusBar(self.player2, x=600, y=450, width=150, height=15, is_mana=True)

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

    def spawn_floating_text(self, text, x, y, color):
        adjusted_y = y
        for f_text in self.floating_texts:
            if abs(f_text.x - x) < 50 and abs(f_text.y - adjusted_y) < 30:
                adjusted_y += 30
        self.floating_texts.append(FloatingText(text, x, adjusted_y, color))

    def on_attack_click(self, event):
        if not self.is_player_turn: return 

        if self.current_turn == self.player1:
            command = BasicAttackCommand()
            status = command.execute(self.player1, self.player2)
            
            self.p2_log = ""
            
            if status == "DODGE":
                self.p1_log = "Serangan Meleset!"
                self.spawn_floating_text("MISS!", 600, 420, arcade.color.GRAY)
            elif status == "CRIT":
                self.p1_log = "CRITICAL HIT!"
                self.spawn_floating_text("CRITICAL!", 600, 420, arcade.color.GOLD)
                self.shake_timer = 0.3  # Picu getaran selama 0.3 detik
            else:
                self.p1_log = "Melancarkan Basic Attack!"
                self.spawn_floating_text("BAM!", 600, 420, arcade.color.RED)
                
            self.check_game_state()

    def on_skill_click(self, event):
        if not self.is_player_turn: return 

        if self.current_turn == self.player1:
            command = SpecialSkillCommand()
            command.execute(self.player1, self.player2)
            
            self.p1_log = "Menggunakan Special Skill!"
            self.p2_log = ""
            
            self.spawn_floating_text("SKILL!", 600, 420, arcade.color.ORANGE)
            self.shake_timer = 0.5  # Skill memicu getaran lebih lama
            self.check_game_state()

    def on_item_click(self, event):
        if not self.is_player_turn: return 

        if self.current_turn == self.player1:
            potion = HealthPotion()
            command = UseItemCommand(potion)
            command.execute(self.player1, self.player2)
            
            self.p1_log = f"Meminum {potion.name}!"
            self.p2_log = ""
            
            self.spawn_floating_text("+40 HP", 200, 420, arcade.color.LIGHT_GREEN)
            self.check_game_state()

    def check_game_state(self):
        if self.player2.current_hp <= 0:
            self.manager.disable()
            self.window.show_view(GameOverView(self.player1, self.player2))
            return

        self.current_turn = self.player2
        self.is_player_turn = False 

        # Efek status musuh (jika ada) ditampilkan di sisi kanan
        effect_logs = self.player2.process_effects()
        if effect_logs:
            self.p2_log = effect_logs
            self.spawn_floating_text("RACUN!", 600, 420, arcade.color.PURPLE)

        if self.player2.current_hp <= 0:
            self.manager.disable()
            self.window.show_view(GameOverView(self.player1, self.player2))
            return

        self.enemy_delay_timer = 1.5

    def on_update(self, delta_time: float):
        # Update Floating Text
        for f_text in self.floating_texts:
            f_text.update()
        self.floating_texts = [f for f in self.floating_texts if not f.is_dead()]

        # Timer Giliran AI
        if not self.is_player_turn and self.enemy_delay_timer > 0:
            self.enemy_delay_timer -= delta_time
            if self.enemy_delay_timer <= 0:
                self.enemy_turn()

        # LOGIKA GETARAN LAYAR (SCREEN SHAKE)
        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            import random
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            
            # Posisi berguncang
            self.p1_sprite.center_x = 200 + offset_x
            self.p1_sprite.center_y = 320 + offset_y
            self.p2_sprite.center_x = 600 + offset_x
            self.p2_sprite.center_y = 320 + offset_y
        else:
            # Kunci kembali ke posisi awal agar tidak bergeser permanen
            self.p1_sprite.center_x = 200
            self.p1_sprite.center_y = 320
            self.p2_sprite.center_x = 600
            self.p2_sprite.center_y = 320

    def enemy_turn(self):
        if hasattr(self.player2, 'ai_strategy'):
            command, log_msg = self.player2.ai_strategy.decide_action(self.player2)
        else:
            command = BasicAttackCommand()
            log_msg = "Menyerang!"
            
        status = command.execute(self.player2, self.player1)
        self.p1_log = ""
        
        if status == "DODGE":
            self.p2_log = "Serangan Meleset!"
            self.spawn_floating_text("MISS!", 200, 420, arcade.color.GRAY)
        elif status == "CRIT":
            self.p2_log = "CRITICAL HIT!"
            self.spawn_floating_text("CRITICAL!", 200, 420, arcade.color.GOLD)
            self.shake_timer = 0.3
        elif status == "SKILL":
            self.p2_log = log_msg.capitalize()
            self.spawn_floating_text("SKILL!", 200, 420, arcade.color.ORANGE)
            self.shake_timer = 0.5
        else:
            self.p2_log = log_msg.capitalize()
            self.spawn_floating_text("BAM!", 200, 420, arcade.color.RED)

        if self.player1.current_hp <= 0:
            self.manager.disable()
            self.window.show_view(GameOverView(self.player2, self.player1))
        else:
            self.current_turn = self.player1
            self.is_player_turn = True 
            
            effect_logs = self.player1.process_effects()
            if effect_logs:
                self.p1_log = f"{effect_logs}\n\nGiliran Anda!"
            else:
                self.p1_log = "Giliran Anda!"

            if self.player1.current_hp <= 0:
                self.manager.disable()
                self.window.show_view(GameOverView(self.player2, self.player1))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.character_sprites.draw()

        arcade.Text(self.player1.name, x=50, y=510, color=arcade.color.WHITE, font_size=20, bold=True).draw()
        arcade.Text(self.player2.name, x=550, y=510, color=arcade.color.WHITE, font_size=20, bold=True).draw()
        self.p1_hp_bar.draw()
        self.p1_mana_bar.draw()
        self.p2_hp_bar.draw()
        self.p2_mana_bar.draw()
        
        # --- PERUBAHAN UI LOG DRAW ---
        # Teks Pemain 1 (Kiri) di bawah sprite
        arcade.Text(
            self.p1_log, x=200, y=200, color=arcade.color.LIGHT_BLUE, 
            font_size=14, anchor_x="center", anchor_y="top", multiline=True, width=280, align="center"
        ).draw()
        
        # Teks Pemain 2 (Kanan) di bawah sprite
        arcade.Text(
            self.p2_log, x=600, y=200, color=arcade.color.LIGHT_RED_OCHRE, 
            font_size=14, anchor_x="center", anchor_y="top", multiline=True, width=280, align="center"
        ).draw()
        
        for f_text in self.floating_texts:
            f_text.draw()
            
        self.manager.draw()

# ==========================================
# LAYAR RIWAYAT PERTANDINGAN (BARU)
# ==========================================
class HistoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        # Judul Layar
        title_label = arcade.gui.UILabel(
            text="📜 RIWAYAT PERTANDINGAN",
            text_color=arcade.color.GOLD,
            font_size=24,
            bold=True
        )
        self.v_box.add(title_label)

        # Mengambil data dari HistoryManager
        from engine.history_manager import HistoryManager
        history_data = HistoryManager.get_history()

        if not history_data:
            empty_label = arcade.gui.UILabel(text="Belum ada riwayat pertandingan.", text_color=arcade.color.WHITE)
            self.v_box.add(empty_label)
        else:
            # Mengambil 5 pertandingan terakhir dan membaliknya (terbaru di atas)
            recent_matches = list(reversed(history_data))[:5]
            
            for match in recent_matches:
                match_text = f"[{match['waktu']}] 🏆 {match['pemenang']} (Sisa HP: {match['sisa_hp_pemenang']}) mengalahkan {match['kalah']}"
                row_label = arcade.gui.UILabel(text=match_text, text_color=arcade.color.LIGHT_GRAY, font_size=12)
                self.v_box.add(row_label)

        # Tombol Kembali
        back_btn = arcade.gui.UIFlatButton(text="Kembali", width=200)
        back_btn.on_click = self.on_back_click
        
        # Tambahkan sedikit jarak buatan menggunakan label kosong
        self.v_box.add(arcade.gui.UILabel(text="", height=20)) 
        self.v_box.add(back_btn)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.v_box, anchor_x="center", anchor_y="center")
        self.manager.add(anchor_layout)

    def on_back_click(self, event):
        self.manager.disable()
        # Kembali ke Menu Utama
        menu_view = MainMenuView()
        self.window.show_view(menu_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EIGHTEEN_PERCENT_GREY if hasattr(arcade.color, 'EIGHTEEN_PERCENT_GREY') else arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()