"""
Storage Cleanup Utility — automatically removes stale debug screenshots, HTML dumps,
and temporary browser profile directories older than N days while preserving all database quotes.
"""
import os
import shutil
import time
import glob


def cleanup_old_debug_files(base_dir: str = None, max_age_days: int = 7) -> dict:
    """
    Deletes temporary debug screenshots (*.png), HTML dumps (*.html), and temporary
    browser profiles older than max_age_days.

    Returns:
        dict summarizing deleted file counts and reclaimed disk space.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cutoff_timestamp = time.time() - (max_age_days * 86400)
    deleted_files_count = 0
    deleted_dirs_count = 0
    freed_bytes = 0

    print(f"[STORAGE CLEANUP] Scanning '{base_dir}' for debug artifacts older than {max_age_days} days...")

    # Search in base_dir (backend/) and parent directory
    search_dirs = [base_dir, os.path.dirname(base_dir)]

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue

        # 1. Clean up stale debug files (*.png, *.html)
        for ext in ["*.png", "*.html"]:
            for file_path in glob.glob(os.path.join(search_dir, ext)):
                filename = os.path.basename(file_path).lower()
                # Protect web essential files if any
                if filename in ["index.html", "favicon.ico"]:
                    continue

                try:
                    mtime = os.path.getmtime(file_path)
                    if mtime < cutoff_timestamp:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files_count += 1
                        freed_bytes += file_size
                except Exception as e:
                    print(f"[STORAGE CLEANUP] Warning: Could not remove file {file_path}: {e}")

        # 2. Clean up temporary Chrome profile directories (e.g. chrome_profile_cma_tmp_*)
        try:
            for item in os.listdir(search_dir):
                item_path = os.path.join(search_dir, item)
                if os.path.isdir(item_path):
                    # Only target temporary browser profiles
                    if (item.startswith("chrome_profile_") and "_tmp_" in item) or item.startswith("chrome_profile_ai_experiment_"):
                        try:
                            mtime = os.path.getmtime(item_path)
                            if mtime < cutoff_timestamp:
                                dir_size = 0
                                for root, _, files in os.walk(item_path):
                                    for f in files:
                                        try:
                                            dir_size += os.path.getsize(os.path.join(root, f))
                                        except Exception:
                                            pass
                                shutil.rmtree(item_path, ignore_errors=True)
                                deleted_dirs_count += 1
                                freed_bytes += dir_size
                        except Exception as e:
                            print(f"[STORAGE CLEANUP] Warning: Could not remove temp dir {item_path}: {e}")
        except Exception as dir_err:
            print(f"[STORAGE CLEANUP] Error reading search directory {search_dir}: {dir_err}")

    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    print(f"[STORAGE CLEANUP] Cleanup complete: Removed {deleted_files_count} debug files and {deleted_dirs_count} temp profiles ({freed_mb} MB reclaimed).")

    return {
        "status": "SUCCESS",
        "max_age_days": max_age_days,
        "deleted_files_count": deleted_files_count,
        "deleted_dirs_count": deleted_dirs_count,
        "freed_mb": freed_mb,
    }
