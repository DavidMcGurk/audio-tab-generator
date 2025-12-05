import numpy as np
from audio_tab_generator.models.note import NoteCandidate
import itertools
from typing import Optional

MAX_STRETCH = 4  # largest gap between frets playable in a single chord


class UnplayableError(Exception):
    pass


class Chord:
    def __init__(self, notes: list[NoteCandidate]) -> None:
        self.notes = notes  # in 'chord'
        self.playable_permutations: Optional[list] = None  # ways of playing the chord which are actually feasible
        self.optimal: list = []

        if len(notes) > 6:
            raise NotImplementedError(
                "The program cannot currently deal with 'chords' which are more than 6 notes at " "one time!"
            )

    def find_playable_chords(self) -> None:
        perms = self._find_valid_permutations([note.candidates for note in self.notes])
        playable_permutations = []
        for idx, perm in enumerate(perms):
            low, high = np.Inf, -1
            for note in perm:
                if note <= 0:
                    continue  # note either not played or can always be played on open string

                if note > high:
                    high = note
                if note < low:
                    low = note

            if low == np.Inf or high - low <= MAX_STRETCH:
                playable_permutations.append(perm)

        if not playable_permutations:
            raise UnplayableError("Chord cannot be played!")
        self.playable_permutations = playable_permutations

    def find_optimal(self) -> None:
        if self.playable_permutations is None:
            self.find_playable_chords()
        best_score = np.Inf

        for perm in self.playable_permutations:  # type: ignore[union-attr]
            total = sum(note for note in perm if note != -1)
            if total < best_score:
                optimal = perm
                best_score = total

        self.optimal = optimal

    def _find_valid_permutations(self, note_possibilities: list) -> list:
        if not note_possibilities:
            return []

        all_choices: list[list[tuple[int, int]]] = []
        max_len = max(len(token) for token in note_possibilities)

        for note in note_possibilities:
            choices = [(i, v) for i, v in enumerate(note) if v >= 0]
            if not choices:
                return []
            all_choices.append(choices)

        permutations = []

        for selection in itertools.product(*all_choices):
            indices = [tpl[0] for tpl in selection]
            if len(set(indices)) != len(indices):
                continue

            perm = [-1] * max_len
            for idx, val in selection:
                perm[idx] = val
            permutations.append(perm)

        return permutations
