import os
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from conversations.models import Conversation, TranscriptSegment

User = get_user_model()


class InsightsCoachSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@example.com", "testpass123")
        self.client = Client()
        self.client.force_login(self.user)

    @patch("conversations.views.coach_search.search")
    def test_post_search_shows_results(self, mock_search):
        mock_search.return_value = (
            [{"text": "Practice pausing instead of filler words.", "score": 0.91}],
            None,
        )
        response = self.client.post("/insights/", {"query": "filler words"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Practice pausing")
        self.assertContains(response, "0.91")
        mock_search.assert_called_once_with("filler words")

    @patch("conversations.views.coach_search.search")
    def test_post_search_shows_no_match_message(self, mock_search):
        mock_search.return_value = ([], "No passages matched strongly enough")
        response = self.client.post("/insights/", {"query": "zzzz"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No passages matched strongly enough")

    def test_post_empty_query_shows_form_error(self):
        response = self.client.post("/insights/", {"query": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a search query")


class ApiActionItemsErrorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("bob", "bob@example.com", "testpass123")
        self.conv = Conversation.objects.create(
            user=self.user,
            title="Test",
            recorded_at=timezone.now(),
        )
        TranscriptSegment.objects.create(
            conversation=self.conv,
            text="We should follow up on the budget tomorrow.",
            segment_order=1,
        )
        self.client = Client()
        self.client.force_login(self.user)

    @patch.dict("os.environ", {"HF_TOKEN": "fake-token"}, clear=False)
    @patch("conversations.views.requests.post")
    def test_hf_error_json_returns_detail(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 503
        mock_resp.text = ""
        mock_resp.reason = "Service Unavailable"
        mock_resp.json.return_value = {"error": "Model is currently loading"}
        mock_post.return_value = mock_resp

        response = self.client.post(
            "/api/action-items/",
            data='{"conversation_id": %d}' % self.conv.pk,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("loading", data["detail"].lower())

    def _env_without_hf_tokens():
        def _getter(key, default=None):
            if key in ("HF_TOKEN", "HUGGINGFACE_TOKEN"):
                return None
            return os.environ.get(key, default)

        return _getter

    @patch("conversations.views.os.environ.get", side_effect=_env_without_hf_tokens())
    def test_missing_token_returns_503(self, _mock):
        response = self.client.post(
            "/api/action-items/",
            data='{"conversation_id": %d}' % self.conv.pk,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("HF_TOKEN", response.json().get("error", ""))
