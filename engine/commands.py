from abc import ABC, abstractmethod
from models.character import Character

# Abstraction untuk Command Pattern
class Command(ABC):
    @abstractmethod
    def execute(self, attacker: Character, defender: Character):
        """Metode yang wajib diimplementasikan oleh setiap aksi spesifik."""
        pass

# Kelas spesifik untuk Basic Attack
class BasicAttackCommand(Command):
    def execute(self, attacker: Character, defender: Character):
        attacker.basic_attack(defender)

# Kelas spesifik untuk Special Skill
class SpecialSkillCommand(Command):
    def execute(self, attacker: Character, defender: Character):
        attacker.use_special_skill(defender)

# Nanti, jika ingin menambah aksi "Gunakan Ramuan", 
# kita cukup membuat class HealCommand(Command) di sini tanpa menyentuh BattleArena!