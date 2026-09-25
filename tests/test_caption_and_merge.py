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


if __name__ == "__main__":
    unittest.main()
