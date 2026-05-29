# engine/commands.py
import random
from abc import ABC, abstractmethod
from models.character import Character
from models.item import Item

class Command(ABC):
    @abstractmethod
    def execute(self, attacker: Character, defender: Character) -> str:
        pass

class BasicAttackCommand(Command):
    def execute(self, attacker: Character, defender: Character) -> str:
        # RNG: 10% Peluang Menghindar (Dodge)
        if random.random() < 0.10:
            return "DODGE"
        
        # RNG: 15% Peluang Serangan Kritis (Critical - Damage x2)
        if random.random() < 0.15:
            # Langsung kirimkan base_attack * 2 ke take_damage. 
            # Biarkan class Character yang mengurus pengurangan defense secara internal!
            defender.take_damage(attacker.base_attack * 2)
            return "CRIT"
        
        # Serangan Normal
        attacker.basic_attack(defender)
        return "NORMAL"

class SpecialSkillCommand(Command):
    def execute(self, attacker: Character, defender: Character) -> str:
        attacker.use_special_skill(defender)
        return "SKILL"

class UseItemCommand(Command):
    def __init__(self, item: Item):
        self.item = item

    def execute(self, attacker: Character, defender: Character) -> str:
        self.item.use(attacker)
        return "HEAL"