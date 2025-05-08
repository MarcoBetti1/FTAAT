import json, sqlite3
from pathlib import Path
from tqdm import tqdm   # nice progress when run standalone
from .db_utils import get_conn
from config import RESULTS_ROOT
# RESULTS_ROOT = Path("results")

def import_json_dir(root: Path = RESULTS_ROOT) -> int:
    conn, cur = get_conn(), get_conn().cursor()
    new_rows  = 0

    for fp in root.rglob("*.json"):
        data = json.loads(fp.read_text())
        base = {
            "id":        data["id"],
            "provider":  data["provider"],
            "model":     data["model"],
            "num_facts": data["num_facts"],
            "k":         data["k"],
        }
        for t in data["trials"]:
            row = (
                base["id"], base["provider"], base["model"],
                base["num_facts"], base["k"],
                t["trial"],
                t["sequence_accuracy"], t["token_accuracy"],
                int(t["major_format_flaw"]),
                t.get("response_time_ms"),            
                t.get("prompt_tokens"),               
                t["prompt_text"], t["response_text"], t["expected_response_text"]
            )
            try:
                cur.execute("""INSERT INTO trials
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", row)
                new_rows += 1
            except sqlite3.IntegrityError:
                pass       # duplicate

    conn.commit()
    return new_rows

if __name__ == "__main__":
    print(f"Imported {import_json_dir()} new rows")