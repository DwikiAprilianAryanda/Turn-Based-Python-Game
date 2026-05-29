from abc import ABC, abstractmethod
from models.element import Element

class Character(ABC):
    # Ubah baris def __init__ menjadi seperti ini:
    def __init__(self, name: str, max_hp: int, max_mana: int, base_attack: int, defense: int, element: str = Element.NETRAL):
        self.element = element
        self.base_name = name # Simpan nama asli tanpa elemen/level
        self.name = f"{name} [{self.element}]" 
        
        self._max_hp = max_hp
        self.__current_hp = max_hp
        self._max_mana = max_mana
        self.__current_mana = max_mana
        self.base_attack = base_attack
        self.defense = defense
        self.active_effects = []
        
        self.level = 1
        self.exp = 0

    def apply_scaling(self, level: int, stat_multiplier: float = 1.0):
        """Skala dinamis: Atribut naik 10% per level."""
        self.level = level
        
        # Rumus: 1.0 (Level 1), 1.1 (Level 2), 1.2 (Level 3), dst.
        level_scale = 1.0 + ((level - 1) * 0.1)
        
        # Terapkan pengali level dikali pengali kesulitan musuh
        self._max_hp = int(self._max_hp * level_scale * stat_multiplier)
        self.__current_hp = self._max_hp
        
        self.base_attack = int(self.base_attack * level_scale * stat_multiplier)
        self.defense = int(self.defense * level_scale * stat_multiplier)
        
        # Update UI Teks Nama agar pemain bisa melihat Levelnya di layar
        self.name = f"Lv.{self.level} {self.base_name} [{self.element}]"

    # Menggunakan decorator @property sebagai Getter (Read-only access)
    @property
    def current_hp(self) -> int:
        return self.__current_hp

    @property
    def current_mana(self) -> int:
        return self.__current_mana

    # Fungsi untuk menerima serangan
    def take_damage(self, raw_damage: int):
        # PERBAIKAN 1: Gunakan self.defense, bukan self.base_defense
        actual_damage = max(0, int(raw_damage) - self.defense)
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
    def basic_attack(self, target):
        # Hitung pengali elemen
        multiplier = Element.get_multiplier(self.element, target.element)
        
        # PERBAIKAN 2: Jangan kurangi defense di sini, biarkan take_damage yang mengurusnya!
        raw_damage = self.base_attack * multiplier
        
        if multiplier > 1.0:
            print(f"SUPER EFEKTIF! Damage x{multiplier}")
        elif multiplier < 1.0:
            print(f"Kurang efektif... Damage x{multiplier}")
            
        # Langsung lempar raw_damage ke target
        target.take_damage(raw_damage)

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

    def add_effect(self, effect):
        """Menambahkan efek ke karakter"""
        self.active_effects.append(effect)
        effect.apply_initial_effect(self)

    def process_effects(self) -> str:
        """Memproses semua efek yang sedang aktif di awal giliran"""
        log_msgs = []
        for effect in self.active_effects[:]: # Salin list untuk iterasi yang aman
            msg = effect.apply_turn_effect(self)
            if msg:
                log_msgs.append(msg)

            # Hapus efek jika durasi sudah habis
            if effect.duration <= 0:
                effect.remove_effect(self)
                self.active_effects.remove(effect)
                log_msgs.append(f"Efek {effect.name} pada {self.name} telah pudar.")

        return "\n".join(log_msgs) if log_msgs else ""