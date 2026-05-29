# engine/factory.py
from models.emperor import Emperor
from models.gladiator import Gladiator
from models.assassin import Assassin
from models.mage import Mage
from models.knight import Knight
from models.valkyrie import Valkyrie

class CharacterFactory:
    """Penerapan Factory Pattern untuk membuat karakter secara dinamis."""
    
    @staticmethod
    def create_character(char_type: str, name: str):
        if char_type == "Emperor":
            return Emperor(name)
        elif char_type == "Gladiator":
            return Gladiator(name)
        elif char_type == "Assassin":
            return Assassin(name)
        elif char_type == "Mage":
            return Mage(name)
        elif char_type == "Knight":
            return Knight(name)
        elif char_type == "Valkyrie":
            return Valkyrie(name)
        else:
            raise ValueError(f"Tipe karakter '{char_type}' tidak ditemukan!")