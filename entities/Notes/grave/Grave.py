from ..Note import Note
import pathlib
import pygame

class Grave(Note):
    def __init__(self, spawn_time: float, hit_time: float):
        super().__init__(spawn_time, hit_time, "g")

    @staticmethod
    def note_sound(self) -> None:
        """Reproduz grave.wav desta pasta."""
        folder = pathlib.Path(__file__).parent
        wav_path = folder / "grave.wav"
        if not wav_path.exists():
            print("grave.note_sound: arquivo grave.wav não encontrado.")
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(str(wav_path))
            sound.play()
        except pygame.error as e:
            print(f"grave.note_sound: erro ao reproduzir grave.wav: {e}")