import unittest

from gh_template_py import _utils


class TestCase(unittest.TestCase):
    def test_log(self):
        self.assertTrue(_utils.log is not None)


if __name__ == '__main__':
    unittest.main()
