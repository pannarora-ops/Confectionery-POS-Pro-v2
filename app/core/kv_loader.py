from pathlib import Path
from kivy.lang import Builder


def load_all_kv():
    root = Path(__file__).resolve().parents[1]

    print("=" * 50)
    print("KV Root:", root)

    for kv in root.rglob("*.kv"):
        print("Loading:", kv)
        Builder.load_file(str(kv))

    print("=" * 50)