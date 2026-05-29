# models/gladiator.py
from models.character import Character
from engine.ai_strategy import AggressiveAI
from models.effects import PoisonEffect
from models.element import Element # Import ini

class Gladiator(Character):
    def __init__(self, name: str):
        # Tambahkan element=Element.AIR
        super().__init__(name, max_hp=100, max_mana=30, base_attack=25, defense=5, element=Element.AIR)
        self.ai_strategy = AggressiveAI()

    def use_special_skill(self, target):
        mana_cost = 15
        if self.consume_mana(mana_cost):
            print(f"{self.name} menggunakan Serangan Brutal!")
            target.add_effect(PoisonEffect(duration=3))
            
            # Terapkan elemen ke skill
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 2) * multiplier
            damage = max(0, int(raw_damage) - target.defense)
            target.take_damage(damage)
        else:
            print(f"Mana tidak cukup! {self.name} hanya menyerang biasa.")
            self.basic_attack(target)