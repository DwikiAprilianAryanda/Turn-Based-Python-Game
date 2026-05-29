# engine/gacha_system.py
import random

class GachaSystem:
    # Harga untuk 1x Tarikan Gacha
    COST_PER_PULL = 100

    # Database Item Gacha (Nama Item: Atribut)
    ITEM_POOL = {
        "Pedang Kayu": {"type": "Weapon", "bonus": 5, "rarity": "Common"},
        "Zirah Kain": {"type": "Armor", "bonus": 5, "rarity": "Common"},
        "Tombak Ksatria": {"type": "Weapon", "bonus": 20, "rarity": "Rare"},
        "Zirah Baja": {"type": "Armor", "bonus": 20, "rarity": "Rare"},
        "Pedang Excalibur": {"type": "Weapon", "bonus": 50, "rarity": "Legendary"},
        "Zirah Sisik Naga": {"type": "Armor", "bonus": 50, "rarity": "Legendary"}
    }

    @staticmethod
    def pull_item():
        """Sistem RNG (Random Number Generator) untuk Gacha"""
        chance = random.randint(1, 100)
        
        # Penentuan tingkat kelangkaan (Drop Rate)
        if chance <= 5: # 5% Peluang Legendary
            target_rarity = "Legendary"
        elif chance <= 30: # 25% Peluang Rare (30 - 5)
            target_rarity = "Rare"
        else: # 70% Peluang Common
            target_rarity = "Common"
            
        # Saring item yang sesuai dengan rarity terpilih
        possible_items = [name for name, data in GachaSystem.ITEM_POOL.items() if data["rarity"] == target_rarity]
        
        # Pilih satu item acak dari daftar yang sudah disaring
        pulled_item_name = random.choice(possible_items)
        
        return pulled_item_name, target_rarity