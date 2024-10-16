import unittest
from flask_testing import TestCase
from pastebin import app, users, notes
import json


class TestPastebin(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        return app

    def setUp(self):
        self.client = self.app.test_client()
        users.clear()
        notes.clear()

    def register_and_login(self, user_id="testuser", password="testpass"):
        self.client.post(
            "/api/register", json={"user_id": user_id, "password": password}
        )
        login_response = self.client.post(
            "/api/login", json={"user_id": user_id, "password": password}
        )
        return login_response.json["token"]

    def test_register_user(self):
        response = self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("api_key", response.json)

    def test_register_duplicate_user(self):
        self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass"}
        )
        response = self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass2"}
        )
        self.assertEqual(response.status_code, 409)

    def test_login_user(self):
        self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass"}
        )
        response = self.client.post(
            "/api/login", json={"user_id": "testuser", "password": "testpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_login_invalid_credentials(self):
        self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass"}
        )
        response = self.client.post(
            "/api/login", json={"user_id": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_note(self):
        token = self.register_and_login()
        response = self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"id": "testnote"})

    def test_create_duplicate_note(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.post(
            "/api/notes",
            json={
                "id": "testnote",
                "text": "This is another test note",
                "isPublic": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 409)

    def test_read_note(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], "testnote")
        self.assertEqual(response.json["text"], "This is a test note")
        self.assertEqual(response.json["isPublic"], True)

    def test_update_note(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.put(
            "/api/notes/testnote",
            json={"text": "This is an updated test note", "isPublic": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)

        # Verify the update
        response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.json["text"], "This is an updated test note")
        self.assertEqual(response.json["isPublic"], False)

    def test_delete_note(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.delete(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)

        # Verify the deletion
        response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 404)

    def test_list_notes(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "note1", "text": "This is note 1", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.post(
            "/api/notes",
            json={"id": "note2", "text": "This is note 2", "isPublic": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/api/notes", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertIn("note1", [note["id"] for note in response.json])
        self.assertIn("note2", [note["id"] for note in response.json])

    def test_unauthorized_access(self):
        token = self.register_and_login()
        self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to access the note without authentication
        response = self.client.get("/api/notes/testnote")
        self.assertEqual(response.status_code, 401)

        # Register another user and try to access the private note
        other_token = self.register_and_login("otheruser", "otherpass")
        response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {other_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_input_sanitization(self):
        token = self.register_and_login()
        response = self.client.post(
            "/api/notes",
            json={
                "id": "testnote",
                "text": '<script>alert("XSS");</script>',
                "isPublic": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertNotIn("<script>", response.json["text"])


if __name__ == "__main__":
    unittest.main()
