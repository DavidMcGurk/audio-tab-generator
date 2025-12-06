from __future__ import annotations
import itertools
import numpy as np
from typing import Optional
from audio_tab_generator.models.note import NoteCandidate, UnplayableError

MAX_STRETCH = 4  # maximum allowed fret span


class Chord:
    """
    Chord model for computing playable and optimal string assignments
    for simultaneous notes in standard-tuned guitar. Note, here 'chord'
    refers to a cluster of 1 or more notes played with overlapping timing.
    """

    def __init__(self, notes: list[NoteCandidate]) -> None:
        if len(notes) > 6:
            raise NotImplementedError("Chords larger than 6 notes are not supported.")

        self.notes = notes
        self.playable_permutations: Optional[list[list[int]]] = None
        self.optimal: list[int] = []

    def find_playable_chords(self) -> None:
        """Generate and filter permutations to retain only playable chord shapes."""

        perms = self._find_valid_permutations([n.candidates for n in self.notes])
        playable: list[list[int]] = []

        for perm in perms:
            fretted = [f for f in perm if f > 0]
            if not fretted or max(fretted) - min(fretted) <= MAX_STRETCH:
                playable.append(perm)

        if not playable:
            raise UnplayableError("No playable fingering for chord.")

        self.playable_permutations = playable

    def find_optimal(self) -> None:
        """Select the permutation with minimal overall fret cost."""

        if self.playable_permutations is None:
            self.find_playable_chords()

        best_score = np.Inf
        best_perm: list[int] = []

        for perm in self.playable_permutations:  # type: ignore
            score = sum(f for f in perm if f != -1)
            if score < best_score:
                best_score = score
                best_perm = perm

        self.optimal = best_perm

    def _find_valid_permutations(self, candidates_per_note: list[list[int]]) -> list[list[int]]:
        """Generate all assignments ensuring no two notes share a string."""

        if not candidates_per_note:
            return []

        choice_groups = []
        for candidates in candidates_per_note:
            valid = [(i, f) for i, f in enumerate(candidates) if f >= 0]
            if not valid:
                return []
            choice_groups.append(valid)

        permutations = []
        max_len = max(len(c) for c in candidates_per_note)

        for combo in itertools.product(*choice_groups):
            strings = [idx for idx, _ in combo]
            if len(set(strings)) != len(strings):
                continue

            perm = [-1] * max_len
            for idx, fret in combo:
                perm[idx] = fret

            permutations.append(perm)

        return permutations
