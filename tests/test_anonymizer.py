import unittest

from app.services.anonymizer import anonymize


class AnonymizerTests(unittest.TestCase):
    def test_email_is_masked(self):
        result, count = anonymize("Напишите мне на ivan.petrov@example.com")
        self.assertNotIn("ivan.petrov@example.com", result)
        self.assertIn("[ДАННЫЕ УДАЛЕНЫ:email]", result)
        self.assertEqual(count, 1)

    def test_phone_is_masked(self):
        result, count = anonymize("Мой телефон +380 50 123 45 67")
        self.assertNotIn("123", result)
        self.assertEqual(count, 1)

    def test_case_number_is_masked(self):
        result, count = anonymize("Дело № 520/1356/24 открыто")
        self.assertNotIn("520/1356/24", result)
        self.assertEqual(count, 1)

    def test_card_number_is_masked(self):
        result, count = anonymize("Карта 4111 1111 1111 1111 заблокирована")
        self.assertNotIn("4111 1111 1111 1111", result)
        self.assertEqual(count, 1)

    def test_ip_is_masked(self):
        result, count = anonymize("Запрос пришёл с 192.168.10.24")
        self.assertNotIn("192.168.10.24", result)
        self.assertEqual(count, 1)

    def test_normal_text_is_untouched(self):
        text = "Хочу обжаловать постановление о штрафе в Украине"
        result, count = anonymize(text)
        self.assertEqual(result, text)
        self.assertEqual(count, 0)

    def test_empty_text(self):
        self.assertEqual(anonymize(""), ("", 0))


if __name__ == "__main__":
    unittest.main()
