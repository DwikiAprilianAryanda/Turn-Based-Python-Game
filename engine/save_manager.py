# engine/save_manager.py
import json
import os

# ==========================================
# FIX BUG: PENAMBAHAN 'exp_mult' UNTUK LAYAR KEMENANGAN
# ==========================================
DIFFICULTY_SETTINGS = {
    # Versi Bahasa Inggris
    "EASY": {"stat_mult": 0.8, "enemy_cap": 10, "exp_mult": 0.8, "gold_reward": 50},
    "NORMAL": {"stat_mult": 1.0, "enemy_cap": 50, "exp_mult": 1.0, "gold_reward": 100},
    "HARD": {"stat_mult": 1.3, "enemy_cap": 99, "exp_mult": 1.5, "gold_reward": 200},

    # Versi Bahasa Indonesia
    "Mudah": {"stat_mult": 0.8, "enemy_cap": 10, "exp_mult": 0.8, "gold_reward": 50},
    "Normal": {"stat_mult": 1.0, "enemy_cap": 50, "exp_mult": 1.0, "gold_reward": 100},
    "Sulit": {"stat_mult": 1.3, "enemy_cap": 99, "exp_mult": 1.5, "gold_reward": 200},

    # Mode Endless (Bonus EXP sedikit lebih besar)
    "Endless": {"stat_mult": 1.0, "enemy_cap": 99, "exp_mult": 1.2, "gold_reward": 150} 
}

class SaveManager:
    FILE_PATH = "save_data.json"

    @staticmethod
    def _load():
        if os.path.exists(SaveManager.FILE_PATH):
            try:
                with open(SaveManager.FILE_PATH, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"inventory": [], "gold": 500} 

    @staticmethod
    def _save(data):
        with open(SaveManager.FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def add_equipment(item_name: str):
        data = SaveManager._load()
        if "inventory" not in data:
            data["inventory"] = []
        data["inventory"].append(item_name)
        SaveManager._save(data)

    # ---> FUNGSI INI YANG SEBELUMNYA HILANG <---
    @staticmethod
    def get_inventory():
        data = SaveManager._load()
        return data.get("inventory", [])

    @staticmethod
    def get_gold():
        return SaveManager._load().get("gold", 500)

    @staticmethod
    def add_gold(amount):
        data = SaveManager._load()
        data["gold"] = data.get("gold", 500) + amount
        SaveManager._save(data)

    @staticmethod
    def deduct_gold(amount):
        data = SaveManager._load()
        current = data.get("gold", 500)
        if current >= amount:
            data["gold"] = current - amount
            SaveManager._save(data)
            return True
        return False
    
    # ---> TAMBAHKAN FUNGSI INI DI BAGIAN BAWAH KELAS SaveManager <---
    @staticmethod
    def get_character_data(char_type: str):
        """Mengambil data level dan EXP karakter dari save data."""
        data = SaveManager._load()
        # Jika belum ada data 'characters' di file save, buat dictionary kosong
        characters_data = data.get("characters", {})
        
        # Kembalikan data karakter, jika belum ada, beri default level 1
        return characters_data.get(char_type, {"level": 1, "exp": 0})
        
    @staticmethod
    def save_character_data(char_type: str, level: int, exp: int):
        """Menyimpan progress level karakter (jika dibutuhkan setelah menang)."""
        data = SaveManager._load()
        if "characters" not in data:
            data["characters"] = {}
            
        data["characters"][char_type] = {"level": level, "exp": exp}
        SaveManager._save(data)

    @staticmethod
    def add_exp(char_type: str, amount: int):
        # FIX: Gunakan _load() bukan load_data()
        data = SaveManager._load()
        
        # Pastikan dictionary 'characters' sudah ada
        if "characters" not in data:
            data["characters"] = {}
            
        if char_type not in data["characters"]:
            data["characters"][char_type] = {"level": 1, "exp": 0}

        char_data = data["characters"][char_type]
        char_data["exp"] += amount

        leveled_up = False
        max_exp = char_data["level"] * 100
        
        while char_data["exp"] >= max_exp:
            char_data["exp"] -= max_exp
            char_data["level"] += 1
            max_exp = char_data["level"] * 100
            leveled_up = True

        # FIX: Gunakan _save() bukan save_data()
        SaveManager._save(data)
        
        return char_data["level"], leveled_up
    
    # ---> TAMBAHKAN 3 FUNGSI INI DI PALING BAWAH KELAS SaveManager <---
    @staticmethod
    def save_endless_state(floor: int, party_names: list):
        """Menyimpan lantai dan tim pemain saat memutuskan keluar sementara."""
        data = SaveManager._load()
        data["endless_state"] = {"floor": floor, "party": party_names}
        SaveManager._save(data)

    @staticmethod
    def get_endless_state():
        """Mengecek apakah ada save data endless yang belum tamat."""
        return SaveManager._load().get("endless_state", None)

    @staticmethod
    def clear_endless_state():
        """Menghapus save data endless jika pemain mati atau mengambil Gold."""
        data = SaveManager._load()
        if "endless_state" in data:
            del data["endless_state"]
            SaveManager._save(data)