from unittest import TestCase

from parameterized import parameterized

import pastebin


class Test(TestCase):
    @parameterized.expand(
        [
            [
                "note exists is public",
                "test1",
                "testauthor",
                200,
                '{"id": "test1", "note": "testdata", "author": "testauthor", "isPublic": true}',
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
            [
                "note exists is private read by author",
                "test1",
                "testauthor",
                200,
                '{"id": "test1", "note": "testdata", "author": "testauthor", "isPublic": true}',
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
            [
                "note exists is private read not by author",
                "test1",
                "otheruser",
                403,
                "",
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
            ],
            ["notes empty", "test1", "", 404, "", {}],
            [
                "note does not exist",
                "test2",
                "",
                404,
                "",
                {"test1": {"text": "testdata", "author": "testauthor"}},
            ],
        ]
    )
    def test_read_note(
        self,
        _,
        note_id,
        user,
        expected_status_code,
        expected_response_body,
        existing_notes,
    ):
        pastebin.notes = existing_notes
        response = pastebin.read_note(note_id, user)

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(expected_response_body, response.data.decode("utf-8"))

    @parameterized.expand(
        [
            [
                "notes empty",
                "test1",
                "testauthor",
                "notebody",
                True,
                201,
                {},
                {
                    "test1": {
                        "text": "notebody",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
            [
                "notes empty private note",
                "test1",
                "testauthor",
                "notebody",
                False,
                201,
                {},
                {
                    "test1": {
                        "text": "notebody",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
            ],
            [
                "note does not exist",
                "test2",
                "testauthor2",
                "notebody",
                False,
                201,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    },
                    "test2": {
                        "text": "notebody",
                        "author": "testauthor2",
                        "isPublic": False,
                    },
                },
            ],
            [
                "note exists",
                "test1",
                "",
                "notebody",
                True,
                409,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
        ]
    )
    def test_create_note(
        self,
        _,
        note_id,
        user,
        request_body,
        is_public,
        expected_status_code,
        existing_notes,
        expected_notes,
    ):
        pastebin.notes = existing_notes
        response = pastebin.create_note(note_id, user, request_body, is_public)

        self.assertEqual(expected_status_code, response.status_code)
        self.assertIn(note_id, pastebin.notes)
        self.assertEqual(expected_notes, pastebin.notes)

    @parameterized.expand(
        [
            [
                "note exists",
                "test1",
                "testauthor",
                "notebody",
                200,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                {
                    "test1": {
                        "text": "notebody",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
            [
                "note exists - not authorized",
                "test1",
                "otheruser",
                "notebody",
                403,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
            ["notes empty", "test1", "testauthor", "notebody", 404, {}, {}],
            [
                "note does not exist",
                "test2",
                "testauthor",
                "notebody",
                404,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
            ],
        ]
    )
    def test_update_note(
        self,
        _,
        note_id,
        user,
        request_body,
        expected_status_code,
        existing_notes,
        expected_notes,
    ):
        pastebin.notes = existing_notes
        response = pastebin.update_note(note_id, user, request_body)

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(expected_notes, pastebin.notes)

    @parameterized.expand(
        [
            [
                "note exists",
                "test1",
                "testauthor",
                200,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                False,
            ],
            [
                "note exists; wrong user",
                "test1",
                "otherauthor",
                403,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                True,
            ],
            ["notes empty", "test1", "", 404, {}, False],
            [
                "note does not exist",
                "test2",
                "",
                404,
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                False,
            ],
        ]
    )
    def test_delete_note(
        self, _, note_id, user, expected_status_code, existing_notes, should_note_exist
    ):
        pastebin.notes = existing_notes
        response = pastebin.delete_note(note_id, user)

        self.assertEqual(response.status_code, expected_status_code)
        if should_note_exist:
            # note should not have been deleted
            self.assertIn(note_id, pastebin.notes)
        else:
            # note should have been deleted
            self.assertNotIn(note_id, pastebin.notes)

    @parameterized.expand(
        [
            [
                "user is author public note",
                "testauthor",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                True,
            ],
            [
                "user is author private note",
                "testauthor",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
                True,
            ],
            [
                "user is not author public note",
                "otheruser",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                True,
            ],
            [
                "user is not author private note",
                "otheruser",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
                False,
            ],
        ]
    )
    def test_can_user_read(
        self, _, user, note_id, user_obj, note_obj, expected_response
    ):
        pastebin.users = user_obj
        pastebin.notes = note_obj

        response = pastebin.can_user_read(user, note_id)
        self.assertEqual(response, expected_response)

    @parameterized.expand(
        [
            [
                "user is author public note",
                "testauthor",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                True,
            ],
            [
                "user is author private note",
                "testauthor",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
                True,
            ],
            [
                "user is not author public note",
                "otheruser",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": True,
                    }
                },
                False,
            ],
            [
                "user is not author private note",
                "otheruser",
                "test1",
                {"testuser": "asdf"},
                {
                    "test1": {
                        "text": "testdata",
                        "author": "testauthor",
                        "isPublic": False,
                    }
                },
                False,
            ],
        ]
    )
    def test_can_user_modify(
        self, _, user, note_id, user_obj, note_obj, expected_response
    ):
        pastebin.users = user_obj
        pastebin.notes = note_obj

        response = pastebin.can_user_modify(user, note_id)
        self.assertEqual(response, expected_response)

    @parameterized.expand(
        [
            ["true", True],
            ["True", True],
            ["TrUe", True],
            ["TRUE", True],
            ["t", False],
            ["false", False],
        ]
    )
    def test_is_true(self, test_string, expected_bool):
        self.assertEqual(pastebin.is_true(test_string), expected_bool)
