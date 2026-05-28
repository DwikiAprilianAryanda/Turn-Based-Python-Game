# gui/views.py
import arcade
import arcade.gui
from models.character import Character
from gui.widgets import StatusBar
from engine.commands import BasicAttackCommand, SpecialSkillCommand, UseItemCommand
from models.item import HealthPotion # Import HealthPotion

class BattleView(arcade.View):
    def __init__(self, player1: Character, player2: Character):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        
        self.current_turn = self.player1
        self.battle_log = f"Pertempuran Dimulai!\nGiliran {self.player1.name}."

        # Widget Bar Status
        self.p1_hp_bar = StatusBar(self.player1, x=50, y=480, width=200, height=20, is_mana=False)
        self.p1_mana_bar = StatusBar(self.player1, x=50, y=450, width=150, height=15, is_mana=True)
        
        self.p2_hp_bar = StatusBar(self.player2, x=550, y=480, width=200, height=20, is_mana=False)
        self.p2_mana_bar = StatusBar(self.player2, x=600, y=450, width=150, height=15, is_mana=True)

        # Setup UI Manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        
        # Tambahkan tombol ketiga
        attack_button = arcade.gui.UIFlatButton(text="⚔️ Attack", width=150)
        skill_button = arcade.gui.UIFlatButton(text="🔥 Skill", width=150)
        item_button = arcade.gui.UIFlatButton(text="🎒 Heal (+40 HP)", width=150)

        # Daftarkan event listener
        attack_button.on_click = self.on_attack_click
        skill_button.on_click = self.on_skill_click
        item_button.on_click = self.on_item_click # Fungsi baru

        self.h_box.add(attack_button)
        self.h_box.add(skill_button)
        self.h_box.add(item_button)

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.h_box,
            anchor_x="center",
            anchor_y="bottom",
            align_y=40 
        )
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

    # EVENT UNTUK TOMBOL ITEM
    def on_item_click(self, event):
        if self.current_turn == self.player1:
            potion = HealthPotion()
            command = UseItemCommand(potion)
            command.execute(self.player1, self.player2)
            self.battle_log = f"{self.player1.name} meminum {potion.name}!"
            self.check_game_state()

    def check_game_state(self):
        if self.player2.current_hp <= 0:
            self.battle_log = f"🏆 {self.player1.name} MENANG!"
            self.h_box.clear()
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
            self.battle_log = f"💀 {self.player2.name} MENANG!"
            self.h_box.clear()
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
            self.battle_log, 
            x=self.window.width // 2, y=200, 
            color=arcade.color.YELLOW, font_size=16, 
            anchor_x="center", anchor_y="center", 
            multiline=True, width=500, align="center"
        ).draw()

        self.manager.draw()