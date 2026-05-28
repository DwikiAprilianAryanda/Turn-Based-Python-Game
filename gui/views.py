# gui/views.py
import arcade
import arcade.gui
from models.character import Character
from gui.widgets import StatusBar
from engine.commands import BasicAttackCommand, SpecialSkillCommand, UseItemCommand
from models.item import HealthPotion
from engine.factory import CharacterFactory # Import Factory Pattern

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

        # Judul Game (Teks sebagai UI Widget agar mudah diposisikan)
        title_label = arcade.gui.UILabel(
            text="EPIC TURN-BASED ARENA",
            text_color=arcade.color.GOLD,
            font_size=36,
            bold=True
        )
        
        start_button = arcade.gui.UIFlatButton(text="Mulai Permainan", width=200)
        quit_button = arcade.gui.UIFlatButton(text="Keluar", width=200)

        # Event Listener untuk tombol
        start_button.on_click = self.on_start_click
        quit_button.on_click = self.on_quit_click

        self.v_box.add(title_label)
        self.v_box.add(start_button)
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
        
        # Di sinilah Factory Pattern bekerja sesuai pilihan pemain!
        p1 = CharacterFactory.create_character(p1_type, p1_name)
        p2 = CharacterFactory.create_character(p2_type, p2_name)
        
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
    def __init__(self, winner_name: str):
        super().__init__()
        self.winner_name = winner_name
        
        # Setup UI Manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # BARIS INI YANG KEMUNGKINAN HILANG: Membuat kotak vertikal
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Membuat teks pemenang
        winner_label = arcade.gui.UILabel(
            text=f"🏆 {self.winner_name} MENANG! 🏆",
            text_color=arcade.color.LIGHT_GREEN,
            font_size=30,
            bold=True
        )
        
        # Membuat tombol kembali ke menu
        menu_button = arcade.gui.UIFlatButton(text="Kembali ke Menu", width=200)
        menu_button.on_click = self.on_menu_click

        # Memasukkan elemen ke dalam kotak vertikal
        self.v_box.add(winner_label)
        self.v_box.add(menu_button)

        # Menempatkan kotak vertikal ke tengah layar
        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor_layout)

    def on_menu_click(self, event):
        self.manager.disable()
        menu_view = MainMenuView()
        self.window.show_view(menu_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.manager.draw()


# ==========================================
# 3. LAYAR PERTEMPURAN (UPDATE)
# ==========================================
class BattleView(arcade.View):
    def __init__(self, player1: Character, player2: Character):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_turn = self.player1
        self.battle_log = f"Pertempuran Dimulai!\nGiliran {self.player1.name}."

        # Widget Bar
        self.p1_hp_bar = StatusBar(self.player1, x=50, y=480, width=200, height=20, is_mana=False)
        self.p1_mana_bar = StatusBar(self.player1, x=50, y=450, width=150, height=15, is_mana=True)
        self.p2_hp_bar = StatusBar(self.player2, x=550, y=480, width=200, height=20, is_mana=False)
        self.p2_mana_bar = StatusBar(self.player2, x=600, y=450, width=150, height=15, is_mana=True)

        # Setup UI Manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        
        attack_button = arcade.gui.UIFlatButton(text="⚔️ Attack", width=150)
        skill_button = arcade.gui.UIFlatButton(text="🔥 Skill", width=150)
        item_button = arcade.gui.UIFlatButton(text="🎒 Heal (+40 HP)", width=150)

        attack_button.on_click = self.on_attack_click
        skill_button.on_click = self.on_skill_click
        item_button.on_click = self.on_item_click

        self.h_box.add(attack_button)
        self.h_box.add(skill_button)
        self.h_box.add(item_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.h_box, anchor_x="center", anchor_y="bottom", align_y=40)
        self.manager.add(anchor_layout)

    def on_attack_click(self, event):
        if self.current_turn == self.player1:
            command = BasicAttackCommand()
            command.execute(self.player1, self.player2)
            self.battle_log = f"{self.player1.name} melancarkan Basic Attack!"
            self.check_game_state()

    def on_skill_click(self, event):
        if self.current_turn == self.player1:
            command = SpecialSkillCommand()
            command.execute(self.player1, self.player2)
            self.battle_log = f"{self.player1.name} menggunakan Special Skill!"
            self.check_game_state()

    def on_item_click(self, event):
        if self.current_turn == self.player1:
            potion = HealthPotion()
            command = UseItemCommand(potion)
            command.execute(self.player1, self.player2)
            self.battle_log = f"{self.player1.name} meminum {potion.name}!"
            self.check_game_state()

    def check_game_state(self):
        """Memindahkan layar ke Game Over jika ada yang kalah"""
        if self.player2.current_hp <= 0:
            self.manager.disable()
            self.window.show_view(GameOverView(self.player1.name))
            return

        self.current_turn = self.player2
        self.enemy_turn()

    def enemy_turn(self):
        if self.player2.current_mana >= 15:
            command = SpecialSkillCommand()
            self.battle_log += f"\nMusuh membalas dengan Special Skill!"
        else:
            command = BasicAttackCommand()
            self.battle_log += f"\nMusuh membalas dengan Basic Attack!"
            
        command.execute(self.player2, self.player1)

        if self.player1.current_hp <= 0:
            self.manager.disable()
            self.window.show_view(GameOverView(self.player2.name))
        else:
            self.current_turn = self.player1

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        arcade.Text(self.player1.name, x=50, y=510, color=arcade.color.WHITE, font_size=20, bold=True).draw()
        arcade.Text(self.player2.name, x=550, y=510, color=arcade.color.WHITE, font_size=20, bold=True).draw()
        self.p1_hp_bar.draw()
        self.p1_mana_bar.draw()
        self.p2_hp_bar.draw()
        self.p2_mana_bar.draw()
        arcade.Text(
            self.battle_log, x=self.window.width // 2, y=200, color=arcade.color.YELLOW, 
            font_size=16, anchor_x="center", anchor_y="center", multiline=True, width=500, align="center"
        ).draw()
        self.manager.draw()