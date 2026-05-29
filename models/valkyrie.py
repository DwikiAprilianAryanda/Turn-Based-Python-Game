# models/valkyrie.py
from models.character import Character
from engine.ai_strategy import AggressiveAI
from models.element import Element

class Valkyrie(Character):
    def __init__(self, name: str):
        # Status seimbang untuk segala situasi
        super().__init__(name, max_hp=110, max_mana=45, base_attack=22, defense=8, element=Element.AIR)
        self.ai_strategy = AggressiveAI()

    def use_special_skill(self, target):
        if self.consume_mana(20):
            print(f"{self.name} menggunakan Tombak Es Menembus Zirah!")
            
            multiplier = Element.get_multiplier(self.element, target.element)
            raw_damage = (self.base_attack * 2.5) * multiplier
            
            # Mekanik Unik Valkyrie: Mengabaikan 50% defense musuh!
            actual_damage = max(0, int(raw_damage) - (target.defense // 2))
            
            # Modifikasi HP target secara langsung karena ini mekanik khusus yang bypass take_damage reguler
            target._Character__current_hp = max(0, target._Character__current_hp - actual_damage)
            print(f"[{target.name}] menerima {actual_damage} True Damage!")
        else:
            self.basic_attack(target)