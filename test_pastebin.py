from unittest import TestCase
from parameterized import parameterized
import pastebin
import mock


class Test(TestCase):
    @parameterized.expand([
        ["note exists", "test1", 200, '{"id": "test1", "note": "testdata", "author": "testauthor"}', {"test1": {"text": "testdata", "author": "testauthor"}}],
        ["notes empty", "test1", 404, '', {}],
        ["note does not exist", "test2", 404, '', {"test1": {"text": "testdata", "author": "testauthor"}}],
    ])
    def test_read_note(self, _, note_id, expected_status_code, expected_response_body, existing_notes):
        pastebin.notes = existing_notes
        response = pastebin.read_note(note_id)

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEquals(response.data.decode("utf-8"), expected_response_body)

    @parameterized.expand([
        ["notes empty", "test1", "notebody", 201, {}],
        ["note does not exist", "test2", "notebody", 201, {"test1": {"text": "testdata", "author": "testauthor"}}],
        ["note exists", "test1", "notebody", 409, {"test1": {"text": "testdata", "author": "testauthor"}}],
    ])
    def test_create_note(self, _, note_id, request_body, expected_status_code, existing_notes):
        pastebin.notes = existing_notes
        m = mock.MagicMock()
        m.values = request_body
        with mock.patch("pastebin.request", m):
            response = pastebin.create_note(note_id)

        self.assertEqual(response.status_code, expected_status_code)
        self.assertIn(note_id, pastebin.notes)

    @parameterized.expand([
        ["note exists", "test1", "notebody", 200, {"test1": {"text": "testdata", "author": "testauthor"}}],
        ["notes empty", "test1", "notebody", 404, {}],
        ["note does not exist", "test2", "notebody", 404, {"test1": {"text": "testdata", "author": "testauthor"}}],
    ])
    def test_update_note(self, _, note_id, request_body, expected_status_code, existing_notes):
        pastebin.notes = existing_notes
        m = mock.MagicMock()
        m.values = request_body
        with mock.patch("pastebin.request", m):
            response = pastebin.update_note(note_id)

        self.assertEqual(response.status_code, expected_status_code)

    @parameterized.expand([
        ["note exists", "test1", 200, {"test1": {"text": "testdata", "author": "testauthor"}}],
        ["notes empty", "test1", 404, {}],
        ["note does not exist", "test2", 404, {"test1": {"text": "testdata", "author": "testauthor"}}],
    ])
    def test_delete_note(self, _, note_id, expected_status_code, existing_notes):
        pastebin.notes = existing_notes
        response = pastebin.delete_note(note_id)

        self.assertEqual(response.status_code, expected_status_code)
        self.assertNotIn(note_id, pastebin.notes)
