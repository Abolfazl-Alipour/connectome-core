import unittest
import numpy as np
import os
import shutil
import tempfile
from src.analytics.null_models import generate_core_null_models

class TestNullModels(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.core_dir = os.path.join(self.test_dir, "group_cores")
        self.control_dir = os.path.join(self.test_dir, "control_networks")
        os.makedirs(self.core_dir, exist_ok=True)
        
        # Create synthetic 30-node core submatrix with ~30% edge density
        N = 30
        np.random.seed(42)
        sift = np.random.uniform(0, 10, (N, N))
        sift = (sift + sift.T) / 2
        np.fill_diagonal(sift, 0)
        
        # Sparsify to realistic 30% density
        mask = (sift > 6.0)
        sift = sift * mask
        prev = mask.astype(float)
        
        np.savetxt(os.path.join(self.core_dir, "core_sift_30.csv"), sift, delimiter=",")
        np.savetxt(os.path.join(self.core_dir, "core_prevalence_30.csv"), prev, delimiter=",")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_null_models_generation(self):
        generate_core_null_models(self.core_dir, self.control_dir, [30])
        
        er_path = os.path.join(self.control_dir, "er", "control_er_sift_30.csv")
        reg_path = os.path.join(self.control_dir, "regular", "control_regular_sift_30.csv")
        dp_path = os.path.join(self.control_dir, "degree_preserved", "control_degree_preserved_sift_30.csv")
        
        self.assertTrue(os.path.exists(er_path))
        self.assertTrue(os.path.exists(reg_path))
        self.assertTrue(os.path.exists(dp_path))
        
        mat_er = np.loadtxt(er_path, delimiter=",")
        self.assertEqual(mat_er.shape, (30, 30))

if __name__ == "__main__":
    unittest.main()
