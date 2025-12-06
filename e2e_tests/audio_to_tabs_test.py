from pathlib import Path
import subprocess


class TestAudioToTabs:
    """End to end tests for run.py"""

    def setup_method(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]

        self.input_dir = self.project_root / "test_audio"
        self.output_dir = self.project_root / "e2e_tests" / "test_output"
        self.expected_outputs_dir = self.project_root / "e2e_tests" / "expected_outputs"

        # Ensure clean output dir
        self.output_dir.mkdir(exist_ok=True)
        for f in self.output_dir.glob("*"):
            f.unlink()

    def test_open_strings(self) -> None:
        self._run_generation(input_file="open_strings.mp3", onset_threshold=0.7)

    def test_hammer_ons(self) -> None:
        self._run_generation(input_file="hammer_ons.m4a", onset_threshold=0.4)

    def _run_generation(self, input_file: str, onset_threshold: float) -> None:
        # Run CLI
        result = subprocess.run(
            [
                "poetry",
                "run",
                "python",
                "run.py",
                str(self.input_dir / input_file),
                "-o",
                str(self.output_dir),
                "--onset-threshold",
                onset_threshold,  # type: ignore[list-item]
            ],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

        # Ensure output files generated
        generated_tabs = list(self.output_dir.glob("*.txt"))
        assert generated_tabs, "No tab files were generated"

        generated_tab_path = generated_tabs[0]
        generated_text = generated_tab_path.read_text()

        # Assert expected output exists
        expected_file = self.expected_outputs_dir / generated_tab_path.name
        assert expected_file.exists(), f"Expected file missing: {expected_file}"

        expected_text = expected_file.read_text()

        # Assert text matches
        assert generated_text == expected_text, (
            "Generated tab does not match expected output.\n"
            f"Generated: {generated_tab_path}\n"
            f"Expected:  {expected_file}"
        )
