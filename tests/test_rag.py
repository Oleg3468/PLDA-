import os
import tempfile
import unittest
from pathlib import Path


class RagTests(unittest.TestCase):
    """Тесты поиска по локальной базе источников (RAG)."""

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "test.db"
        os.environ["PLDA_DB_PATH"] = str(self.database_path)

    def tearDown(self):
        os.environ.pop("PLDA_DB_PATH", None)
        self.temporary_directory.cleanup()

    def _seeded_search(self, query, **kwargs):
        from app.core import rag
        from database.seed_ukraine import run_seed

        run_seed()
        return rag.search_sources(query, **kwargs)

    def test_seed_inserts_sources(self):
        from database.seed_ukraine import run_seed

        result = run_seed()
        self.assertGreaterEqual(result["inserted"], 20)
        again = run_seed()
        self.assertEqual(again["inserted"], 0)
        self.assertEqual(again["skipped"], result["inserted"])

    def test_appeal_query_finds_civil_procedure_code(self):
        results = self._seeded_search("как обжаловать решение суда апелляция", limit=5)
        self.assertTrue(results)
        titles = " ".join(source["title"] for source in results)
        self.assertIn("Цивільний процесуальний кодекс", titles)

    def test_fine_query_finds_admin_offences_code(self):
        results = self._seeded_search("штраф протокол обжалование постановления", limit=5)
        titles = " ".join(source["title"] for source in results)
        self.assertIn("адміністративні правопорушення", titles)

    def test_police_query_finds_criminal_procedure_code(self):
        results = self._seeded_search("задержание полиция подозрение адвокат", limit=5)
        titles = " ".join(source["title"] for source in results)
        self.assertIn("Кримінальний процесуальний кодекс", titles)

    def test_jurisdiction_filter_excludes_other_countries(self):
        results = self._seeded_search("договор наследство", jurisdiction="UA", limit=20)
        self.assertTrue(results)
        for source in results:
            self.assertIn(source["jurisdiction"], {"UA", "international"})

    def test_verified_sources_get_priority(self):
        results = self._seeded_search("исполнительное производство арест имущества", limit=8)
        self.assertTrue(results)
        self.assertEqual(results[0]["verified"], 1)
        self.assertEqual(results[0]["checked_at"], "2026-10-01")

    def test_no_match_returns_empty_without_fallback(self):
        results = self._seeded_search("zzzz xxxx yyyy")
        self.assertEqual(results, [])

    def test_fallback_returns_starting_set(self):
        results = self._seeded_search("zzzz xxxx yyyy", include_fallback=True, limit=5)
        self.assertEqual(len(results), 5)

    def test_stats_counts_sources(self):
        stats = self._seeded_search("апелляция")  # прогрев базы через сид
        from app.core import rag

        stats = rag.get_stats()
        self.assertGreaterEqual(stats["total"], 20)
        self.assertGreaterEqual(stats["verified"], 9)
        jurisdictions = {row["jurisdiction"] for row in stats["by_jurisdiction"]}
        self.assertIn("UA", jurisdictions)


if __name__ == "__main__":
    unittest.main()
