import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import case_analyzer, intent, legal_repository, research_mode, research_storage


class IntentTests(unittest.TestCase):
    def test_police_encounter_is_detected_in_russian_inflections(self):
        result = intent.analyze_intent("Я вызвал полицию после остановки")
        self.assertEqual(result.category, "police_encounter")

    def test_police_encounter_is_detected_in_english(self):
        result = intent.analyze_intent("I was stopped by police")
        self.assertEqual(result.category, "police_encounter")


class ValidationTests(unittest.TestCase):
    def test_case_analyzer_normalizes_supported_jurisdiction(self):
        result = case_analyzer.analyze_case("Нужна юридическая помощь", "de")
        self.assertEqual(result.jurisdiction, "DE")

    def test_case_analyzer_rejects_unknown_jurisdiction(self):
        with self.assertRaisesRegex(ValueError, "Unsupported jurisdiction"):
            case_analyzer.analyze_case("Нужна помощь", "XX")

    def test_unknown_research_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown research mode"):
            research_mode.get_policy("bogus")

    def test_case_mode_requires_explicit_confirmation(self):
        self.assertFalse(research_mode.should_download("case", user_confirmed=False))
        self.assertTrue(research_mode.should_download("case", user_confirmed=True))

    def test_auto_mode_requires_explicit_confirmation(self):
        self.assertFalse(research_mode.should_download("auto", user_confirmed=False))
        self.assertTrue(research_mode.should_download("auto", user_confirmed=True))

    def test_consultation_never_saves_even_if_confirmed(self):
        self.assertFalse(research_mode.should_download("consultation", user_confirmed=True))

    def test_case_id_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.object(research_storage, "CASE_DIR", Path(temporary_directory)):
                with self.assertRaises(ValueError):
                    research_storage.prepare_case("../outside")

    def test_unconfirmed_document_is_not_saved(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "source.txt"
            source.write_text("sample", encoding="utf-8")
            case_directory = directory / "cases"

            with patch.object(research_storage, "CASE_DIR", case_directory):
                result = research_storage.process_document(
                    str(source), mode="case", case_id="case-1", user_confirmed=False
                )

            self.assertFalse(result.saved)
            self.assertEqual(result.action, "online_only")
            self.assertFalse(case_directory.exists())


class LegalRepositoryTests(unittest.TestCase):
    def test_database_schema_is_initialized_and_sources_round_trip(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "nested" / "plda.db"
            with patch.object(legal_repository, "DB_PATH", database_path):
                self.assertEqual(legal_repository.count_sources(), 0)
                source_id = legal_repository.add_source(
                    title="Test law",
                    source_type="statute",
                    jurisdiction="DE",
                    text="Article text",
                    article="5",
                    verified=1,
                )
                stored = legal_repository.get_source(source_id)
                self.assertEqual(stored["title"], "Test law")
                self.assertEqual(legal_repository.count_sources(), 1)
                results = legal_repository.search_sources("Article", jurisdiction="DE")
                self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
