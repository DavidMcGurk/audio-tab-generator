class UnplayableError(Exception):
    """Raised when a note cannot be played on the instrument."""

    pass


class Note:
    """Basic timed note."""

    def __init__(self, start_time: float, end_time: float) -> None:
        self.start_time = start_time
        self.end_time = end_time


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

    def to_final_note(self, string: int, fret: int):
        return FinalNote(start_time=self.start_time, end_time=self.end_time, string=string, fret=fret)


class FinalNote(Note):
    """
    The final note, with the calcualted location (string, fret) of where to play.

    """

    def __init__(self, string: int, fret: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.string = string
        self.fret = fret

    def __eq__(self, other) -> bool:
        return (
            self.start_time == other.start_time
            and self.end_time == other.end_time
            and self.string == other.string
            and self.fret == other.fret
        )
