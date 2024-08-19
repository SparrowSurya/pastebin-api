import unittest
import time

from api import database, crud, schemas


# NOTE - others are not included since they are being tested indirectly
class TestTask(unittest.TestCase):

    def setUp(self):
        self.db = database.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_deletes_expired_paste(self):
        paste1 = schemas.Paste(
            files=[
                schemas.File(name="name1.txt", text="123", kind="text"),
                schemas.File(name="name2.txt", text="246", kind="text"),
            ],
            expiry=1,
        )
        paste2 = schemas.Paste(
            files=[
                schemas.File(name="name3.txt", text="987", kind="text"),
                schemas.File(name="name4.txt", text="321", kind="text"),
            ],
            expiry=3600,
        )

        pasteinfo1 = crud.create_db_paste(self.db, paste1)
        pasteinfo2 = crud.create_db_paste(self.db, paste2)

        self.assertIsNotNone(crud.get_db_paste_by_key(self.db, pasteinfo1.key))
        self.assertIsNotNone(crud.get_db_paste_by_key(self.db, pasteinfo2.key))

        time.sleep(1) # wait for paste1 to expire

        crud.delete_expired_pastes(self.db)

        self.assertIsNone(crud.get_db_paste_by_key(self.db, pasteinfo1.key))
        self.assertIsNotNone(crud.get_db_paste_by_key(self.db, pasteinfo2.key))