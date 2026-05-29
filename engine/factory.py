# engine/factory.py
# KITA UBAH IMPORT-NYA AGAR MENGAMBIL DARI SATU FILE YANG SUDAH KITA UPDATE
from models.character import Emperor, Gladiator, Assassin, Mage, Knight, Valkyrie

class CharacterFactory:
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
            raise ValueError(f"Tipe karakter tidak dikenal: {char_type}")