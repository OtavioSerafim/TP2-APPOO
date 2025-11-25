from abc import ABC, abstractmethod

class Note(ABC):
    """Classe abstrata das notas"""
    def __init__(self, spawn_time: float, hit_time: float, note_type: str):
        self.spawn_time = spawn_time
        self.hit_time = hit_time
        self.note_type = note_type
        self.spawned = False
        self.active = False
        self.x = 0.0
        self.y = 0
        self.state = None        # None | 'fading' | 'falling'
        self.result = None       # 'perfect' | 'good' | 'miss'
        self.fade_elapsed = 0.0
        self.fade_total = 0.4
        self.alpha = 255
        self.vy = 0.0
        self.key_mistaken = False

    @abstractmethod
    def note_sound(self):
        pass