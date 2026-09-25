import os
import sys
import unittest
from types import ModuleType

# 1. Stub third-party dependencies that may not be installed in the host python
sys.modules["aiofiles"] = ModuleType("aiofiles")

aiofiles_os = ModuleType("aiofiles.os")
aiofiles_os.makedirs = lambda *args, **kwargs: None
aiofiles_os.remove = lambda *args, **kwargs: None
aiofiles_os.listdir = lambda *args, **kwargs: []
aiofiles_os.stat = lambda *args, **kwargs: None
aiofiles_os.rmdir = lambda *args, **kwargs: None
aiofiles_os.rename = lambda *args, **kwargs: None
aiofiles_os.readlink = lambda *args, **kwargs: None
aiofiles_os.symlink = lambda *args, **kwargs: None
aiofiles_os.path = ModuleType("aiofiles.os.path")
sys.modules["aiofiles.os"] = aiofiles_os
sys.modules["aiofiles.os.path"] = aiofiles_os.path

aioshutil_mod = ModuleType("aioshutil")
aioshutil_mod.rmtree = lambda *args, **kwargs: None
aioshutil_mod.move = lambda *args, **kwargs: None
sys.modules["aioshutil"] = aioshutil_mod

httpx_mod = ModuleType("httpx")
httpx_mod.AsyncClient = ModuleType("httpx.AsyncClient")
sys.modules["httpx"] = httpx_mod

magic_mod = ModuleType("magic")
magic_mod.Magic = lambda *args, **kwargs: None
sys.modules["magic"] = magic_mod

pil_mod = ModuleType("PIL")
pil_image_mod = ModuleType("PIL.Image")
pil_mod.Image = pil_image_mod
sys.modules["PIL"] = pil_mod
sys.modules["PIL.Image"] = pil_image_mod

# 2. Setup paths
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 3. Stub the dependencies
bot_pkg = ModuleType("bot")
bot_pkg.__path__ = []


class _Logger:

    @staticmethod
    def info(msg):
        pass

    @staticmethod
    def error(msg):
        pass


bot_pkg.LOGGER = _Logger()
bot_pkg.DOWNLOAD_DIR = "/app/downloads/"
bot_pkg.threads = 4
bot_pkg.cores = "0-3"
bot_pkg.task_dict = {}
bot_pkg.task_dict_lock = None

config_pkg = ModuleType("bot.core")
config_pkg.__path__ = []
config_manager = ModuleType("bot.core.config_manager")


class Config:
    TLDV_TOKEN = "global-test-token"


config_manager.Config = Config

torrent_manager_mod = ModuleType("bot.core.torrent_manager")
torrent_manager_mod.TorrentManager = ModuleType("bot.core.torrent_manager.TorrentManager")
sys.modules["bot.core.torrent_manager"] = torrent_manager_mod

helper_pkg = ModuleType("bot.helper")
helper_pkg.__path__ = []

ext_utils_pkg = ModuleType("bot.helper.ext_utils")
ext_utils_pkg.__path__ = [
    os.path.join(project_root, "bot", "helper", "ext_utils")
]

bot_utils_mod = ModuleType("bot.helper.ext_utils.bot_utils")
bot_utils_mod.cmd_exec = lambda *args, **kwargs: (b"", b"", 0)
bot_utils_mod.sync_to_async = lambda func, *args, **kwargs: func(*args, **kwargs)

import re

def _clean_caption_name(caption, original_filename=""):
    if not caption:
        return ""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA70-\U0001FAFF"
        "\u2702-\u27B0"
        "\u24C2-\u25B6"
        "\u2600-\u27EF"
        "\u2300-\u23FF"
        "\u2B00-\u2BFF"
        "\u200D"
        "\uFE0F"
        "]+",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", caption)
    cleaned = " ".join(cleaned.split()).strip()

    ext_match = re.search(
        r"^(.*?\.[a-zA-Z0-9]{2,4})\b", cleaned, re.IGNORECASE | re.DOTALL
    )
    if ext_match:
        name = ext_match.group(1).strip()
    else:
        ext = ""
        if original_filename and "." in original_filename:
            ext = "." + original_filename.rsplit(".", 1)[-1]
        name = cleaned + ext if ext else cleaned
    return name

bot_utils_mod.clean_caption_name = _clean_caption_name

task_manager_mod = ModuleType("bot.helper.ext_utils.task_manager")
task_manager_mod.check_running_tasks = lambda *args, **kwargs: (False, None)
task_manager_mod.stop_duplicate_check = lambda *args, **kwargs: (None, None)

status_utils_mod = ModuleType("bot.helper.ext_utils.status_utils")


class MirrorStatus:
    STATUS_DOWNLOAD = "Downloading"
    STATUS_METADATA = "Applying Metadata"
    STATUS_MERGE = "Merging"
    STATUS_CONVERT = "Converting"
    STATUS_SPLIT = "Splitting"
    STATUS_SAMVID = "SamVid"
    STATUS_FFMPEG = "FFmpeg"


status_utils_mod.MirrorStatus = MirrorStatus
status_utils_mod.get_readable_file_size = lambda x: "10MB"
status_utils_mod.get_readable_time = lambda x: "10s"
status_utils_mod.time_to_seconds = lambda x: 0

mlu_pkg = ModuleType("bot.helper.mirror_leech_utils")
mlu_pkg.__path__ = [
    os.path.join(project_root, "bot", "helper", "mirror_leech_utils")
]

status_utils_dir = ModuleType("bot.helper.mirror_leech_utils.status_utils")
status_utils_dir.__path__ = [
    os.path.join(project_root, "bot", "helper", "mirror_leech_utils", "status_utils")
]

queue_status_mod = ModuleType(
    "bot.helper.mirror_leech_utils.status_utils.queue_status"
)


class QueueStatus:

    def __init__(self, *args):
        pass


queue_status_mod.QueueStatus = QueueStatus

tldv_status_mod = ModuleType(
    "bot.helper.mirror_leech_utils.status_utils.tldv_status"
)


class TldvStatus:

    def __init__(self, *args):
        pass


tldv_status_mod.TldvStatus = TldvStatus

download_utils_pkg = ModuleType(
    "bot.helper.mirror_leech_utils.download_utils"
)
download_utils_pkg.__path__ = [
    os.path.join(
        project_root, "bot", "helper", "mirror_leech_utils", "download_utils"
    )
]

message_utils_mod = ModuleType("bot.helper.telegram_helper.message_utils")
message_utils_mod.send_status_message = lambda *args, **kwargs: None

sys.modules["bot"] = bot_pkg
sys.modules["bot.core"] = config_pkg
sys.modules["bot.core.config_manager"] = config_manager
sys.modules["bot.helper"] = helper_pkg
sys.modules["bot.helper.ext_utils"] = ext_utils_pkg
sys.modules["bot.helper.ext_utils.bot_utils"] = bot_utils_mod
sys.modules["bot.helper.ext_utils.task_manager"] = task_manager_mod
sys.modules["bot.helper.ext_utils.status_utils"] = status_utils_mod
sys.modules["bot.helper.mirror_leech_utils"] = mlu_pkg
sys.modules["bot.helper.mirror_leech_utils.status_utils"] = status_utils_dir
sys.modules["bot.helper.mirror_leech_utils.status_utils.queue_status"] = (
    queue_status_mod
)
sys.modules["bot.helper.mirror_leech_utils.status_utils.tldv_status"] = (
    tldv_status_mod
)
sys.modules["bot.helper.mirror_leech_utils.download_utils"] = download_utils_pkg
sys.modules["bot.helper.telegram_helper"] = ModuleType(
    "bot.helper.telegram_helper"
)
sys.modules["bot.helper.telegram_helper.message_utils"] = message_utils_mod

# 4. Import the downloader under test
from bot.helper.mirror_leech_utils.download_utils.tldv_downloader import (
    caesar_decipher,
    parse_tldv_conf,
    get_tldv_token,
)
from tests.test_caption_and_merge import TestCaptionAndMerge


class TestTldv(unittest.TestCase):

    def test_caesar_decipher(self):
        self.assertEqual(caesar_decipher("abcXYZ012", 3), "defABC012")
        self.assertEqual(caesar_decipher("defABC012", -3), "abcXYZ012")
        self.assertEqual(caesar_decipher("abc", 26 + 3), "def")
        self.assertEqual(caesar_decipher("abcXYZ", 0), "abcXYZ")

    def test_parse_tldv_conf(self):
        line = "#TLDVCONF:1234567890,13,https://example.com/stream/"
        expiry, offset, base_url = parse_tldv_conf(line)
        self.assertEqual(expiry, "1234567890")
        self.assertEqual(offset, 13)
        self.assertEqual(base_url, "https://example.com/stream/")

    def test_get_tldv_token(self):
        # 1. From Config fallback
        self.assertEqual(get_tldv_token(None), "global-test-token")

        # 2. From headers list
        self.assertEqual(
            get_tldv_token(None, ["authorization: bearer special-token"]),
            "special-token",
        )
        self.assertEqual(
            get_tldv_token(None, ["Cookie: tldvtoken=cookie-token; other=1"]),
            "cookie-token",
        )


if __name__ == "__main__":
    unittest.main()
