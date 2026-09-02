import unittest
import numpy as np
import os
import shutil
import tempfile
from src.analytics.score import extract_score

class TestScoreExtraction(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.in_dir = os.path.join(self.test_dir, "group_connectomes")
        self.out_dir = os.path.join(self.test_dir, "group_cores")
        os.makedirs(self.in_dir, exist_ok=True)
        
        # Create synthetic 100-node connectome
        N = 100
        np.random.seed(42)
        sift = np.random.uniform(0, 10, (N, N))
        sift = (sift + sift.T) / 2
        np.fill_diagonal(sift, 0)
        
        prev = (sift > 2).astype(float)
        length = np.random.uniform(10, 150, (N, N))
        
        np.savetxt(os.path.join(self.in_dir, "group_mean_sift_100.csv"), sift, delimiter=",")
        np.savetxt(os.path.join(self.in_dir, "group_prevalence_100.csv"), prev, delimiter=",")
        np.savetxt(os.path.join(self.in_dir, "group_mean_length_100.csv"), length, delimiter=",")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_score_15_percent(self):
        stats = extract_score(self.in_dir, self.out_dir, [100], retention_percentage=0.15)
        self.assertIn(100, stats)
        self.assertEqual(stats[100]["target_core_nodes"], 15)
        self.assertTrue(os.path.exists(os.path.join(self.out_dir, "core_sift_100.csv")))
        
        core_sift = np.loadtxt(os.path.join(self.out_dir, "core_sift_100.csv"), delimiter=",")
        self.assertEqual(core_sift.shape[0], stats[100]["final_gcc_nodes"])
        self.assertEqual(core_sift.shape[1], stats[100]["final_gcc_nodes"])

if __name__ == "__main__":
    unittest.main()
