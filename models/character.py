# models/character.py
import random
from abc import ABC, abstractmethod

class Character(ABC):
    def __init__(self, name, hp, attack, defense, speed, element="Netral"):
        self.name = name
        self._max_hp = hp
        self.current_hp = hp
        self._max_mana = 100
        self.current_mana = 100
        self._base_attack = attack
        self._base_defense = defense
        self.speed = speed
        self.element = element
        
        # Sistem Ultimate & Pasif
        self.ultimate_cd = 4
        self.current_ulti_cd = 0
        self.is_invincible = False
        self.passive_logs = ""

    @property
    def base_attack(self): return self._base_attack
    @property
    def defense(self): return self._base_defense
    @property
    def critical_chance(self): return 15

    # Menerima 'attacker' agar bisa memantulkan damage
    def take_damage(self, amount, attacker=None):
        if self.is_invincible:
            self.passive_logs += "[Kebal DMG!] "
            return 0
        
        # FORMULA BALANCE BARU:
        # Minimal damage yang dijamin masuk adalah 15% dari kekuatan serangan asli, 
        # sehingga musuh setebal apapun tetap akan bocor darahnya.
        min_damage = max(1, int(amount * 0.15))
        actual_damage = max(min_damage, amount - self.defense)
        
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage

    def heal(self, amount):
        self.current_hp = min(self._max_hp, self.current_hp + amount)

    # Dipanggil setiap awal giliran
    def on_turn_start(self):
        self.passive_logs = ""
        if self.current_ulti_cd > 0:
            self.current_ulti_cd -= 1
        self.is_invincible = False

    def apply_scaling(self, level, stat_multiplier):
        self._max_hp = int(self._max_hp * stat_multiplier * (1 + 0.1 * level))
        self.current_hp = self._max_hp
        self._base_attack = int(self._base_attack * stat_multiplier * (1 + 0.1 * level))
        self._base_defense = int(self._base_defense * stat_multiplier * (1 + 0.1 * level))

    def process_effects(self):
        return ""

    def use_special_skill(self, target): pass

    def use_ultimate(self, target, enemy_party=None, ally_party=None): pass


# ==========================================
# SUBCLASS KARAKTER & MEKANIK UNIKNYA
# ==========================================

class Emperor(Character):
    def __init__(self, name="Emperor"):
        super().__init__(name, 120, 15, 10, 12, "Api")
        
    def take_damage(self, amount, attacker=None):
        dmg = super().take_damage(amount, attacker)
        if self.current_hp > 0 and self.current_hp < (self._max_hp * 0.5) and attacker:
            reflect = max(1, int(dmg * 0.3))
            attacker.current_hp -= reflect
            self.passive_logs += f"[Pantulan DMG: {reflect}] "
        return dmg

    def use_special_skill(self, target):
        self.current_mana -= 20
        dmg = self.base_attack * 1.5
        return target.take_damage(dmg, self), "menggunakan Titah Kaisar!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        log = "mengaktifkan ABSOLUTE DECREE!\n"
        total_dmg = 0
        if enemy_party:
            for enemy in enemy_party:
                if enemy.current_hp > 0:
                    dmg = max(1, (self.base_attack * 2) - (enemy.defense // 2))
                    enemy.current_hp -= dmg
                    total_dmg += dmg
        return total_dmg, log + f"Seluruh musuh terkena total {total_dmg} DMG!"


class Gladiator(Character):
    def __init__(self, name="Gladiator"):
        super().__init__(name, 150, 12, 8, 10, "Air")
        self.bloodlust_stacks = 0

    def on_turn_start(self):
        super().on_turn_start()
        if self.bloodlust_stacks < 5:
            self.bloodlust_stacks += 1
            self.passive_logs += "[Bloodlust +10% ATK] "

    @property
    def base_attack(self):
        return int(self._base_attack * (1 + (self.bloodlust_stacks * 0.1)))

    def use_special_skill(self, target):
        self.current_mana -= 15
        return target.take_damage(self.base_attack * 1.8, self), "menggunakan Tebasan Barbar!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        dmg = target.take_damage(self.base_attack * 3.5, self)
        log = f"mengeksekusi ARENA EXECUTION! ({dmg} DMG)"
        if target.current_hp <= 0:
            heal_amt = int(self._max_hp * 0.4)
            self.heal(heal_amt)
            log += f"\nGladiator memulihkan {heal_amt} HP!"
        return dmg, log


class Assassin(Character):
    def __init__(self, name="Assassin"):
        super().__init__(name, 90, 25, 5, 20, "Daun")
        self.shadow_stance = True

    def on_turn_start(self):
        super().on_turn_start()
        self.shadow_stance = True
        self.passive_logs += "[Shadow Stance] "

    def take_damage(self, amount, attacker=None):
        self.shadow_stance = False 
        return super().take_damage(amount, attacker)

    @property
    def critical_chance(self):
        return 100 if self.shadow_stance else 15

    def use_special_skill(self, target):
        self.current_mana -= 25
        return target.take_damage(self.base_attack * 2, self), "menyerang dari bayangan!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        dmg = self.base_attack * 3
        target.current_hp -= dmg
        return dmg, f"menusuk titik vital dengan FATAL STRIKE! ({dmg} True DMG)"


class Mage(Character):
    def __init__(self, name="Mage"):
        super().__init__(name, 80, 30, 4, 15, "Api")

    def take_damage(self, amount, attacker=None):
        if self.current_mana >= (self._max_mana * 0.5):
            amount = int(amount * 0.75)
            self.passive_logs += "[Mana Shield Aktif] "
        return super().take_damage(amount, attacker)

    def use_special_skill(self, target):
        self.current_mana -= 30
        return target.take_damage(self.base_attack * 2.2, self), "menembakkan Bola Api!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        log = "memanggil METEOR SWARM!\n"
        total_dmg = 0
        if enemy_party:
            for enemy in enemy_party:
                if enemy.current_hp > 0:
                    dmg = max(1, (self.base_attack * 2.5) - enemy.defense)
                    enemy.current_hp -= dmg
                    total_dmg += dmg
        return total_dmg, log + f"Badai meteor menghasilkan {total_dmg} DMG AoE!"


class Knight(Character):
    def __init__(self, name="Knight"):
        super().__init__(name, 180, 10, 20, 8, "Air")
        self.aegis_stacks = 0

    def take_damage(self, amount, attacker=None):
        if self.aegis_stacks < 10:
            self.aegis_stacks += 1
            self.passive_logs += "[Aegis: +5% DEF] "
        return super().take_damage(amount, attacker)

    @property
    def defense(self):
        return int(self._base_defense * (1 + (self.aegis_stacks * 0.05)))

    def use_special_skill(self, target):
        self.current_mana -= 15
        return target.take_damage(self.base_attack + self.defense, self), "menggunakan Shield Bash!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        dmg = target.take_damage(self.defense * 2, self)
        return dmg, f"menghantam dengan HOLY JUDGEMENT! ({dmg} DMG dari DEF)"


class Valkyrie(Character):
    def __init__(self, name="Valkyrie"):
        # NERF STATS: HP turun tajam (110 -> 90) dan DEF sangat bocor (12 -> 4)
        super().__init__(name, 90, 15, 4, 18, "Daun")

    def on_turn_start(self):
        super().on_turn_start()
        # PASIF BARU (Holy Aura): Mengisi Mana, bukan lagi auto-heal HP
        if self.current_mana < self._max_mana:
            self.current_mana = min(self._max_mana, self.current_mana + 10)
            self.passive_logs += "[Holy Aura: +10 Mana] "

    def use_special_skill(self, target):
        self.current_mana -= 20
        # NERF SKILL: Fitur "self.heal(30)" DIHAPUS. Hanya fokus untuk attack.
        dmg = self.base_attack * 2.2
        return target.take_damage(dmg, self), "melemparkan Light Spear!"

    def use_ultimate(self, target, enemy_party=None, ally_party=None):
        log = "melantunkan HYMN OF VALHALLA!\n"
        # NERF ULTIMATE: Heal area dikurangi dari 40% menjadi 25%. 
        # Fitur "self.is_invincible = True" DIHAPUS total!
        if ally_party:
            for ally in ally_party:
                if ally.current_hp > 0:
                    ally.heal(int(ally._max_hp * 0.25))
        return 0, log + "Seluruh rekan tim memulihkan 25% HP!"