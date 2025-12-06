from typing import Optional


class UnplayableError(Exception):
    """Raised when a note cannot be played on the instrument."""

    pass


class Note:
    """Basic timed note with optional assigned output value. Also used for final values."""

    def __init__(self, start_time: float, end_time: float, value: Optional[int] = None) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.value = value

    def set_final_value(self, value: int) -> None:
        self.value = value

    def get_final_value(self) -> int:
        if self.value is None:
            raise ValueError("Final value has not been set.")
        return self.value


class NoteCandidate(Note):
    """
    A note extended with candidate fret positions across all strings.

    Parameters
    ----------
    candidates : list[int]
        Possible fret values per string; -1 where the note is unplayable.
    """

    def __init__(self, candidates: list[int], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.candidates = candidates

        if len(candidates) != 6:
            raise ValueError("Candidates list must have length 6.")

        if all(v == -1 for v in candidates):
            raise UnplayableError("This note is unplayable in current tuning.")
