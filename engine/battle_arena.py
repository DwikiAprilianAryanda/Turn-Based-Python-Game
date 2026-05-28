# engine/battle_arena.py

from models.character import Character
from engine.commands import BasicAttackCommand, SpecialSkillCommand

class BattleArena:
    def __init__(self, player1: Character, player2: Character):
        self.player1 = player1
        self.player2 = player2
        self.turn_count = 1
        
        # OCP: Mendaftarkan command. 
        # Menambah aksi baru di masa depan hanya perlu menambah baris di dictionary ini.
        self.actions = {
            "1": ("Basic Attack", BasicAttackCommand()),
            "2": ("Special Skill", SpecialSkillCommand())
        }

    def start_battle(self):
        print("========================================")
        print(f" PERTEMPURAN DIMULAI: {self.player1.name} VS {self.player2.name} ")
        print("========================================")

        while self.player1.current_hp > 0 and self.player2.current_hp > 0:
            print(f"\n--- RONDE {self.turn_count} ---")
            
            self._execute_turn(self.player1, self.player2)
            if self.player2.current_hp <= 0:
                print(f"\n🏆 {self.player1.name} MENANG!")
                break

            self._execute_turn(self.player2, self.player1)
            if self.player1.current_hp <= 0:
                print(f"\n🏆 {self.player2.name} MENANG!")
                break

            self.turn_count += 1
            print("========================================")

    def _execute_turn(self, attacker: Character, defender: Character):
        print(f"\nGiliran {attacker.name} ({attacker.current_hp} HP, {attacker.current_mana} Mana)")
        print("Pilih aksi:")
        
        # Loop dinamis untuk menampilkan menu berdasarkan command yang terdaftar
        for key, (description, _) in self.actions.items():
            print(f"{key}. {description}")
        
        choice = input("Masukkan pilihan: ")

        # Mengambil aksi berdasarkan input user
        action_tuple = self.actions.get(choice)
        
        if action_tuple:
            # action_tuple[1] adalah objek Command-nya (misal: BasicAttackCommand)
            command_to_execute = action_tuple[1]
            # Polimorfisme bekerja: memanggil .execute() tanpa peduli apa tipe command-nya
            command_to_execute.execute(attacker, defender)
        else:
            print("Pilihan tidak valid! Anda melewatkan giliran karena bingung.")