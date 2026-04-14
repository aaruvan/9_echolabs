import os
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
    @patch("conversations.views.InferenceClient")
    def test_hf_error_json_returns_detail(self, mock_client_cls):
        from huggingface_hub.errors import HfHubHTTPError

        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.json.return_value = {"error": "Model is currently loading"}
        err = HfHubHTTPError("inference error", response=mock_resp)

        mock_instance = MagicMock()
        mock_instance.chat_completion.side_effect = err
        mock_client_cls.return_value = mock_instance

        response = self.client.post(
            "/api/action-items/",
            data='{"conversation_id": %d}' % self.conv.pk,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("loading", data["detail"].lower())

    @patch.dict("os.environ", {"HF_TOKEN": "fake-token"}, clear=False)
    @patch("conversations.views.InferenceClient")
    def test_post_returns_action_items_on_success(self, mock_client_cls):
        mock_msg = MagicMock()
        mock_msg.content = "- Follow up on budget\n- Schedule review"
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_out = MagicMock()
        mock_out.choices = [mock_choice]

        mock_instance = MagicMock()
        mock_instance.chat_completion.return_value = mock_out
        mock_client_cls.return_value = mock_instance

        response = self.client.post(
            "/api/action-items/",
            data='{"conversation_id": %d}' % self.conv.pk,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Follow up on budget", data.get("action_items", ""))

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


class TranscribeUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("carol", "carol@example.com", "testpass123")
        self.client = Client()
        self.client.force_login(self.user)

    def test_get_shows_form(self):
        response = self.client.get("/conversations/transcribe/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transcribe")

    @patch("conversations.views.transcribe.transcribe_audio_file")
    def test_post_creates_conversation_and_redirects(self, mock_tr):
        mock_tr.return_value = (
            [("Speaker A", "Hello world."), ("Speaker B", "Second line.")],
            42.7,
        )
        audio = SimpleUploadedFile(
            "clip.mp3",
            b"not-real-mp3",
            content_type="audio/mpeg",
        )
        response = self.client.post(
            "/conversations/transcribe/",
            {"title": "Practice session", "audio": audio},
        )
        self.assertEqual(response.status_code, 302)
        conv = Conversation.objects.get(user=self.user, title="Practice session")
        self.assertEqual(conv.segments.count(), 2)
        segs = list(conv.segments.order_by("segment_order"))
        self.assertEqual(segs[0].text, "Hello world.")
        self.assertEqual(segs[0].speaker_label, "Speaker A")
        self.assertEqual(segs[1].text, "Second line.")
        self.assertEqual(segs[1].speaker_label, "Speaker B")
        self.assertEqual(conv.duration_seconds, 43)

    @patch("conversations.views.transcribe.transcribe_audio_file")
    def test_post_value_error_shows_message(self, mock_tr):
        mock_tr.side_effect = ValueError("No speech detected in the audio.")
        audio = SimpleUploadedFile("x.wav", BytesIO(b"x").read(), content_type="audio/wav")
        response = self.client.post(
            "/conversations/transcribe/",
            {"title": "Empty", "audio": audio},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No speech detected")

    def test_wrong_extension_rejected(self):
        audio = SimpleUploadedFile("x.txt", b"x", content_type="text/plain")
        response = self.client.post(
            "/conversations/transcribe/",
            {"title": "Bad", "audio": audio},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported format")
