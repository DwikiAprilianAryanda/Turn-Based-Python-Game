# models/equipment.py

class EquipmentDecorator:
    """
    Base Decorator Class.
    Secara transparan membungkus objek Character asli.
    """
    def __init__(self, character):
        self._character = character

    def __getattr__(self, name):
        # Teruskan semua panggilan metode/atribut (seperti take_damage, current_hp) ke karakter asli
        return getattr(self._character, name)


class Weapon(EquipmentDecorator):
    def __init__(self, character, weapon_name: str, bonus_attack: int):
        super().__init__(character)
        self.weapon_name = weapon_name
        self.bonus_attack = bonus_attack

    @property
    def base_attack(self):
        # Mencegat panggilan base_attack, lalu menambahkan status asli dengan bonus senjata
        return self._character.base_attack + self.bonus_attack

    @property
    def name(self):
        # Mengubah nama karakter untuk menampilkan senjata yang dipakai
        return f"{self._character.name} \n(+ {self.weapon_name})"


class Armor(EquipmentDecorator):
    def __init__(self, character, armor_name: str, bonus_defense: int):
        super().__init__(character)
        self.armor_name = armor_name
        self.bonus_defense = bonus_defense

    @property
    def defense(self):
        # Mencegat panggilan defense, menambahkan status asli dengan bonus zirah
        return self._character.defense + self.bonus_defense

    @property
    def name(self):
        return f"{self._character.name} \n(+ {self.armor_name})"