import os
import time
import tempfile
from services.storage_cleanup import cleanup_old_debug_files


def test_storage_cleanup_deletes_old_files():
    """Verify that cleanup_old_debug_files removes debug pngs/htmls older than N days and leaves new files intact."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an old debug screenshot (10 days old)
        old_file = os.path.join(temp_dir, "old_debug_fail.png")
        with open(old_file, "w") as f:
            f.write("fake image")
        old_time = time.time() - (10 * 86400)
        os.utime(old_file, (old_time, old_time))

        # Create a fresh debug screenshot (1 day old)
        new_file = os.path.join(temp_dir, "new_debug_fail.png")
        with open(new_file, "w") as f:
            f.write("fake image")

        res = cleanup_old_debug_files(base_dir=temp_dir, max_age_days=7)

        assert res["status"] == "SUCCESS"
        assert not os.path.exists(old_file)
        assert os.path.exists(new_file)
