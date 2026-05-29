# engine/save_manager.py
import json
import os

SAVE_FILE = "save_data.json"

# Aturan Kesulitan & Batasan Level Musuh (Opsi A)
DIFFICULTY_SETTINGS = {
    "EASY": {"enemy_cap": 10, "stat_mult": 0.8, "exp_mult": 1.0},
    "MEDIUM": {"enemy_cap": 30, "stat_mult": 1.0, "exp_mult": 1.5},
    "HARD": {"enemy_cap": 100, "stat_mult": 1.3, "exp_mult": 2.5}
}

class SaveManager:
    """Manajer I/O untuk Persistensi Data Leveling Karakter"""
    
    @staticmethod
    def load_data():
        if not os.path.exists(SAVE_FILE):
            return {}
        with open(SAVE_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def save_data(data):
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_character_data(char_type: str):
        data = SaveManager.load_data()
        # Jika karakter baru pertama kali dipakai, berikan Level 1 dan EXP 0
        return data.get(char_type, {"level": 1, "exp": 0})

    @staticmethod
    def add_exp(char_type: str, amount: int):
        data = SaveManager.load_data()
        if char_type not in data:
            data[char_type] = {"level": 1, "exp": 0}

        char_data = data[char_type]
        char_data["exp"] += amount

        # Algoritma Kenaikan Level (Butuh 100 EXP * Level Saat Ini)
        leveled_up = False
        max_exp = char_data["level"] * 100
        
        while char_data["exp"] >= max_exp:
            char_data["exp"] -= max_exp
            char_data["level"] += 1
            max_exp = char_data["level"] * 100
            leveled_up = True

        SaveManager.save_data(data)
        return char_data["level"], leveled_up