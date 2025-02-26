import os
import platform
import unittest

import torch
import torchtext.data as data
from torchtext.experimental.transforms import basic_english_normalize, regex_tokenizer

from ..common.torchtext_test_case import TorchtextTestCase


class TestFunctional(TorchtextTestCase):
    # TODO(Nayef211): remove decorator once https://github.com/pytorch/pytorch/issues/38207 is closed
    @unittest.skipIf(platform.system() == "Windows", "Test is known to fail on Windows.")
    def test_BasicEnglishNormalize(self):
        test_sample = "'\".<br />,()!?;:   Basic English Normalization for a Line of Text   '\".<br />,()!?;:"
        ref_results = [
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
            "basic",
            "english",
            "normalization",
            "for",
            "a",
            "line",
            "of",
            "text",
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
        ]

        basic_eng_norm = basic_english_normalize()
        experimental_eager_tokens = basic_eng_norm(test_sample)

        jit_basic_eng_norm = torch.jit.script(basic_eng_norm)
        experimental_jit_tokens = jit_basic_eng_norm(test_sample)

        basic_english_tokenizer = data.get_tokenizer("basic_english")
        eager_tokens = basic_english_tokenizer(test_sample)

        assert not basic_eng_norm.is_jitable
        # Call the __prepare_scriptable__() func and convert the building block to the torbhind version
        # Not expect users to use the torchbind version on eager mode but still need a CI test here.
        assert basic_eng_norm.__prepare_scriptable__().is_jitable

        self.assertEqual(experimental_jit_tokens, ref_results)
        self.assertEqual(eager_tokens, ref_results)
        self.assertEqual(experimental_eager_tokens, ref_results)

    def test_basicEnglishNormalize_load_and_save(self):
        test_sample = "'\".<br />,()!?;:   Basic English Normalization for a Line of Text   '\".<br />,()!?;:"
        ref_results = [
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
            "basic",
            "english",
            "normalization",
            "for",
            "a",
            "line",
            "of",
            "text",
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
        ]

        with self.subTest("pybind"):
            save_path = os.path.join(self.test_dir, "ben_pybind.pt")
            ben = basic_english_normalize()
            torch.save(ben, save_path)
            loaded_ben = torch.load(save_path)
            self.assertEqual(loaded_ben(test_sample), ref_results)

        with self.subTest("torchscript"):
            save_path = os.path.join(self.test_dir, "ben_torchscrip.pt")
            # Call the __prepare_scriptable__() func and convert the building block to the torbhind version
            # Not expect users to use the torchbind version on eager mode but still need a CI test here.
            ben = basic_english_normalize().__prepare_scriptable__()
            torch.save(ben, save_path)
            loaded_ben = torch.load(save_path)
            self.assertEqual(loaded_ben(test_sample), ref_results)

    # TODO(Nayef211): remove decorator once	https://github.com/pytorch/pytorch/issues/38207 is closed
    @unittest.skipIf(platform.system() == "Windows", "Test is known to fail on Windows.")
    def test_RegexTokenizer(self):
        test_sample = "'\".<br />,()!?;:   Basic Regex Tokenization for a Line of Text   '\".<br />,()!?;:"
        ref_results = [
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
            "Basic",
            "Regex",
            "Tokenization",
            "for",
            "a",
            "Line",
            "of",
            "Text",
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
        ]
        patterns_list = [
            (r"\'", " '  "),
            (r"\"", ""),
            (r"\.", " . "),
            (r"<br \/>", " "),
            (r",", " , "),
            (r"\(", " ( "),
            (r"\)", " ) "),
            (r"\!", " ! "),
            (r"\?", " ? "),
            (r"\;", " "),
            (r"\:", " "),
            (r"\s+", " "),
        ]

        r_tokenizer = regex_tokenizer(patterns_list)
        eager_tokens = r_tokenizer(test_sample)

        jit_r_tokenizer = torch.jit.script(r_tokenizer)
        jit_tokens = jit_r_tokenizer(test_sample)

        assert not r_tokenizer.is_jitable
        # Call the __prepare_scriptable__() func and convert the building block to the torbhind version
        # Not expect users to use the torchbind version on eager mode but still need a CI test here.
        assert r_tokenizer.__prepare_scriptable__().is_jitable

        self.assertEqual(eager_tokens, ref_results)
        self.assertEqual(jit_tokens, ref_results)

    def test_load_and_save(self):
        test_sample = "'\".<br />,()!?;:   Basic Regex Tokenization for a Line of Text   '\".<br />,()!?;:"
        ref_results = [
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
            "Basic",
            "Regex",
            "Tokenization",
            "for",
            "a",
            "Line",
            "of",
            "Text",
            "'",
            ".",
            ",",
            "(",
            ")",
            "!",
            "?",
        ]
        patterns_list = [
            (r"\'", " '  "),
            (r"\"", ""),
            (r"\.", " . "),
            (r"<br \/>", " "),
            (r",", " , "),
            (r"\(", " ( "),
            (r"\)", " ) "),
            (r"\!", " ! "),
            (r"\?", " ? "),
            (r"\;", " "),
            (r"\:", " "),
            (r"\s+", " "),
        ]

        with self.subTest("pybind"):
            save_path = os.path.join(self.test_dir, "regex_pybind.pt")
            tokenizer = regex_tokenizer(patterns_list)
            torch.save(tokenizer, save_path)
            loaded_tokenizer = torch.load(save_path)
            results = loaded_tokenizer(test_sample)
            self.assertEqual(results, ref_results)

        with self.subTest("torchscript"):
            save_path = os.path.join(self.test_dir, "regex_torchscript.pt")
            # Call the __prepare_scriptable__() func and convert the building block to the torbhind version
            # Not expect users to use the torchbind version on eager mode but still need a CI test here.
            tokenizer = regex_tokenizer(patterns_list).__prepare_scriptable__()
            torch.save(tokenizer, save_path)
            loaded_tokenizer = torch.load(save_path)
            results = loaded_tokenizer(test_sample)
            self.assertEqual(results, ref_results)
