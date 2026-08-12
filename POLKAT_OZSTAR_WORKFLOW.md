# POLKAT MeerKAT Imaging Workflow on OzSTAR

Personal notes for running POLKAT with Apptainer on OzSTAR.

---

## 0. Working directory

First move into the directory containing the Measurement Set.

Example:

```bash
cd /fred/oz341/skavya/FRB20121102A_kavya/Imaging/S1
```

---

# Step 1 — Inspect the Measurement Set

Run:

```bash
apptainer exec  --bind /fred:/fred  /fred/oz341/skavya/scripts/containers/polkat-0.2.5.sif python3 tools/ms_info.py <MS_NAME>
```

Replace `<MS_NAME>` with the Measurement Set.

For example:

```bash
apptainer exec --bind /fred:/fred  /fred/oz341/skavya/scripts/containers/polkat-0.2.5.sif python3 tools/ms_info.py S1.ms
```

Check all fields, calibrators, scans, frequencies, etc.

---

# Step 2 — Edit config.py

Open:

```bash
nano config.py
```

Check/change:

- `NODE_CONTAINER_PATH`
- Polarization-angle calibrator name
- Polarization-angle calibrator coordinates
- `BIND = '/fred:/fred'`

Make sure the calibrator information is correct for this observation.

---

# Step 3 — Run 0_GET_INFO

Run:

```bash
apptainer exec  --bind /fred:/fred  /fred/oz341/skavya/scripts/containers/polkat-0.2.5.sif python3 setups/0_GET_INFO.py node
```

This should create:

```text
project_info.json
```

---

# Step 4 — Inspect project_info.json

DO NOT proceed to 1GC immediately.

Inspect:

```bash
cat project_info.json
```

or:

```bash
less project_info.json
```

Check the following carefully:

- Is `project_info.json` present and sensible?
- Are target identities correct?
- Is the primary/bandpass calibrator correct?
- Is the phase calibrator correct?
- Is the polarization-angle calibrator correct?
- Is the detected observing band correct?
- Is the output channel count what I intended?
- Were unexpected scans removed?
- If the data have 2-second integrations, did the short-scan metadata workaround remove or modify genuine science scans?

## Important

Do not continue to 1GC until I can name every field in the Measurement Set and explain why each is:

- target
- primary/bandpass calibrator
- phase calibrator
- polarization-angle calibrator

---

# Step 5 — Generate the 1GC jobs

Run:

```bash
apptainer exec --bind /fred:/fred /fred/oz341/skavya/scripts/containers/polkat-0.2.5.sif python3 setups/1GC.py node
```

Check what submit scripts were generated:

```bash
ls submit_1GC*
```

For example, POLKAT may generate something like:

```text
submit_1GC_jobs.sh
```

---

# Step 6 — Create an OzSTAR Slurm wrapper

Create:

```bash
nano run_1GC.slurm
```

Use:

```bash
#!/bin/bash

#SBATCH --job-name=polkat_1GC
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=240G
#SBATCH --time=1-00:00:00
#SBATCH --output=polkat_1GC_%j.out
#SBATCH --error=polkat_1GC_%j.err

set -e

# --------------------------------------------------
# Working directory
# --------------------------------------------------

cd /fred/oz341/skavya/FRB20121102A_kavya/Imaging/S1

# --------------------------------------------------
# Avoid MKL LD_PRELOAD warning
# --------------------------------------------------

unset LD_PRELOAD

# Let threaded software use the CPUs allocated by Slurm

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

echo "=============================================="
echo "POLKAT 1GC calibration"
echo "Job ID:       $SLURM_JOB_ID"
echo "Node:         $(hostname)"
echo "CPUs:         $SLURM_CPUS_PER_TASK"
echo "Start time:   $(date)"
echo "Directory:    $(pwd)"
echo "=============================================="

# --------------------------------------------------
# Run POLKAT-generated 1GC pipeline
# --------------------------------------------------

bash submit_1GC_jobs.sh

echo
echo "=============================================="
echo "POLKAT 1GC finished"
echo "End time: $(date)"
echo "=============================================="
```

IMPORTANT: check the generated filename first:

```bash
ls submit_1GC*
```

If POLKAT generated a different filename, change:

```bash
bash submit_1GC_jobs.sh
```

accordingly.

---

# Step 7 — Submit the Slurm job

Submit with:

```bash
sbatch run_1GC.slurm
```

Check the queue:

```bash
squeue -u $USER
```

Check output files:

```bash
ls polkat_1GC_*
```

Follow the output:

```bash
tail -f polkat_1GC_<JOBID>.out
```

---

# Important reminder

Before starting each calibration stage:

1. Check the generated configuration.
2. Check field/calibrator identities.
3. Check expected input and output files.
4. Do not blindly submit generated scripts.
5. Keep a record of exactly which POLKAT/container version was used.

Current container:

```text
polkat-0.2.5.sif
```
