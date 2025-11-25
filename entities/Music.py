import pathlib

class Music:
    """Classe das músicas"""
    def __init__(self, title: str, csv_path: pathlib.Path, mp3_path: pathlib.Path):
        self.title = title
        self.csv_path = csv_path
        self.mp3_path = mp3_path