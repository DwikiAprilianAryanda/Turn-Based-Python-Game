from models.character import Character
from models.effects import PowerUpEffect

class Emperor(Character):
    def __init__(self, name: str):
        # Penerapan Inheritance: Mewarisi constructor dari Base Class
        # Kaisar dirancang memiliki HP dan Defense tinggi, namun Attack sedang
        super().__init__(
            name=name, 
            max_hp=130, 
            max_mana=50, 
            base_attack=15, 
            base_defense=10
        )

    # Penerapan Polymorphism: Meng-override metode abstrak sesuai mekanik unik kelas ini
    def use_special_skill(self, target: Character):
        mana_cost = 20
        print(f"\n[SKILL] {self.name} menggunakan teknik khusus: Pertahanan Kaisar!")
        
        # Menggunakan fungsi terenkapsulasi dari kelas induk untuk mengecek & mengurangi mana
        if self.consume_mana(mana_cost):
            # Mekanik Unik: Mengubah total pertahanannya sendiri menjadi serangan balik yang kuat
            skill_damage = self.base_attack + (self.base_defense * 2)
            print(f"Memusatkan energi pertahanan menjadi gelombang kejut sebesar {skill_damage}!")
            target.take_damage(skill_damage)
            self.add_effect(PowerUpEffect(duration=2))