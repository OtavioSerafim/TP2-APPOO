from ..Note import Note
import pathlib
import pygame

class Agudo(Note):
    def __init__(self, spawn_time: float, hit_time: float):
        super().__init__(spawn_time, hit_time, "a")

    @staticmethod
    def note_sound(self) -> None:
        """Reproduz agudo.wav desta pasta."""
        folder = pathlib.Path(__file__).parent
        wav_path = folder / "agudo.wav"
        if not wav_path.exists():
            print("Agudo.note_sound: arquivo agudo.wav não encontrado.")
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(str(wav_path))
            sound.play()
        except pygame.error as e:
            print(f"Agudo.note_sound: erro ao reproduzir agudo.wav: {e}")