# models/element.py

class Element:
    API = "Api 🔥"
    AIR = "Air 💧"
    DAUN = "Daun 🍃"
    NETRAL = "Netral ⚪"

    @staticmethod
    def get_multiplier(attacker_elem: str, defender_elem: str) -> float:
        # Jika elemen sama (selain netral), serangan menjadi resisten (kurang efektif)
        if attacker_elem == defender_elem and attacker_elem != Element.NETRAL:
            return 0.8
        
        # Logika Super Efektif (Kelemahan Musuh)
        if attacker_elem == Element.API and defender_elem == Element.DAUN: return 1.5
        if attacker_elem == Element.DAUN and defender_elem == Element.AIR: return 1.5
        if attacker_elem == Element.AIR and defender_elem == Element.API: return 1.5
        
        # Logika Tidak Efektif (Musuh Kuat Terhadap Elemen Ini)
        if attacker_elem == Element.API and defender_elem == Element.AIR: return 0.5
        if attacker_elem == Element.DAUN and defender_elem == Element.API: return 0.5
        if attacker_elem == Element.AIR and defender_elem == Element.DAUN: return 0.5
        
        # Default jika tidak ada interaksi spesial
        return 1.0