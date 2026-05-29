# models/effects.py
from abc import ABC, abstractmethod

class StatusEffect(ABC):
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def apply_initial_effect(self, target):
        """Dipanggil HANYA SEKALI saat efek pertama kali diberikan (misal: tambah ATK)"""
        pass

    @abstractmethod
    def apply_turn_effect(self, target) -> str:
        """Dipanggil SETIAP KALI giliran karakter dimulai (misal: kurang HP dari racun)"""
        pass

    def remove_effect(self, target):
        """Dipanggil saat durasi giliran habis untuk mengembalikan status seperti semula"""
        pass

# ==========================================
# CONTOH DEBUFF (EFEK NEGATIF)
# ==========================================
class PoisonEffect(StatusEffect):
    def __init__(self, duration: int = 3):
        super().__init__(name="Racun", duration=duration)
        self.damage_per_turn = 10

    def apply_turn_effect(self, target) -> str:
        target.take_damage(self.damage_per_turn)
        self.duration -= 1
        return f"🤢 {target.name} terkena racun! (-{self.damage_per_turn} HP). Sisa: {self.duration} turn."

# ==========================================
# CONTOH BUFF (EFEK POSITIF)
# ==========================================
class PowerUpEffect(StatusEffect):
    def __init__(self, duration: int = 2):
        super().__init__(name="Power Up", duration=duration)
        self.bonus_attack = 20

    def apply_initial_effect(self, target):
        target.base_attack += self.bonus_attack

    def apply_turn_effect(self, target) -> str:
        self.duration -= 1
        return f"🔥 {target.name} sedang mode Power Up! (+{self.bonus_attack} ATK). Sisa: {self.duration} turn."

    def remove_effect(self, target):
        target.base_attack -= self.bonus_attack