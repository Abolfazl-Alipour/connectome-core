import unittest
import numpy as np
import os
import shutil
import tempfile
from src.analytics.subnetworks import extract_subnetwork_matrices, get_schaefer_labels, YEO_7_NETWORKS

class TestSubnetworkExtraction(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.out_dir = os.path.join(self.test_dir, "subnetworks")
        os.makedirs(self.out_dir, exist_ok=True)
        
        # Create synthetic 1000-node connectome
        N = 1000
        np.random.seed(42)
        sift = np.random.uniform(0, 10, (N, N))
        sift = (sift + sift.T) / 2
        np.fill_diagonal(sift, 0)
        
        length = np.random.uniform(10, 150, (N, N))
        length = (length + length.T) / 2
        np.fill_diagonal(length, 0)
        
        self.sift_path = os.path.join(self.test_dir, "group_mean_sift_1000.csv")
        self.length_path = os.path.join(self.test_dir, "group_mean_length_1000.csv")
        np.savetxt(self.sift_path, sift, delimiter=",")
        np.savetxt(self.length_path, length, delimiter=",")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_yeo_partition_sum(self):
        labels = get_schaefer_labels(1000)
        self.assertEqual(len(labels), 1000)
        
        results = extract_subnetwork_matrices(
            self.sift_path,
            self.length_path,
            self.out_dir,
            resolution=1000
        )
        
        # 1. Check all 7 Yeo networks exist and sum to 1000
        yeo_sum = sum(results[net]["num_nodes"] for net in YEO_7_NETWORKS)
        self.assertEqual(yeo_sum, 1000)
        
        # 2. Check consciousness subgraphs exist
        self.assertIn("Posterior_Hot_Zone", results)
        self.assertIn("Global_Neuronal_Workspace", results)
        self.assertGreater(results["Posterior_Hot_Zone"]["num_nodes"], 400)
        self.assertGreater(results["Global_Neuronal_Workspace"]["num_nodes"], 300)
        
        # 3. Check matrix symmetry and files existence
        for net in YEO_7_NETWORKS + ["Posterior_Hot_Zone", "Global_Neuronal_Workspace"]:
            sub_dir = os.path.join(self.out_dir, net.lower())
            sift_file = os.path.join(sub_dir, "subnetwork_sift_1000.csv")
            length_file = os.path.join(sub_dir, "subnetwork_length_1000.csv")
            idx_file = os.path.join(sub_dir, "subnetwork_indices_1000.csv")
            
            self.assertTrue(os.path.exists(sift_file))
            self.assertTrue(os.path.exists(length_file))
            self.assertTrue(os.path.exists(idx_file))
            
            mat = np.loadtxt(sift_file, delimiter=",")
            n = results[net]["num_nodes"]
            self.assertEqual(mat.shape, (n, n))
            self.assertTrue(np.allclose(mat, mat.T))
            self.assertTrue(np.allclose(np.diag(mat), 0.0))

if __name__ == "__main__":
    unittest.main()
