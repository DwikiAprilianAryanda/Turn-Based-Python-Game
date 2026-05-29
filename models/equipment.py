# models/equipment.py
from models.character import Character

class Equipment(Character):
    """
    Decorator Universal untuk Senjata dan Zirah.
    Bisa menangani Buff (nilai positif) dan Debuff (nilai negatif) sekaligus.
    """
    def __init__(self, character: Character, item_name: str, bonus_atk: int, bonus_def: int):
        self._character = character
        self.item_name = item_name
        self._bonus_atk = bonus_atk
        self._bonus_def = bonus_def

    @property
    def name(self):
        return f"{self._character.name} (+ {self.item_name})"

    @property
    def base_attack(self):
        # Mencegah attack menjadi minus jika debuff terlalu besar
        final_atk = self._character.base_attack + self._bonus_atk
        return max(1, final_atk)

    @property
    def defense(self):
        # Mencegah defense menjadi minus
        final_def = self._character.defense + self._bonus_def
        return max(0, final_def)

    # --- PENERUSAN STATUS HP ---
    @property
    def current_hp(self):
        return self._character.current_hp
        
    @current_hp.setter
    def current_hp(self, value):
        self._character.current_hp = value

    @property
    def _max_hp(self):
        return self._character._max_hp

    # --- PENERUSAN STATUS MANA & ELEMEN (YANG SEBELUMNYA KURANG) ---
    @property
    def current_mana(self):
        return self._character.current_mana
        
    @current_mana.setter
    def current_mana(self, value):
        self._character.current_mana = value

    @property
    def _max_mana(self):
        return self._character._max_mana
        
    @property
    def element(self):
        return self._character.element

    # --- PENERUSAN FUNGSI WAJIB KE KARAKTER ASLI ---
    def take_damage(self, amount):
        return self._character.take_damage(amount)
        
    def apply_scaling(self, level, stat_multiplier):
        self._character.apply_scaling(level, stat_multiplier)
        
    def process_effects(self):
        return self._character.process_effects()

    def use_special_skill(self, target):
        return self._character.use_special_skill(target)