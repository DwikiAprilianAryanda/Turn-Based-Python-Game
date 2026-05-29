# models/knight.py
from models.character import Character
from engine.ai_strategy import DefensiveAI
from models.effects import PowerUpEffect
from models.element import Element

class Knight(Character):
    def __init__(self, name: str):
        # HP Sangat Tinggi, Defense Tinggi, Elemen Netral (Tidak punya kelemahan)
        super().__init__(name, max_hp=150, max_mana=30, base_attack=18, defense=15, element=Element.NETRAL)
        self.ai_strategy = DefensiveAI()

    def use_special_skill(self, target):
        if self.consume_mana(15):
            print(f"{self.name} menggunakan Pertahanan Absolut & Serangan Balik!")
            # Buff diri sendiri
            self.add_effect(PowerUpEffect(duration=3))
            
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 1.2) * multiplier
            target.take_damage(raw_damage)
        else:
            self.basic_attack(target)