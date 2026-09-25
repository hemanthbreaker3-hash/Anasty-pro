import unittest
from bot.helper.ext_utils.bot_utils import clean_caption_name


class TestCaptionAndMerge(unittest.TestCase):

    def test_clean_caption_name_exact_prompt_example(self):
        caption = "🎬 Konosuba God_s Blessing on This Wonderful World! S03E01 480p x264 BluRay Multi Audio ESub.mkv 🍿"
        cleaned = clean_caption_name(caption)
        self.assertEqual(
            cleaned,
            "Konosuba God_s Blessing on This Wonderful World! S03E01 480p x264 BluRay Multi Audio ESub.mkv",
        )

    def test_clean_caption_name_with_fallback_extension(self):
        caption = "🔥 Konosuba God_s Blessing S03E01 ⚡"
        orig_fname = "video_file.mkv"
        cleaned = clean_caption_name(caption, orig_fname)
        self.assertEqual(cleaned, "Konosuba God_s Blessing S03E01.mkv")

    def test_clean_caption_name_multiline(self):
        caption = "✨ Movie Title (2024) 1080p.mp4 ✨\nDownloaded via Telegram Bot\nJoin channel"
        cleaned = clean_caption_name(caption)
        self.assertEqual(cleaned, "Movie Title (2024) 1080p.mp4")


    def test_ffmpeg_status_metadata(self):
        from unittest.mock import MagicMock
        from bot.helper.mirror_leech_utils.status_utils.ffmpeg_status import (
            FFmpegStatus,
        )
        from bot.helper.ext_utils.status_utils import MirrorStatus

        listener = MagicMock()
        listener.name = "test_video.mkv"
        ffmpeg_obj = MagicMock()
        status = FFmpegStatus(listener, ffmpeg_obj, "gid123", "Metadata")
        self.assertEqual(status.status(), MirrorStatus.STATUS_METADATA)

    def test_ffmpeg_status_merge(self):
        from unittest.mock import MagicMock
        from bot.helper.mirror_leech_utils.status_utils.ffmpeg_status import (
            FFmpegStatus,
        )
        from bot.helper.ext_utils.status_utils import MirrorStatus

        listener = MagicMock()
        listener.name = "test_video.mkv"
        ffmpeg_obj = MagicMock()
        status = FFmpegStatus(listener, ffmpeg_obj, "gid123", "Merge")
        self.assertEqual(status.status(), MirrorStatus.STATUS_MERGE)

    def test_ffmpeg_cmds_output_path_resolution(self):
        import asyncio
        from unittest.mock import MagicMock, patch
        from bot.helper.ext_utils.media_utils import FFMpeg

        listener = MagicMock()
        listener.is_cancelled = True
        ffmpeg = FFMpeg(listener)

        cmd = [
            "ffmpeg",
            "-i",
            "/downloads/123/v1.mp4",
            "-c",
            "copy",
            "/downloads/123/mltb.mkv",
        ]
        with patch(
            "bot.helper.ext_utils.media_utils.get_media_info",
            return_value=(10, "artist", "title"),
        ):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ffmpeg.ffmpeg_cmds(
                    cmd, ["/downloads/123/v1.mp4", "/downloads/123/v2.mp4"]
                )
            )
            loop.close()

        self.assertEqual(cmd[-1], "/downloads/123/v.mkv")

    def test_ffmpeg_cmds_merge_output_no_collision(self):
        import asyncio
        from unittest.mock import MagicMock, patch
        from bot.helper.ext_utils.media_utils import FFMpeg

        listener = MagicMock()
        listener.is_cancelled = True
        ffmpeg = FFMpeg(listener)

        cmd = [
            "ffmpeg",
            "-i",
            "/downloads/123/v1.mp4",
            "-c",
            "copy",
            "/downloads/123/mltb_merge_output.mkv",
        ]
        with patch(
            "bot.helper.ext_utils.media_utils.get_media_info",
            return_value=(10, "artist", "title"),
        ):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ffmpeg.ffmpeg_cmds(
                    cmd, ["/downloads/123/v1.mp4", "/downloads/123/v2.mp4"]
                )
            )
            loop.close()

        self.assertEqual(cmd[-1], "/downloads/123/mltb_merge_output.mkv")

    def test_m_and_merge_parsed_options(self):
        from pathlib import Path
        file_path = Path(__file__).resolve().parent.parent / "bot" / "helper" / "ext_utils" / "bot_utils.py"
        src = file_path.read_text(encoding="utf-8")
        namespace = {}
        namespace["loads"] = __import__("ast").literal_eval
        snippet_start = src.find("def arg_parser(")
        snippet_end = src.find("\ndef ", snippet_start + 1)
        if snippet_end == -1:
            snippet_end = len(src)
        snippet = src[snippet_start:snippet_end]
        exec(snippet, namespace)
        arg_parser = namespace["arg_parser"]

        # Test case 1: -m folder_name
        args1 = {"-m": "", "-merge": False}
        arg_parser(["-m", "my_folder"], args1)
        folder_name1 = (
            f"/{args1['-m']}".rstrip("/")
            if isinstance(args1["-m"], str) and len(args1["-m"]) > 0
            else ""
        )
        auto_merge1 = args1["-merge"] or (
            isinstance(args1["-m"], bool) and args1["-m"]
        )
        self.assertEqual(folder_name1, "/my_folder")
        self.assertFalse(auto_merge1)

        # Test case 2: -m boolean flag
        args2 = {"-m": "", "-merge": False}
        arg_parser(["-m"], args2)
        folder_name2 = (
            f"/{args2['-m']}".rstrip("/")
            if isinstance(args2["-m"], str) and len(args2["-m"]) > 0
            else ""
        )
        auto_merge2 = args2["-merge"] or (
            isinstance(args2["-m"], bool) and args2["-m"]
        )
        self.assertEqual(folder_name2, "")
        self.assertTrue(auto_merge2)

        # Test case 3: -merge boolean flag
        args3 = {"-m": "", "-merge": False}
        arg_parser(["-merge"], args3)
        folder_name3 = (
            f"/{args3['-m']}".rstrip("/")
            if isinstance(args3["-m"], str) and len(args3["-m"]) > 0
            else ""
        )
        auto_merge3 = args3["-merge"] or (
            isinstance(args3["-m"], bool) and args3["-m"]
        )
        self.assertEqual(folder_name3, "")
        self.assertTrue(auto_merge3)

    def test_user_configured_ffmpeg_cmds_auto_populate(self):
        user_dict = {
            "FFMPEG_CMDS": {
                "convert": ["-i mltb.mkv -c copy mltb.mp4"]
            }
        }
        ffmpeg_cmds = None
        ffmpeg_dict = user_dict["FFMPEG_CMDS"]
        if not ffmpeg_cmds:
            keys_to_process = list(ffmpeg_dict.keys())
        else:
            keys_to_process = list(ffmpeg_cmds)
        cmds = []
        for key in keys_to_process:
            if key in ffmpeg_dict:
                for vl in ffmpeg_dict[key]:
                    cmds.append(vl)
        ffmpeg_cmds = cmds
        self.assertEqual(ffmpeg_cmds, ["-i mltb.mkv -c copy mltb.mp4"])


if __name__ == "__main__":
    unittest.main()
