from pathlib import Path

import wfdb

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
EXPECTED_RECORDS = 48


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    wfdb.dl_database("mitdb", str(RAW_DIR))

    records = sorted(p.stem for p in RAW_DIR.glob("*.hea"))
    missing = [r for r in records if not (RAW_DIR / f"{r}.dat").exists() or not (RAW_DIR / f"{r}.atr").exists()]
    if len(records) != EXPECTED_RECORDS or missing:
        raise SystemExit(f"Incomplete download: {len(records)} headers, missing .dat/.atr for {missing}")

    print(f"{len(records)} records in {RAW_DIR}")


if __name__ == "__main__":
    main()
