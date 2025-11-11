from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"

if DB_PATH.exists():
    DB_PATH.unlink()

def _migration_order(sql_path: Path) -> tuple[int, str]:
    """Ordena as migrações pelo prefixo."""
    prefix, _, remainder = sql_path.name.partition("_")
    try:
        return int(prefix), remainder
    except ValueError:
        return float("inf"), sql_path.name


with sqlite3.connect(DB_PATH) as conn:
    # Ordena as migrações pelo prefixo numérico para garantir 10_* depois de 9_*.
    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql"), key=_migration_order):
        conn.executescript(sql_file.read_text(encoding="utf-8"))


print(f"Banco criado em {DB_PATH}")