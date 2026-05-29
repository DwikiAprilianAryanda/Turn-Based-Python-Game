# engine/save_manager.py
import json
import os

SAVE_FILE = "save_data.json"

# Tambahkan "gold_reward" di aturan kesulitan
DIFFICULTY_SETTINGS = {
    "EASY": {"enemy_cap": 10, "stat_mult": 0.8, "exp_mult": 1.0, "gold_reward": 50},
    "MEDIUM": {"enemy_cap": 30, "stat_mult": 1.0, "exp_mult": 1.5, "gold_reward": 100},
    "HARD": {"enemy_cap": 100, "stat_mult": 1.3, "exp_mult": 2.5, "gold_reward": 150}
}

class SaveManager:
    """Manajer I/O untuk Persistensi Data RPG"""
    
    @staticmethod
    def load_data():
        if not os.path.exists(SAVE_FILE):
            return {"characters": {}, "gold": 0, "inventory": []}
            
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            
            # MIGRASI STRUKTUR LAMA: Jika data lama tidak punya "characters"
            if "characters" not in data:
                migrated_data = {"characters": data, "gold": 0, "inventory": []}
                return migrated_data
                
            return data

    @staticmethod
    def save_data(data):
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_character_data(char_type: str):
        data = SaveManager.load_data()
        return data["characters"].get(char_type, {"level": 1, "exp": 0})

    @staticmethod
    def add_exp(char_type: str, amount: int):
        data = SaveManager.load_data()
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

        SaveManager.save_data(data)
        return char_data["level"], leveled_up

    # --- FITUR BARU: MANAJEMEN GOLD ---
    @staticmethod
    def add_gold(amount: int):
        data = SaveManager.load_data()
        data["gold"] += amount
        SaveManager.save_data(data)
        return data["gold"]

    @staticmethod
    def get_gold():
        return SaveManager.load_data().get("gold", 0)

    # --- FITUR BARU: MANAJEMEN INVENTORY (Persiapan Tahap 2) ---
    @staticmethod
    def add_item_to_inventory(item_name: str):
        data = SaveManager.load_data()
        data["inventory"].append(item_name)
        SaveManager.save_data(data)
        
    @staticmethod
    def get_inventory():
        return SaveManager.load_data().get("inventory", [])