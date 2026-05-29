# models/equipment.py
from models.character import Character

class Equipment(Character):
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
        return max(1, self._character.base_attack + self._bonus_atk)

    @property
    def defense(self):
        return max(0, self._character.defense + self._bonus_def)

    # --- JEMBATAN STATUS HP (LENGKAP) ---
    @property
    def current_hp(self):
        return self._character.current_hp
    
    @current_hp.setter
    def current_hp(self, value):
        self._character.current_hp = value

    @property
    def _max_hp(self):
        return self._character._max_hp

    # --- JEMBATAN STATUS MANA (LENGKAP) ---
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

    # --- FUNGSI WAJIB LAINNYA ---
    def heal(self, amount):
        self._character.heal(amount)

    def take_damage(self, amount, attacker=None):
        return self._character.take_damage(amount, attacker)
        
    def __getattr__(self, name):
        # Ini akan otomatis meneruskan fungsi ultimate, on_turn_start, dll ke karakter asli!
        return getattr(self._character, name)
        
    def apply_scaling(self, level, stat_multiplier):
        self._character.apply_scaling(level, stat_multiplier)
        
    def process_effects(self):
        return self._character.process_effects()

    def use_special_skill(self, target):
        return self._character.use_special_skill(target)
    
    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        return self._character.use_ultimate(target, enemy_party, ally_party)