from audio_tab_generator.models.note import NoteCandidate

from .chord import Chord


class TestChord:
    def setup_method(self) -> None:
        self.test_input_list = [[0, -1, -1, -1, -1, -1], [19, 14, 9, 4, 0, -1], [24, 19, 14, 9, 5, 0]]
        test_note1 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[0])
        test_note2 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[1])
        test_note3 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[2])

        self.chord = Chord(notes=[test_note1, test_note2, test_note3])

    def test_find_possible_permutations(self) -> None:
        expected_permutations = [
            [0, 19, 9, -1, -1, -1],
            [0, 19, -1, 4, -1, -1],
            [0, 19, -1, -1, 0, -1],
            [0, 14, 14, -1, -1, -1],
            [0, 14, -1, 9, -1, -1],
            [0, 14, -1, -1, 5, -1],
            [0, 14, -1, -1, -1, 0],
            [0, -1, 14, 4, -1, -1],
            [0, -1, 14, -1, 0, -1],
            [0, -1, 9, 9, -1, -1],
            [0, -1, 9, -1, 5, -1],
            [0, -1, 9, -1, -1, 0],
            [0, -1, -1, 9, 0, -1],
            [0, -1, -1, 4, -1, 0],
            [0, -1, -1, 4, 5, -1],
            [0, -1, -1, -1, 0, 0],
        ]
        assert sorted(self.chord._find_valid_permutations(self.test_input_list)) == sorted(expected_permutations)

    def test_find_playable_chords(self) -> None:
        playable_chords = [
            [0, 19, -1, -1, 0, -1],
            [0, 14, -1, -1, -1, 0],
            [0, 14, 14, -1, -1, -1],
            [0, -1, 14, -1, 0, -1],
            [0, -1, 9, 9, -1, -1],
            [0, -1, 9, -1, 5, -1],
            [0, -1, 9, -1, -1, 0],
            [0, -1, -1, 9, 0, -1],
            [0, -1, -1, 4, -1, 0],
            [0, -1, -1, 4, 5, -1],
            [0, -1, -1, -1, 0, 0],
        ]
        self.chord.find_playable_chords()
        assert sorted(self.chord.playable_permutations) == sorted(playable_chords)  # type: ignore[arg-type]

    def test_(self):
        self.chord.find_playable_chords()

    def test_find_best_chord(self) -> None:
        self.chord.find_optimal()
        assert self.chord.optimal == [0, -1, -1, -1, 0, 0]
