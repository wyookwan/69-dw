import json
import logging
from .config import LOG_DIR, OUTPUT_DIR
from .extract import extract_data
from .transform import transform_data
from .load import load_data
from .validate import validate_data

def main():
    LOG_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logging.info("ETL started")

    raw = extract_data()
    customers, products, sales, rejects = transform_data(raw)

    rejects.to_csv(OUTPUT_DIR / "rejects.csv", index=False)

    load_data(customers, products, sales)

    result = validate_data(sales)
    (OUTPUT_DIR / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    logging.info("ETL completed")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
