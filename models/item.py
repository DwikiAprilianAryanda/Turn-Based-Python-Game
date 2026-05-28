# models/item.py
from abc import ABC, abstractmethod
from models.character import Character

class Item(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def use(self, target: Character):
        """
        Penerapan Abstraction: Setiap item wajib memiliki cara penggunaannya sendiri,
        namun cara kerjanya disembunyikan dari sistem utama.
        """
        pass


class HealthPotion(Item):
    def __init__(self):
        super().__init__(name="Ramuan Darah", description="Memulihkan 40 HP.")
        self.heal_amount = 40

    def use(self, target: Character):
        # Penerapan Polymorphism untuk item penyembuh HP
        print(f"\nMenggunakan {self.name}...")
        target.heal(self.heal_amount)


class ManaPotion(Item):
    def __init__(self):
        super().__init__(name="Ramuan Mana", description="Memulihkan 30 Mana.")
        self.mana_amount = 30

    def use(self, target: Character):
        # Penerapan Polymorphism untuk item penyembuh Mana
        print(f"\nMenggunakan {self.name}...")
        target.restore_mana(self.mana_amount)