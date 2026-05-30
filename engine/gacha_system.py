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
        
        if chance <= 2: target_rarity = "Mythic"
        elif chance <= 5: target_rarity = "Legendary"
        elif chance <= 30: target_rarity = "Rare"
        else: target_rarity = "Common"
            
        possible_items = [name for name, data in GachaSystem.ITEM_POOL.items() if data["rarity"] == target_rarity]
        pulled_item_name = random.choice(possible_items)
        
        return pulled_item_name, target_rarity
    
    # ---> TAMBAHKAN FUNGSI INI DI PALING BAWAH KELAS GachaSystem <---
    @staticmethod
    def get_enemy_equipment(difficulty: str, floor: int = 0):
        import random
        allowed_rarities = ["Common"]
        
        # Aturan Mode Standar
        if difficulty in ["EASY", "Mudah"]:
            allowed_rarities = ["Common"]
        elif difficulty in ["NORMAL", "Normal"]:
            allowed_rarities = ["Common", "Rare"]
        elif difficulty in ["HARD", "Sulit"]:
            allowed_rarities = ["Rare", "Legendary", "Mythic"]
            
        # Aturan Mode Endless (Menyiksa secara perlahan)
        elif difficulty == "Endless":
            if floor <= 10:
                allowed_rarities = ["Common"]
            elif floor <= 15:
                allowed_rarities = ["Common", "Rare"]
            elif floor <= 30:
                allowed_rarities = ["Rare", "Legendary"]
            else:
                allowed_rarities = ["Legendary", "Mythic"]
                
        # Saring item yang sesuai kasta
        possible_items = [
            name for name, data in GachaSystem.ITEM_POOL.items() 
            if data.get("rarity", "Common") in allowed_rarities
        ]
        
        # Keamanan cadangan jika list kosong
        if not possible_items: 
            return random.choice(list(GachaSystem.ITEM_POOL.keys()))
            
        return random.choice(possible_items)