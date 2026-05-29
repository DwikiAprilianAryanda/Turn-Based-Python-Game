# engine/gacha_system.py
import random

class GachaSystem:
    COST_PER_PULL = 100

    # Format Baru: Termasuk Bonus ATK, Bonus DEF (bisa minus), Path Gambar, dan Deskripsi
    ITEM_POOL = {
        "Pedang Kayu": {"bonus_atk": 5, "bonus_def": 0, "rarity": "Common", "img": "assets/pedang_kayu.png", "desc": "+5 ATK"},
        "Zirah Kain": {"bonus_atk": 0, "bonus_def": 5, "rarity": "Common", "img": "assets/zirah_kain.png", "desc": "+5 DEF"},
        
        "Tombak Ksatria": {"bonus_atk": 20, "bonus_def": 0, "rarity": "Rare", "img": "assets/tombak.png", "desc": "+20 ATK"},
        "Zirah Baja": {"bonus_atk": 0, "bonus_def": 20, "rarity": "Rare", "img": "assets/zirah_baja.png", "desc": "+20 DEF"},
        
        # ITEM DENGAN TRADE-OFF (DEBUFF)
        "Pedang Iblis": {"bonus_atk": 60, "bonus_def": -15, "rarity": "Legendary", "img": "assets/pedang_iblis.png", "desc": "Kuat tapi rapuh (+60 ATK, -15 DEF)"},
        "Zirah Duri Beracun": {"bonus_atk": -10, "bonus_def": 60, "rarity": "Legendary", "img": "assets/zirah_duri.png", "desc": "Sangat tebal tapi berat (-10 ATK, +60 DEF)"},
        
        # TIER BARU: MYTHIC (3%)
        "Mahkota Raja Iblis": {"bonus_atk": 150, "bonus_def": -50, "rarity": "Mythic", "img": "assets/mahkota.png", "desc": "Kekuatan gila, mengorbankan pertahanan (+150 ATK, -50 DEF)"},
        "Aegis Shield": {"bonus_atk": -20, "bonus_def": 150, "rarity": "Mythic", "img": "assets/aegis.png", "desc": "Tembok tak tertembus (-20 ATK, +150 DEF)"}
    }

    @staticmethod
    def pull_item():
        chance = random.randint(1, 100)
        
        # RNG System: Mythic 3%, Legendary 5%, Rare 22%, Common 70%
        if chance <= 3:
            target_rarity = "Mythic"
        elif chance <= 8:  # 3 + 5
            target_rarity = "Legendary"
        elif chance <= 30: # 8 + 22
            target_rarity = "Rare"
        else:
            target_rarity = "Common"
            
        possible_items = [name for name, data in GachaSystem.ITEM_POOL.items() if data["rarity"] == target_rarity]
        pulled_item_name = random.choice(possible_items)
        
        return pulled_item_name, target_rarity