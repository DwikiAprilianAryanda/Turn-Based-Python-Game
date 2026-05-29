# engine/commands.py
import random
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self, attacker, target, *args, **kwargs):
        pass

class BasicAttackCommand(Command):
    def execute(self, attacker, target):
        chance = random.randint(1, 100)
        
        if chance <= 10: 
            return "DODGE"
        
        if chance <= attacker.critical_chance: 
            # CRITICAL: Damage 2x Lipat dari Base Attack
            damage = attacker.base_attack * 2
            target.take_damage(damage, attacker) 
            return "CRIT"
            
        # HIT NORMAL
        damage = attacker.base_attack
        target.take_damage(damage, attacker)
        return "HIT"

class SpecialSkillCommand(Command):
    def execute(self, attacker, target):
        # Langsung tembak ke fungsi Skill di masing-masing karakter
        return attacker.use_special_skill(target)

class UltimateCommand(Command):
    def execute(self, attacker, target, enemy_party=None, ally_party=None):
        # Cek apakah Ultimate masih dalam Cooldown
        if attacker.current_ulti_cd > 0:
            return "FAIL", f"Ultimate belum siap! (Sisa {attacker.current_ulti_cd} Turn)"
        
        # Reset Cooldown dan Eksekusi
        attacker.current_ulti_cd = attacker.ultimate_cd
        damage, log = attacker.use_ultimate(target, enemy_party, ally_party)
        return "ULTIMATE", log

class UseItemCommand(Command):
    def __init__(self, item):
        self.item = item
        
    def execute(self, attacker, target=None):
        self.item.use(attacker)
        return "HEAL"