# engine/ai_strategy.py
from abc import ABC, abstractmethod
from engine.commands import BasicAttackCommand, SpecialSkillCommand

class AIStrategy(ABC):
    """Penerapan Strategy Pattern untuk Kecerdasan Buatan Musuh"""
    @abstractmethod
    def decide_action(self, attacker):
        pass

class AggressiveAI(AIStrategy):
    """Fokus menyerang dengan skill secepat mungkin."""
    def decide_action(self, attacker):
        if attacker.current_mana >= 15:
            return SpecialSkillCommand(), "mengamuk dengan Special Skill!"
        return BasicAttackCommand(), "menyerang tanpa ampun!"

class DefensiveAI(AIStrategy):
    """Bermain aman, hanya menggunakan skill jika HP mulai kritis."""
    def decide_action(self, attacker):
        if attacker.current_hp < (attacker._max_hp // 2) and attacker.current_mana >= 15:
            return SpecialSkillCommand(), "menggunakan Special Skill untuk membalikkan keadaan!"
        return BasicAttackCommand(), "menyerang dengan hati-hati."