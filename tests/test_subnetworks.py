import unittest
import numpy as np
import os
import shutil
import tempfile
from src.analytics.subnetworks import extract_subnetwork_matrices, get_schaefer_labels, YEO_7_NETWORKS, build_hybrid_node_metadata

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
        
        self.sift_path_1000 = os.path.join(self.test_dir, "group_mean_sift_1000.csv")
        self.length_path_1000 = os.path.join(self.test_dir, "group_mean_length_1000.csv")
        np.savetxt(self.sift_path_1000, sift, delimiter=",")
        np.savetxt(self.length_path_1000, length, delimiter=",")
        
        # Create synthetic 1014-node hybrid connectome
        N14 = 1014
        sift14 = np.random.uniform(0, 10, (N14, N14))
        sift14 = (sift14 + sift14.T) / 2
        np.fill_diagonal(sift14, 0)
        
        length14 = np.random.uniform(10, 150, (N14, N14))
        length14 = (length14 + length14.T) / 2
        np.fill_diagonal(length14, 0)
        
        self.sift_path_1014 = os.path.join(self.test_dir, "group_mean_sift_1014.csv")
        self.length_path_1014 = os.path.join(self.test_dir, "group_mean_length_1014.csv")
        np.savetxt(self.sift_path_1014, sift14, delimiter=",")
        np.savetxt(self.length_path_1014, length14, delimiter=",")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_yeo_partition_1000(self):
        labels = get_schaefer_labels(1000)
        self.assertEqual(len(labels), 1000)
        
        results = extract_subnetwork_matrices(
            self.sift_path_1000,
            self.length_path_1000,
            self.out_dir,
            resolution=1000,
            include_subcortical_augmented=False
        )
        
        yeo_sum = sum(results[net]["num_nodes"] for net in YEO_7_NETWORKS)
        self.assertEqual(yeo_sum, 1000)
        self.assertIn("Posterior_Hot_Zone", results)
        self.assertIn("Global_Neuronal_Workspace", results)
        
    def test_hybrid_resolution_1014(self):
        labels, meta = build_hybrid_node_metadata(1014)
        self.assertEqual(len(labels), 1014)
        self.assertEqual(len(meta), 1014)
        
        # Check subcortical indices 1000..1013
        for i in range(1000, 1014):
            self.assertEqual(meta[i]["Structure_Type"], "Subcortex")
            self.assertGreater(meta[i]["FSL_Label"], 0)
            
        results = extract_subnetwork_matrices(
            self.sift_path_1014,
            self.length_path_1014,
            self.out_dir,
            resolution=1014,
            include_subcortical_augmented=True
        )
        
        # Verify master labels file was created
        labels_file = os.path.join(self.out_dir, "node_labels_1014.csv")
        self.assertTrue(os.path.exists(labels_file))
        
        # Verify subcortical augmented networks
        self.assertIn("Visual_with_subcortex", results)
        self.assertEqual(results["Visual_with_subcortex"]["num_nodes"], 162 + 14)
        self.assertEqual(results["Somatomotor_with_subcortex"]["num_nodes"], 194 + 14)
        self.assertEqual(results["Posterior_Hot_Zone_with_subcortex"]["num_nodes"], 462 + 14)
        self.assertEqual(results["Global_Neuronal_Workspace_with_subcortex"]["num_nodes"], 347 + 14)
        self.assertIn("Subcortex_Only", results)
        self.assertEqual(results["Subcortex_Only"]["num_nodes"], 14)

if __name__ == "__main__":
    unittest.main()
