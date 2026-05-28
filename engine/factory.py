# engine/factory.py
from models.emperor import Emperor
from models.gladiator import Gladiator

class CharacterFactory:
    """Penerapan Factory Pattern untuk membuat karakter secara dinamis."""
    
    @staticmethod
    def create_character(char_type: str, name: str):
        if char_type == "Emperor":
            return Emperor(name)
        elif char_type == "Gladiator":
            return Gladiator(name)
        else:
            raise ValueError(f"Tipe karakter '{char_type}' tidak ditemukan!")