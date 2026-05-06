import os
import tempfile
import unittest

from bot.activity_store import ActivityStore


class ActivityStoreTests(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.store = ActivityStore(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_append_and_list_activity(self):
        self.store.append(
            title="Validation passed",
            payload="BTCUSDT | BUY | MARKET | qty 0.01",
            details=None,
        )
        self.store.append(
            title="Execution failed",
            payload="BTCUSDT | BUY | MARKET | qty 0.01",
            details="Timestamp for this request was ahead of the server's time.",
        )

        rows = self.store.list_recent(limit=8)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["title"], "Execution failed")
        self.assertIn("Timestamp", rows[0]["details"])
        self.assertEqual(rows[1]["title"], "Validation passed")

    def test_keeps_only_most_recent_limit(self):
        for index in range(10):
            self.store.append(
                title=f"Activity {index}",
                payload=f"payload {index}",
                details=None,
            )

        rows = self.store.list_recent(limit=8)

        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["title"], "Activity 9")
        self.assertEqual(rows[-1]["title"], "Activity 2")


if __name__ == "__main__":
    unittest.main()
