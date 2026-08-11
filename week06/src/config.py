from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SOURCE_DB = ROOT / "data" / "source_db" / "store.db"
WAREHOUSE_DB = ROOT / "data" / "warehouse" / "warehouse.db"
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"

PROVINCE_MAP = {
    "chonburi": "Chonburi",
    "chon buri": "Chonburi",
    "ชลบุรี": "Chonburi",
    "bangkok": "Bangkok",
    "bkk": "Bangkok",
    "กรุงเทพฯ": "Bangkok",
    "rayong": "Rayong",
    "ระยอง": "Rayong",
    "chanthaburi": "Chanthaburi",
    "chantaburi": "Chanthaburi",
    "จันทบุรี": "Chanthaburi",
}
