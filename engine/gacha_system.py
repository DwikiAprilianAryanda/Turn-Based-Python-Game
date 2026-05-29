# engine/gacha_system.py
import random

class GachaSystem:
    COST_PER_PULL = 100

    # Format Baru: Ditambahkan "lore" untuk kisah item
    ITEM_POOL = {
        "Pedang Kayu": {"bonus_atk": 5, "bonus_def": 0, "rarity": "Common", "img": "assets/pedang_kayu.png", "desc": "+5 ATK", "lore": "Pedang usang yang biasa digunakan oleh prajurit pemula. Tidak tajam, tapi cukup untuk memukul mundur slime."},
        "Zirah Kain": {"bonus_atk": 0, "bonus_def": 5, "rarity": "Common", "img": "assets/zirah_kain.png", "desc": "+5 DEF", "lore": "Pakaian tebal berbahan dasar wol murahan. Lebih cocok dipakai tidur daripada untuk berperang."},
        
        "Tombak Ksatria": {"bonus_atk": 20, "bonus_def": 0, "rarity": "Rare", "img": "assets/tombak.png", "desc": "+20 ATK", "lore": "Tombak standar milik pasukan elit kerajaan. Ujungnya ditempa dengan baja berkualitas tinggi."},
        "Zirah Baja": {"bonus_atk": 0, "bonus_def": 20, "rarity": "Rare", "img": "assets/zirah_baja.png", "desc": "+20 DEF", "lore": "Meskipun berat, zirah ini telah menyelamatkan banyak nyawa prajurit di garis depan."},
        
        "Pedang Iblis": {"bonus_atk": 60, "bonus_def": -15, "rarity": "Legendary", "img": "assets/pedang_iblis.png", "desc": "Kuat tapi rapuh (+60 ATK, -15 DEF)", "lore": "Pedang terkutuk yang haus akan darah. Penggunanya mendapatkan kekuatan luar biasa, namun jiwanya perlahan terkikis."},
        "Zirah Duri Beracun": {"bonus_atk": -10, "bonus_def": 60, "rarity": "Legendary", "img": "assets/zirah_duri.png", "desc": "Tebal tapi berat (-10 ATK, +60 DEF)", "lore": "Diambil dari kulit monster naga beracun. Melindungi pemakainya, namun durinya menghalangi pergerakan menyerang."},
        
        "Mahkota Raja Iblis": {"bonus_atk": 150, "bonus_def": -50, "rarity": "Mythic", "img": "assets/mahkota.png", "desc": "Mengorbankan pertahanan (+150 ATK, -50 DEF)", "lore": "Benda paling berbahaya di muka bumi. Siapapun yang memakainya akan memiliki kekuatan setara dewa, namun satu tebasan fatal bisa mengakhiri hidupnya."},
        "Aegis Shield": {"bonus_atk": -20, "bonus_def": 150, "rarity": "Mythic", "img": "assets/aegis.png", "desc": "Tembok tak tertembus (-20 ATK, +150 DEF)", "lore": "Perisai mitologi yang konon ditempa di surga. Tidak ada serangan yang bisa menembusnya, membuat penggunanya menjadi benteng berjalan."}
    }

    @staticmethod
    def pull_item():
        chance = random.randint(1, 100)
        
        if chance <= 3: target_rarity = "Mythic"
        elif chance <= 8: target_rarity = "Legendary"
        elif chance <= 30: target_rarity = "Rare"
        else: target_rarity = "Common"
            
        possible_items = [name for name, data in GachaSystem.ITEM_POOL.items() if data["rarity"] == target_rarity]
        pulled_item_name = random.choice(possible_items)
        
        return pulled_item_name, target_rarity