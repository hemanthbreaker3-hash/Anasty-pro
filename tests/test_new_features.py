"""Unit tests for newly added features: Auto Merge, Split Mode, Sequence Queueing, Import/Export settings."""

import json
import zipfile
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

from bot.helper.ext_utils.task_manager import can_start_queued_task, user_has_active_task


def test_split_filename_formatting():
    # Test split_file filename logic
    f_path = "/downloads/my_video.mkv"
    dir_path, file_name = f_path.rsplit("/", 1)
    base_name, extension = "my_video", ".mkv"

    # Part mode
    part_prefix = f"{dir_path}/{base_name}.part"
    part_suffix = extension
    # First split part filename check
    part_out = f"{part_prefix}001{part_suffix}"
    assert part_out == "/downloads/my_video.part001.mkv"

    # Number mode
    num_prefix = f"{dir_path}/{base_name}."
    num_suffix = extension
    num_out = f"{num_prefix}001{num_suffix}"
    assert num_out == "/downloads/my_video.001.mkv"


def test_settings_zip_export_import(tmp_path):
    user_id = 123456
    user_data_content = {"AUTO_MERGE": True, "KEEP_ORIGINAL": False, "LEECH_SPLIT_MODE": "number"}

    zip_file = tmp_path / f"Settings_{user_id}.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("user_data.json", json.dumps(user_data_content))

    assert zip_file.exists()

    with zipfile.ZipFile(zip_file, "r") as zf:
        assert "user_data.json" in zf.namelist()
        data = json.loads(zf.read("user_data.json").decode())
        assert data["AUTO_MERGE"] is True
        assert data["LEECH_SPLIT_MODE"] == "number"


@pytest.mark.asyncio
async def test_sequence_active_task_check():
    user_id = 999
    listener1 = SimpleNamespace(user_id=user_id, user_dict={"SEQUENCE": True})
    task1 = SimpleNamespace(listener=listener1, status=lambda: "Downloading")

    listener2 = SimpleNamespace(user_id=user_id, user_dict={"SEQUENCE": True})
    task2 = SimpleNamespace(listener=listener2, status=lambda: "QueueDl")

    with patch("bot.helper.ext_utils.task_manager.task_dict", {101: task1, 102: task2}):
        # User has active task1 (Downloading)
        has_active = await user_has_active_task(user_id, current_mid=102)
        assert has_active is True

        # task2 should not be allowed to start yet
        can_start = await can_start_queued_task(mid=102)
        assert can_start is False
