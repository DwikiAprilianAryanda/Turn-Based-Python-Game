from abc import ABC, abstractmethod

class Character(ABC):
    def __init__(self, name: str, max_hp: int, max_mana: int, base_attack: int, base_defense: int):
        self.name = name
        # Atribut statis (protected)
        self._max_hp = max_hp
        self._max_mana = max_mana
        self.base_attack = base_attack
        self.base_defense = base_defense
        
        # Atribut dinamis (private) - Penerapan Encapsulation
        self.__current_hp = max_hp
        self.__current_mana = max_mana

    # Menggunakan decorator @property sebagai Getter (Read-only access)
    @property
    def current_hp(self) -> int:
        return self.__current_hp

    @property
    def current_mana(self) -> int:
        return self.__current_mana

    # Fungsi untuk menerima serangan
    def take_damage(self, raw_damage: int):
        # Kalkulasi sederhana: damage dikurangi defense (minimal 0)
        actual_damage = max(0, raw_damage - self.base_defense)
        
        # Pastikan HP tidak turun di bawah 0
        self.__current_hp = max(0, self.__current_hp - actual_damage)
        print(f"[{self.name}] menerima {actual_damage} damage! (Sisa HP: {self.__current_hp}/{self._max_hp})")

    # Fungsi untuk mengonsumsi mana
    def consume_mana(self, amount: int) -> bool:
        if self.__current_mana >= amount:
            self.__current_mana -= amount
            print(f"[{self.name}] menggunakan {amount} Mana. (Sisa Mana: {self.__current_mana}/{self._max_mana})")
            return True
        else:
            print(f"[{self.name}] gagal menggunakan skill! Mana tidak cukup.")
            return False

    # Serangan dasar biasa (tanpa mana)
    def basic_attack(self, target: 'Character'):
        print(f"\n{self.name} melakukan serangan dasar ke {target.name}!")
        target.take_damage(self.base_attack)

    # Abstraction: Fungsi ini WAJIB di-override oleh class turunannya nanti
    @abstractmethod
    def use_special_skill(self, target: 'Character'):
        """Gunakan skill khusus yang mengonsumsi mana. Implementasi ada di class turunan."""
        pass

    def heal(self, amount: int):
        """Memulihkan HP tanpa melebihi batas maksimal."""
        self.__current_hp = min(self._max_hp, self.__current_hp + amount)
        print(f"[{self.name}] dipulihkan sebesar {amount} HP! (HP: {self.__current_hp}/{self._max_hp})")

    def restore_mana(self, amount: int):
        """Memulihkan Mana tanpa melebihi batas maksimal."""
        self.__current_mana = min(self._max_mana, self.__current_mana + amount)
        print(f"[{self.name}] memulihkan {amount} Mana! (Mana: {self.__current_mana}/{self._max_mana})")