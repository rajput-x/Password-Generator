import string
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .password_utils import (
	PASSWORD_PRESETS,
	estimate_password_strength,
	generate_passphrase,
	generate_password,
	selected_character_pool_size,
)


class PasswordUtilsTests(TestCase):
	def test_generate_password_includes_selected_sets(self):
		password = generate_password(
			length=24,
			include_uppercase=True,
			include_lowercase=True,
			include_numbers=True,
			include_symbols=True,
			exclude_ambiguous=False,
		)

		self.assertIsNotNone(password)
		self.assertEqual(len(password), 24)
		self.assertTrue(any(ch in string.ascii_uppercase for ch in password))
		self.assertTrue(any(ch in string.ascii_lowercase for ch in password))
		self.assertTrue(any(ch in string.digits for ch in password))
		self.assertTrue(any(ch in string.punctuation for ch in password))

	def test_generate_password_returns_none_without_groups(self):
		password = generate_password(
			length=12,
			include_uppercase=False,
			include_lowercase=False,
			include_numbers=False,
			include_symbols=False,
		)
		self.assertIsNone(password)

	def test_generate_passphrase(self):
		phrase = generate_passphrase(word_count=5, separator="-", append_number=True, append_symbol=True)
		self.assertIsNotNone(phrase)
		self.assertIn("-", phrase)

	def test_real_world_presets_available(self):
		self.assertIn("basic_web", PASSWORD_PRESETS)
		self.assertIn("high_security", PASSWORD_PRESETS)
		self.assertIn("legacy_compatible", PASSWORD_PRESETS)
		self.assertIn("description", PASSWORD_PRESETS["basic_web"])

	def test_strength_penalizes_common_patterns(self):
		pool_size = selected_character_pool_size(True, True, True, True)
		weak = estimate_password_strength("Password1234", pool_size)
		strong = estimate_password_strength("V9!mQ2#xT7@bN4&k", pool_size)
		self.assertLess(weak["entropy_bits"], strong["entropy_bits"])
		self.assertTrue(len(weak.get("findings", [])) >= 1)


class IndexViewTests(TestCase):
	def test_get_index_page(self):
		response = self.client.get(reverse("index"))
		self.assertEqual(response.status_code, 200)

	def test_post_generates_password_and_strength(self):
		response = self.client.post(
			reverse("index"),
			{
				"action": "generate",
				"mode": "password",
				"length": 20,
				"uppercase": "on",
				"lowercase": "on",
				"numbers": "on",
				"symbols": "on",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertIn("password", response.context)
		self.assertIn("strength", response.context)
		self.assertIsNotNone(response.context["password"])
		self.assertIsNotNone(response.context["strength"])

	def test_post_with_invalid_length_shows_error(self):
		response = self.client.post(
			reverse("index"),
			{
				"action": "generate",
				"mode": "password",
				"length": 4,
				"uppercase": "on",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Choose a password length between 8 and 64.")

	def test_apply_passphrase_preset(self):
		response = self.client.post(
			reverse("index"),
			{
				"action": "apply_preset",
				"preset": "passphrase",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["mode"], "passphrase")

	def test_generate_variations(self):
		response = self.client.post(
			reverse("index"),
			{
				"action": "variations",
				"mode": "password",
				"length": 18,
				"uppercase": "on",
				"lowercase": "on",
				"numbers": "on",
				"symbols": "on",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.context["variations"]), 3)

	@patch("generator.views.check_password_breach_count", return_value=0)
	def test_breach_check_message(self, _mock_breach):
		response = self.client.post(
			reverse("index"),
			{
				"action": "generate",
				"mode": "password",
				"length": 18,
				"uppercase": "on",
				"lowercase": "on",
				"numbers": "on",
				"symbols": "on",
				"check_breach": "on",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No breach record found")

	@patch("generator.views.check_password_breach_count", return_value=12)
	def test_exposed_password_shows_recommendation(self, _mock_breach):
		response = self.client.post(
			reverse("index"),
			{
				"action": "generate",
				"mode": "password",
				"length": 12,
				"uppercase": "on",
				"lowercase": "on",
				"numbers": "on",
				"symbols": "on",
				"check_breach": "on",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Please regenerate immediately")
