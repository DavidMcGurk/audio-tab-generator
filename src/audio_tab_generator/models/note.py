from typing import Optional


class UnplayableError(Exception):
    pass


class Note:
    def __init__(self, start_time: float, end_time: float, value: Optional[int] = None) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.value = value

    def set_final_value(self, value: int) -> None:
        self.value = value

    def get_final_value(self) -> int:
        if self.value is not None:
            return self.value
        else:
            raise ValueError("The final value has not yet been set")


class NoteCandidate(Note):
    def __init__(self, candidates: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.candidates = candidates

        if len(candidates) != 6:
            raise ValueError("Candidates must be a list of length 6")

        if all(string == "-" for string in candidates):
            raise UnplayableError("This note is not playable with the current instrument specifications")
