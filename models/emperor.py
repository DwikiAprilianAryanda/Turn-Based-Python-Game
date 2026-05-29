# models/emperor.py
from models.character import Character
from engine.ai_strategy import DefensiveAI
from models.effects import PowerUpEffect
from models.element import Element # Import ini

class Emperor(Character):
    def __init__(self, name: str):
        # Tambahkan element=Element.API
        super().__init__(name, max_hp=120, max_mana=50, base_attack=15, defense=10, element=Element.API)
        self.ai_strategy = DefensiveAI()

    def use_special_skill(self, target):
        mana_cost = 15
        if self.consume_mana(mana_cost):
            print(f"{self.name} menggunakan Titah Kaisar!")
            self.add_effect(PowerUpEffect(duration=2))
            
            # Terapkan elemen ke skill
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 1.5) * multiplier
            damage = max(0, int(raw_damage) - target.defense)
            target.take_damage(damage)
        else:
            print(f"Mana tidak cukup! {self.name} hanya menyerang biasa.")
            self.basic_attack(target)