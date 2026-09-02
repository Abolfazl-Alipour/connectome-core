# Troubleshooting & Performance Guide

## 1. Disk Space Management & Scratch Cleanup
High-throughput tractography with 10M streamlines requires temporary scratch space during processing (~15GB per subject for intermediate 5TT, FOD, and raw tck files).

* The pipeline script isolates all intermediate outputs into `tmp_work_${SUBJECT_ID}/`.
* A guaranteed `trap ... EXIT` cleanup handler automatically removes all scratch files upon subject completion or error.
* Never run tractography directly inside long-term archive directories.

## 2. Multi-Core CPU Allocation
* **Recommended Configuration**: Run 1 subject at a time with 16–30 CPU cores (`-nthreads 24` or `-nthreads 30`).
* Running multiple subjects simultaneously with low thread counts increases RAM competition and disk I/O bottlenecks without speeding up execution.

## 3. Re-running Group Analytics
Group analytics (`generate_group_consensus.py`, `generate_score.py`, `generate_degree_preserved.py`) run in under 30 seconds for the entire 169-subject cohort.
To re-run the entire pipeline from scratch:
```bash
bash scripts/run_group_analytics.sh
```
