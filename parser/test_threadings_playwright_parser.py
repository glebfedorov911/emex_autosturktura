import unittest
from unittest.mock import patch
from io import StringIO

from threadings_playwright_parser import run, NoneException

from playwright.async_api import TimeoutError as playwright_TimeoutError


class ParserTest(unittest.TestCase):
    def test_proxy(self):
        self.assertRaises((playwright_TimeoutError, IndexError), run, ["Peugeot---Citroen", "Mahle---Knecht", "Peugeot---Citroen", "Peugeot---Citroen"]*2, ["82026", "02943N0", "362312", "00004254A2"]*2, [["http://45.81.136.39:1050", "2Q3n1o", "FjvCaesiwS"]])
        self.assertRaises((playwright_TimeoutError, IndexError), run, ["Peugeot---Citroen", "Mahle---Knecht", "Peugeot---Citroen", "Peugeot---Citroen"]*2, ["82026", "02943N0", "362312", "00004254A2"]*2, [["http://111.182.124.119:1050", "2Q3n1o", "FjvCaesiwS"], ["http://45.81.136.39:1050", "2Q3n1o", "FjvCaesiwS"]])

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_word(self, mock_stdout):
        run(["Autocomponent", "Peugeot---Citroen"], ["01М21С9", "82026"], [["http://188.130.219.173:1050", "2Q3n1o", "FjvCaesiwS"]])
        self.assertEqual(mock_stdout.getvalue().strip().split("\n")[0], "Данный продукт не в наличии")
        run(["Autocomponent"], ["01М21С9"], [["http://188.130.219.173:1050", "2Q3n1o", "FjvCaesiwS"]])
        self.assertEqual(mock_stdout.getvalue().strip().split("\n")[0], "Данный продукт не в наличии")
        run(["Peugeot---Citroen"], ["01М21С9"], [["http://188.130.219.173:1050", "2Q3n1o", "FjvCaesiwS"]])
        self.assertEqual(mock_stdout.getvalue().strip().split("\n")[0], "Данный продукт не в наличии")

if __name__ == "__main__":
    unittest.main()
