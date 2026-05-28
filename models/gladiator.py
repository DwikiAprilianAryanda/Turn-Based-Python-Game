from models.character import Character

class Gladiator(Character):
    def __init__(self, name: str):
        # Gladiator dirancang agresif: Attack sangat tinggi, namun HP dan Defense lebih rendah
        super().__init__(
            name=name, 
            max_hp=100, 
            max_mana=40, 
            base_attack=25, 
            base_defense=4
        )

    # Penerapan Polymorphism: Meng-override metode yang sama dengan logika yang berbeda
    def use_special_skill(self, target: Character):
        mana_cost = 15
        print(f"\n[SKILL] {self.name} menggunakan teknik khusus: Tebasan Brutal!")
        
        if self.consume_mana(mana_cost):
            # Mekanik Unik: Serangan murni dengan pengganda damage dasar yang besar
            skill_damage = self.base_attack * 2
            print(f"Menghantam musuh dengan sekuat tenaga!")
            target.take_damage(skill_damage)