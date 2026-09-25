"""Tests for the BuzzHeavier uploader."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def buzzheavier_module(monkeypatch):
    import bot.core.config_manager as cm
    import bot.helper.mirror_leech_utils.upload_utils.buzzheavier_uploader as bhu

    monkeypatch.setattr(cm.Config, "BUZZHEAVIER_ACCOUNT_ID", "", raising=False)
    return bhu


def _make_listener():
    return SimpleNamespace(
        is_cancelled=False,
        size=0,
        up_dest="",
        user_dict={},
        on_upload_complete=AsyncMock(),
        on_upload_error=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_upload_walks_directory(buzzheavier_module, tmp_path, monkeypatch):
    import asyncio
    file_a = tmp_path / "a.bin"
    file_b = tmp_path / "sub" / "b.bin"
    file_b.parent.mkdir()
    file_a.write_bytes(b"a" * 1024)
    file_b.write_bytes(b"b" * 2048)

    listener = _make_listener()
    listener.size = file_a.stat().st_size + file_b.stat().st_size

    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))

    upload_calls: list[str] = []

    async def fake_upload_file(self, file_path, parent_id):
        upload_calls.append(os.path.basename(file_path))
        self._processed_bytes += os.path.getsize(file_path)
        self._files += 1
        return f"https://buzzheavier.com/{os.path.basename(file_path)}"

    async def fake_create_directory(self, name, parent_id):
        return "root_folder_id"

    monkeypatch.setattr(
        buzzheavier_module.BuzzHeavierUploader,
        "_upload_file",
        fake_upload_file,
    )
    monkeypatch.setattr(
        buzzheavier_module.BuzzHeavierUploader,
        "_create_directory",
        fake_create_directory,
    )
    monkeypatch.setattr(
        buzzheavier_module,
        "sync_to_async",
        lambda func, *args, **kwargs: asyncio.sleep(0, result=func(*args, **kwargs)),
    )

    await uploader.upload()

    assert sorted(upload_calls) == ["a.bin", "b.bin"]
    listener.on_upload_complete.assert_awaited()
    args = listener.on_upload_complete.await_args.args
    assert args[0] == "https://buzzheavier.com/root_folder_id"
    assert args[1] == 2
    assert args[2] == 1
    assert args[3] == "Folder"


@pytest.mark.asyncio
async def test_upload_handles_empty_path(buzzheavier_module, tmp_path):
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(
        listener, str(tmp_path / "non_existent_file.txt")
    )
    await uploader.upload()
    listener.on_upload_error.assert_awaited()
    listener.on_upload_complete.assert_not_awaited()


@pytest.mark.asyncio
async def test_upload_aborts_when_cancelled(
    buzzheavier_module, tmp_path, monkeypatch
):
    import asyncio
    file_a = tmp_path / "a.bin"
    file_a.write_bytes(b"a" * 16)
    listener = _make_listener()
    listener.size = file_a.stat().st_size

    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))

    async def fake_create_directory(self, name, parent_id):
        listener.is_cancelled = True
        return "root_folder_id"

    monkeypatch.setattr(
        buzzheavier_module.BuzzHeavierUploader,
        "_create_directory",
        fake_create_directory,
    )
    monkeypatch.setattr(
        buzzheavier_module,
        "sync_to_async",
        lambda func, *args, **kwargs: asyncio.sleep(0, result=func(*args, **kwargs)),
    )

    await uploader.upload()

    listener.on_upload_error.assert_not_awaited()
    listener.on_upload_complete.assert_not_awaited()


def test_status_interface_exposed(buzzheavier_module, tmp_path):
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))
    assert hasattr(uploader, "processed_bytes")
    assert isinstance(uploader.processed_bytes, int)
    assert hasattr(uploader, "speed")
    assert uploader.speed == 0.0


def test_auth_headers_uses_config(buzzheavier_module, monkeypatch):
    monkeypatch.setattr(
        buzzheavier_module.Config, "BUZZHEAVIER_ACCOUNT_ID", "abc-123"
    )
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(listener, "dummy")
    assert uploader._account_id == "abc-123"


def test_auth_headers_empty_when_unset(buzzheavier_module, monkeypatch):
    monkeypatch.setattr(
        buzzheavier_module.Config, "BUZZHEAVIER_ACCOUNT_ID", ""
    )
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(listener, "dummy")
    assert uploader._account_id == ""
