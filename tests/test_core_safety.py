import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import legal_repository
from app.core.case_analyzer import analyze_case
from app.core.intent import analyze_intent
from app.core.research_mode import get_policy, should_download
from app.core.research_storage import process_document, prepare_case


class ConfigurationValidationTests(unittest.TestCase):
    def test_supported_jurisdiction_is_normalized(self):
        self.assertEqual(analyze_case("Нужна правовая помощь", " de ").jurisdiction, "DE")

    def test_unknown_jurisdiction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported jurisdiction"):
            analyze_case("Нужна правовая помощь", "XX")

    def test_unknown_research_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown research mode"):
            get_policy("bogus")


class IntentTests(unittest.TestCase):
    def test_police_inflections_are_detected(self):
        self.assertEqual(analyze_intent("Вызвал полицию").category, "police_encounter")
        self.assertEqual(analyze_intent("Меня остановили сотрудники полиции").category, "police_encounter")

    def test_english_police_query_is_detected(self):
        self.assertEqual(analyze_intent("I was stopped by police").category, "police_encounter")


class StoragePolicyTests(unittest.TestCase):
    def test_case_mode_still_requires_explicit_confirmation(self):
        self.assertFalse(should_download("case"))
        self.assertTrue(should_download("case", user_confirmed=True))

    def test_auto_mode_saves_only_after_confirmation(self):
        self.assertFalse(should_download("auto"))
        self.assertTrue(should_download("auto", user_confirmed=True))

    def test_consultation_mode_never_saves(self):
        self.assertFalse(should_download("consultation", user_confirmed=True))

    def test_case_id_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("app.core.research_storage.CASE_DIR", Path(directory)):
                with self.assertRaises(ValueError):
                    prepare_case("../outside")
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_documents_require_confirmation_and_case_id(self):
        result = process_document("missing.txt", mode="case", case_id="case-1")
        self.assertFalse(result.saved)
        self.assertEqual(result.action, "online_only")

        with self.assertRaisesRegex(ValueError, "case_id is required"):
            process_document("missing.txt", mode="case", user_confirmed=True)

    def test_confirmed_case_document_is_saved_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "evidence.txt"
            source.write_text("evidence", encoding="utf-8")

            with patch("app.core.research_storage.CASE_DIR", root / "cases"):
                first = process_document(
                    str(source), mode="case", case_id="case-1", user_confirmed=True
                )
                second = process_document(
                    str(source), mode="case", case_id="case-1", user_confirmed=True
                )

            self.assertTrue(first.saved)
            self.assertEqual(first.action, "saved_and_ingested")
            self.assertTrue(Path(first.path).is_file())
            self.assertEqual(second.action, "already_saved")


class LegalRepositoryTests(unittest.TestCase):
    def test_database_schema_initializes_and_crud_search_work(self):
        with tempfile.TemporaryDirectory() as directory:
            test_database = Path(directory) / "plda.db"
            with patch.object(legal_repository, "DB_PATH", test_database):
                self.assertEqual(legal_repository.count_sources(), 0)
                source_id = legal_repository.add_source(
                    title="European Convention on Human Rights",
                    source_type="treaty",
                    jurisdiction="international",
                    country_code="DE",
                    article="Article 5",
                    text="Everyone has the right to liberty and security.",
                    source_url="https://example.org/source",
                    verified=1,
                )

                self.assertGreater(source_id, 0)
                self.assertEqual(legal_repository.count_sources(), 1)
                row = legal_repository.get_source(source_id)
                self.assertEqual(row["country_code"], "DE")
                self.assertEqual(row["verified"], 1)
                found = legal_repository.search_sources(
                    "liberty", jurisdiction="international", country_code="DE"
                )
                self.assertEqual([item["id"] for item in found], [source_id])


if __name__ == "__main__":
    unittest.main()
