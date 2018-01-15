from dragon.transpiler.lark.validators.lark_validator import LarkValidator
from lark.lexer import Token
from lark import Tree
import os
import unittest

class TestLarkValidator(unittest.TestCase):

    _GRAMMAR_LOCATION = os.path.join("dragon", "transpiler", "lark", "python3.g")

    def test_is_fully_parsed_succeeds_if_all_tokens_are_transformed(self):
        # Just a bunch of tokens, like "super", "update", "elapsed"
        tree = [Tree("getattr", ['super', Token("NAME", 'update')]), Tree("arguments", ['elapsed'])]
        validator = LarkValidator(TestLarkValidator._GRAMMAR_LOCATION)
        self.assertTrue(validator.is_fully_parsed(tree))

    def test_is_fully_parsed_fails_if_token_remains(self):
        # raw tokens: file_input, compound_stmt, classdef, suite, pass_stmt
        tree = Tree("file_input", [Tree("compound_stmt", [Tree("classdef",
            [Token("NAME", 'AssetPaths'), Tree("suite", [Tree("pass_stmt", [])])])])])

        validator = LarkValidator(TestLarkValidator._GRAMMAR_LOCATION)
        self.assertFalse(validator.is_fully_parsed(tree))