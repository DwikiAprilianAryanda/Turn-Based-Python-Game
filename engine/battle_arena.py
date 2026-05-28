from models.character import Character

class BattleArena:
    def __init__(self, player1: Character, player2: Character):
        self.player1 = player1
        self.player2 = player2
        self.turn_count = 1

    def start_battle(self):
        print("========================================")
        print(f" PERTEMPURAN DIMULAI: {self.player1.name} VS {self.player2.name} ")
        print("========================================")

        # Game Loop berjalan selama kedua karakter masih hidup
        while self.player1.current_hp > 0 and self.player2.current_hp > 0:
            print(f"\n--- RONDE {self.turn_count} ---")
            
            # Giliran Player 1
            self._execute_turn(self.player1, self.player2)
            if self.player2.current_hp <= 0:
                print(f"\n🏆 {self.player1.name} MENANG!")
                break

            # Giliran Player 2
            self._execute_turn(self.player2, self.player1)
            if self.player1.current_hp <= 0:
                print(f"\n🏆 {self.player2.name} MENANG!")
                break

            self.turn_count += 1
            print("========================================")

    def _execute_turn(self, attacker: Character, defender: Character):
        """Mengelola pilihan aksi untuk karakter yang sedang mendapat giliran."""
        print(f"\nGiliran {attacker.name} ({attacker.current_hp} HP, {attacker.current_mana} Mana)")
        print("Pilih aksi:")
        print("1. Basic Attack")
        print("2. Special Skill")
        
        choice = input("Masukkan pilihan (1/2): ")

        if choice == "1":
            attacker.basic_attack(defender)
        elif choice == "2":
            # Polymorphism bekerja di sini. Kita tidak perlu tahu apakah attacker itu 
            # Emperor atau Gladiator, Python akan memanggil skill yang tepat secara otomatis.
            attacker.use_special_skill(defender)
        else:
            print("Pilihan tidak valid! Anda melewatkan giliran karena bingung.")