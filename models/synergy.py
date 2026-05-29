# models/synergy.py
from models.character import Character

class SynergyBuff(Character):
    """
    Decorator khusus untuk menerapkan efek Sinergi Tim.
    Membungkus karakter (atau karakter yang sudah ber-equipment).
    """
    def __init__(self, character: Character, synergy_type: str):
        self._character = character
        self.synergy_type = synergy_type

    @property
    def name(self):
        return self._character.name

    @property
    def base_attack(self):
        final_atk = self._character.base_attack
        # INFERNO memberikan +20% Attack
        if self.synergy_type == "INFERNO":
            return int(final_atk * 1.2) 
        return final_atk

    @property
    def defense(self):
        final_def = self._character.defense
        # NATURE memberikan +20% Defense
        if self.synergy_type == "NATURE":
            return int(final_def * 1.2) 
        return final_def

    # --- JEMBATAN STATUS HP & MANA ---
    @property
    def current_hp(self): return self._character.current_hp
    @current_hp.setter
    def current_hp(self, value): self._character.current_hp = value

    @property
    def _max_hp(self): return self._character._max_hp

    @property
    def current_mana(self): return self._character.current_mana
    @current_mana.setter
    def current_mana(self, value): self._character.current_mana = value

    @property
    def _max_mana(self): return self._character._max_mana

    @property
    def element(self): return self._character.element

    # --- PENERUSAN FUNGSI WAJIB ---
    def heal(self, amount): self._character.heal(amount)
    def take_damage(self, amount, attacker=None):
        return self._character.take_damage(amount, attacker)
        
    def __getattr__(self, name):
        # Ini akan otomatis meneruskan fungsi ultimate, on_turn_start, dll ke karakter asli!
        return getattr(self._character, name)
    def apply_scaling(self, level, stat_multiplier): self._character.apply_scaling(level, stat_multiplier)
    def use_special_skill(self, target): return self._character.use_special_skill(target)

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        return self._character.use_ultimate(target, enemy_party, ally_party)

    # --- INTERSEPSI EFEK PASIF GILIRAN ---
    def process_effects(self):
        logs = ""
        
        # 1. OCEANIC: Regen 5% Max HP setiap giliran
        if self.synergy_type == "OCEANIC":
            regen = max(1, int(self._max_hp * 0.05))
            self.heal(regen)
            logs += f"🌊 [OCEANIC] {self.name} memulihkan {regen} HP!\n"
            
        # 2. TRINITY: Menghapus/membersihkan racun secara instan
        elif self.synergy_type == "TRINITY":
            if hasattr(self._character, 'status_effects') and self._character.status_effects:
                self._character.status_effects.clear()
                logs += f"✨ [TRINITY] Semua debuff pada {self.name} dinetralkan!\n"

        # 3. Teruskan efek asli karakter (misal luka bakar, racun dari musuh)
        char_logs = self._character.process_effects()
        if char_logs:
            logs += char_logs
            
        return logs.strip()