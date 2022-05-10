from unittest import TestCase

from main import split_path

class Test(TestCase):
    def test_split_path(self):
        inp = 'this/is/path/to/file.ext'

        expected_path = 'this/is/path/to'
        expected_name = 'file.ext'

        path, name = split_path(inp)

        self.assertEqual(expected_path, path)
        self.assertEqual(expected_name, name)

    def test_split_path2(self):
        inp = 'file.ext'

        expected_path = ''
        expected_name = 'file.ext'


        path, name = split_path(inp)

        self.assertEqual(expected_path, path)
        self.assertEqual(expected_name, name)

    def test_split_path3(self):
        inp = 'C:/file.ext'

        expected_path = 'C:'
        expected_name = 'file.ext'

        path, name = split_path(inp)

        self.assertEqual(expected_path, path)
        self.assertEqual(expected_name, name)
