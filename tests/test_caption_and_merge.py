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


if __name__ == "__main__":
    unittest.main()
