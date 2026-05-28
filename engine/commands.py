# engine/commands.py
from abc import ABC, abstractmethod
from models.character import Character
from models.item import Item  # Import class Item yang baru dibuat

class Command(ABC):
    @abstractmethod
    def execute(self, attacker: Character, defender: Character):
        pass

class BasicAttackCommand(Command):
    def execute(self, attacker: Character, defender: Character):
        attacker.basic_attack(defender)

class SpecialSkillCommand(Command):
    def execute(self, attacker: Character, defender: Character):
        attacker.use_special_skill(defender)

# CLASS BARU UNTUK MENGGUNAKAN ITEM
class UseItemCommand(Command):
    def __init__(self, item: Item):
        self.item = item

    def execute(self, attacker: Character, defender: Character):
        # Berbeda dengan attack, item digunakan ke diri sendiri (attacker)
        self.item.use(attacker)