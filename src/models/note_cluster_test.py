from src.models.note import NoteCandidate, FinalNote

from .note_cluster import NoteCluster


class TestNoteCluster:
    def setup_method(self) -> None:
        self.test_input_list = [[0, -1, -1, -1, -1, -1], [19, 14, 9, 4, 0, -1], [24, 19, 14, 9, 5, 0]]
        test_note1 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[0])
        test_note2 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[1])
        test_note3 = NoteCandidate(start_time=0.0, end_time=0.1, candidates=self.test_input_list[2])

        self.cluster = NoteCluster(notes=[test_note1, test_note2, test_note3])

    def test_assign_notes(self) -> None:
        self.cluster.assign_notes()
        assert self.cluster.optimal == [
            FinalNote(start_time=0.0, end_time=0.1, string=1, fret=0),
            FinalNote(start_time=0.0, end_time=0.1, string=5, fret=0),
            FinalNote(start_time=0.0, end_time=0.1, string=6, fret=0),
        ]
