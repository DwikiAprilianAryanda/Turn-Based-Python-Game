# models/assassin.py
from models.character import Character
from engine.ai_strategy import AggressiveAI
from models.effects import PoisonEffect
from models.element import Element

class Assassin(Character):
    def __init__(self, name: str):
        # HP Rendah, Attack Sangat Tinggi, Defense Sangat Rendah
        super().__init__(name, max_hp=80, max_mana=20, base_attack=35, defense=2, element=Element.DAUN)
        self.ai_strategy = AggressiveAI()

    def use_special_skill(self, target):
        if self.consume_mana(15):
            print(f"{self.name} menggunakan Serangan Bayangan Berbisa!")
            target.add_effect(PoisonEffect(duration=4))
            
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 1.5) * multiplier
            target.take_damage(raw_damage)
        else:
            self.basic_attack(target)