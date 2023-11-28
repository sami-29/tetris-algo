import unittest
from TetrisGameGenerator import TetrisGameGenerator

class TestTetrisGameGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = TetrisGameGenerator()

    def test_generate_sequence_with_max_moves(self):
        sequence = self.generator.generate_sequence(10)
        self.assertEqual(len(sequence), 10)
        self.assertCountEqual(sequence, self.generator.tetrominoes_names[:10])

    def test_generate_sequence_without_max_moves(self):
        sequence = self.generator.generate_sequence(None)
        self.assertEqual(len(sequence), self.generator.tetrominoes)
        self.assertCountEqual(sequence, self.generator.tetrominoes_names)

    def test_generate_sequence_with_invalid_max_moves(self):
        sequence = self.generator.generate_sequence(-5)
        self.assertEqual(len(sequence), 0)

if __name__ == '__main__':
    unittest.main()
