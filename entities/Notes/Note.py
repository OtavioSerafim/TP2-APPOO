from abc import ABC

class Note(ABC):
    """Classe abstrata das notas"""
    def __init__(self, spawn_time: float, hit_time: float, note_type: str):
        self.spawn_time = spawn_time
        self.hit_time = hit_time
        self.note_type = note_type
        self.spawned = False
        self.active = False
        self.x = None
        self.y = None