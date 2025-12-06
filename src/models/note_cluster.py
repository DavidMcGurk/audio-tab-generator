from src.models.note import NoteCandidate, FinalNote, UnplayableError


class NoteCluster:
    """
    Handles a cluster of notes which overlap in time.
    """

    def __init__(self, notes: list[NoteCandidate], quantisation: int) -> None:
        """
        Initialises note cluster

        :param notes: List of note candidates with overlapping timing
        :type notes: list[NoteCandidate]
        :param quantisation: Timeframe in ms within which notes are considered concurrent
        :type quantisation: int
        """
        self.notes = sorted(notes, key=lambda n: n.start_time)
        self.quantisation = quantisation
        self.strings: dict[int, list[FinalNote]] = {i: [] for i in range(1, 7)}  # 1=high E, 6=low E
        self.grouped_final_notes: list[list[FinalNote]] = []

    def assign_notes(self) -> None:
        """
        Assign each note to a string such that:
        - Notes on the same string do not overlap in time
        - Movement on fretboard is minimised
        """
        self._quantise_notes()

        self.strings = {i: [] for i in range(1, 7)}

        # Group notes by quantised start time
        notes_by_start: dict[float, list[NoteCandidate]] = {}
        if not self.quantised_notes:
            return

        for note in self.quantised_notes:
            notes_by_start.setdefault(note.start_time, []).append(note)

        # Process each group in order of start time
        for start_time in sorted(notes_by_start.keys()):
            group_notes = notes_by_start[start_time]
            assigned_group: list[FinalNote] = []

            for note in group_notes:
                assigned = False
                candidate_pairs = sorted(
                    [(i + 1, f) for i, f in enumerate(note.candidates) if f != -1], key=lambda x: x[1]
                )

                for string, fret in candidate_pairs:
                    timeline = self.strings[string]
                    # check for overlap
                    if all(note.end_time <= n.start_time or note.start_time >= n.end_time for n in timeline):
                        final_note = note.to_final_note(string, fret)
                        timeline.append(final_note)
                        assigned_group.append(final_note)
                        assigned = True
                        break

                if not assigned:
                    raise UnplayableError(f"Cannot assign note starting at {note.start_time}s")

            assigned_group.sort(key=lambda n: n.string)
            self.grouped_final_notes.append(assigned_group)

    def _quantise_notes(self) -> None:
        """
        Quantises note start times so that any notes whose start times lie
        within `quantisation` milliseconds of each other are treated as concurrent.

        The earliest note in each quantisation window becomes the reference, and
        all other notes in the window take its start_time.
        """

        if not self.notes:
            self.quantised_notes = None
            return

        quantised = []
        current_group = [self.notes[0]]

        for note in self.notes[1:]:
            # If this note starts within the quantisation window from the
            # *earliest* note of the group, add it to the same group.
            if note.start_time - current_group[0].start_time <= self.quantisation / 1000:
                current_group.append(note)
            else:
                # Close previous group
                earliest_start = current_group[0].start_time
                for n in current_group:
                    n.start_time = earliest_start
                quantised.extend(current_group)

                # Begin new group
                current_group = [note]

        # Final group
        earliest_start = current_group[0].start_time
        for n in current_group:
            n.start_time = earliest_start
        quantised.extend(current_group)

        self.quantised_notes = quantised
