import unittest
import os
import tempfile
import json
from src.utils import load_categories
from src.main import parse_args

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_categories_txt(self):
        txt_path = os.path.join(self.temp_dir.name, "cats.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Invoice\nReceipt \n\n")
        
        categories = load_categories(txt_path)
        self.assertEqual(categories, ["Invoice", "Receipt"])
        
    def test_load_categories_json(self):
        json_path = os.path.join(self.temp_dir.name, "cats.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(["Invoice", " Receipt ", ""], f)
            
        categories = load_categories(json_path)
        self.assertEqual(categories, ["Invoice", "Receipt"])
        
    def test_load_categories_inline(self):
        categories = load_categories("Invoice, Receipt, Letter")
        self.assertEqual(categories, ["Invoice", "Receipt", "Letter"])

class TestCLI(unittest.TestCase):
    def test_parse_args(self):
        args = parse_args(["-i", "file1.pdf", "file2.pdf", "-c", "cats.txt", "-o", "out_dir", "--instructions", "inst.txt"])
        self.assertEqual(args.input_pdfs, ["file1.pdf", "file2.pdf"])
        self.assertEqual(args.categories_file, "cats.txt")
        self.assertEqual(args.output_dir, "out_dir")
        self.assertEqual(args.instructions, "inst.txt")

if __name__ == "__main__":
    unittest.main()
