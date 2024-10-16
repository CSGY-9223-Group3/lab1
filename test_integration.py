import unittest
from flask_testing import TestCase
from pastebin import app, users, notes
import json


class TestPastebinIntegration(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        return app

    def setUp(self):
        self.client = self.app.test_client()
        users.clear()
        notes.clear()

    def test_full_user_journey(self):
        # 1. Register a new user
        register_response = self.client.post(
            "/api/register", json={"user_id": "testuser", "password": "testpass"}
        )
        self.assertEqual(register_response.status_code, 201)
        self.assertIn("api_key", register_response.json)

        # 2. Login with the new user
        login_response = self.client.post(
            "/api/login", json={"user_id": "testuser", "password": "testpass"}
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.json)
        token = login_response.json["token"]

        # 3. Create a new note
        create_note_response = self.client.post(
            "/api/notes",
            json={"id": "testnote", "text": "This is a test note", "isPublic": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(create_note_response.status_code, 201)

        # 4. Read the created note
        read_note_response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(read_note_response.status_code, 200)
        self.assertEqual(read_note_response.json["text"], "This is a test note")

        # 5. Update the note
        update_note_response = self.client.put(
            "/api/notes/testnote",
            json={"text": "This is an updated test note", "isPublic": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(update_note_response.status_code, 200)

        # 6. Verify the update
        read_updated_note_response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(read_updated_note_response.status_code, 200)
        self.assertEqual(
            read_updated_note_response.json["text"], "This is an updated test note"
        )
        self.assertEqual(read_updated_note_response.json["isPublic"], False)

        # 7. List all notes
        list_notes_response = self.client.get(
            "/api/notes", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(list_notes_response.status_code, 200)
        self.assertEqual(len(list_notes_response.json), 1)

        # 8. Delete the note
        delete_note_response = self.client.delete(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(delete_note_response.status_code, 200)

        # 9. Verify the deletion
        read_deleted_note_response = self.client.get(
            "/api/notes/testnote", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(read_deleted_note_response.status_code, 404)

    def test_multiple_users_interaction(self):
        # Register and login two users
        user1_token = self.register_and_login("user1", "pass1")
        user2_token = self.register_and_login("user2", "pass2")

        # User 1 creates a public note
        self.client.post(
            "/api/notes",
            json={
                "id": "publicnote",
                "text": "This is a public note",
                "isPublic": True,
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # User 1 creates a private note
        self.client.post(
            "/api/notes",
            json={
                "id": "privatenote",
                "text": "This is a private note",
                "isPublic": False,
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # User 2 tries to read both notes
        public_note_response = self.client.get(
            "/api/notes/publicnote", headers={"Authorization": f"Bearer {user2_token}"}
        )
        self.assertEqual(public_note_response.status_code, 200)

        private_note_response = self.client.get(
            "/api/notes/privatenote", headers={"Authorization": f"Bearer {user2_token}"}
        )
        self.assertEqual(private_note_response.status_code, 403)

        # User 2 tries to update User 1's public note
        update_response = self.client.put(
            "/api/notes/publicnote",
            json={"text": "Attempted update by User 2", "isPublic": True},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        self.assertEqual(update_response.status_code, 403)

    def register_and_login(self, username, password):
        self.client.post(
            "/api/register", json={"user_id": username, "password": password}
        )
        login_response = self.client.post(
            "/api/login", json={"user_id": username, "password": password}
        )
        return login_response.json["token"]


if __name__ == "__main__":
    unittest.main()
