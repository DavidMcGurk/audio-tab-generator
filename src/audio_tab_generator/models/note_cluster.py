import itertools
from audio_tab_generator.models.note import NoteCandidate, FinalNote, UnplayableError

MAX_STRETCH = 4  # max allowed fret span


class NoteCluster:
    """
    Handles a cluster of notes which overlap in time
    """

    def __init__(self, notes: list[NoteCandidate]) -> None:
        self.notes = sorted(notes, key=lambda n: n.start_time)
        self.strings: dict[int, list[FinalNote]] = {i: [] for i in range(1, 7)}  # 1=high E, 6=low E
        self.optimal: list[FinalNote] = []

    def assign_notes(self) -> None:
        """
        Assign each note to a string such that:
        - Notes on the same string do not overlap in time
        - Movement on fretboard is minimised
        """
        for note in self.notes:
            assigned = False
            candidate_pairs = sorted([(i + 1, f) for i, f in enumerate(note.candidates) if f != -1], key=lambda x: x[1])

            for string, fret in candidate_pairs:
                timeline = self.strings[string]
                # check for overlap
                if all(note.end_time <= n.start_time or note.start_time >= n.end_time for n in timeline):
                    timeline.append(note.to_final_note(string, fret))
                    assigned = True
                    break

            if not assigned:
                raise UnplayableError(f"Cannot assign note starting at {note.start_time}s")

        # sort each string's timeline by start time
        for timeline in self.strings.values():
            timeline.sort(key=lambda n: n.start_time)

        # flatten to a single optimal sequence
        self.optimal = sorted(itertools.chain.from_iterable(self.strings.values()), key=lambda n: n.start_time)
