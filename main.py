# main.py

# Mengambil class dari dalam folder models dan engine
from models.emperor import Emperor
from models.gladiator import Gladiator
from engine.battle_arena import BattleArena

if __name__ == "__main__":
    p1 = Emperor("Qin Shi Huang")
    p2 = Gladiator("Spartacus")

    arena = BattleArena(p1, p2)
    arena.start_battle()