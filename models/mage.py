# models/mage.py
from models.character import Character
from engine.ai_strategy import DefensiveAI
from models.element import Element

class Mage(Character):
    def __init__(self, name: str):
        # HP Rendah, Mana Sangat Tinggi
        super().__init__(name, max_hp=90, max_mana=60, base_attack=15, defense=3, element=Element.API)
        self.ai_strategy = DefensiveAI()

    def use_special_skill(self, target):
        # Biaya mana lebih tinggi, tapi damage murni sangat mematikan
        mana_cost = 25
        if self.consume_mana(mana_cost):
            print(f"{self.name} merapal Bola Api Raksasa!")
            
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 3.5) * multiplier # Damage dikalikan 3.5!
            target.take_damage(raw_damage)
        else:
            self.basic_attack(target)