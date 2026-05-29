# engine/history_manager.py
import json
import os
from datetime import datetime

class HistoryManager:
    """Kelas utilitas untuk menangani penyimpanan riwayat pertandingan (File I/O)."""
    
    FILE_PATH = "match_history.json"

    @staticmethod
    def save_match(winner_name: str, loser_name: str, winner_hp: int):
        # 1. Siapkan data yang ingin disimpan (menggunakan dictionary)
        match_data = {
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pemenang": winner_name,
            "kalah": loser_name,
            "sisa_hp_pemenang": winner_hp
        }

        # 2. Baca data lama jika filenya sudah ada
        history = []
        if os.path.exists(HistoryManager.FILE_PATH):
            try:
                with open(HistoryManager.FILE_PATH, "r") as file:
                    history = json.load(file)
            except json.JSONDecodeError:
                # Jika file kosong atau rusak, mulai dengan list kosong
                history = []

        # 3. Tambahkan data pertandingan baru ke dalam list
        history.append(match_data)

        # 4. Tulis ulang seluruh data ke dalam file JSON
        with open(HistoryManager.FILE_PATH, "w") as file:
            json.dump(history, file, indent=4)
            
        print(f"Riwayat tersimpan: {winner_name} mengalahkan {loser_name}")