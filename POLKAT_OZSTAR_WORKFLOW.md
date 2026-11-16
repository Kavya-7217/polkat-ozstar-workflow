# Running POLKAT on OzSTAR

These are the commands for taking one MeerKAT Measurement Set (MS) through INFO, referenced calibration (1GC), and imaging and direction-independent phase self-calibration (2GC) with `polkat-0.2.5.sif`. Run the setup commands and submit each Slurm wrapper from the same observation directory.

## 1. Prepare the working directory

For a fresh run, make the observation directory and clone the fork into it. Replace the example paths with the run directory and the absolute path to your MS. If the observation directory already contains the POLKAT checkout, enter it and skip the clone. POLKAT resolves `oxkat/` and `tools/` from the current directory.

```bash
WORK=/fred/oz341/skavya/FRB20121102A_kavya/Imaging/S1
MS_SOURCE=/fred/oz341/path/to/S1.ms
mkdir -p "$WORK"
cd "$WORK"
git clone https://github.com/Kavya-7217/polkat.git .
ln -s "$MS_SOURCE" .
MS=$(basename "$MS_SOURCE")
git rev-parse HEAD
```

Start INFO with a single input ending in `.ms` in this directory. The setup script selects the first match. If the link points outside `/fred` (for example, into `/idia/raw`), the compute node must have access to that filesystem, and the container bind settings must include the target path.

## 2. Inspect the MS and configure calibration

```bash
module load apptainer
SIF=/fred/oz341/skavya/scripts/containers/polkat-0.2.5.sif
apptainer exec --bind /fred:/fred "$SIF" python3 tools/ms_info.py "$MS"
nano oxkat/config.py
```

Check field names, scan intents, band and channel count. In `oxkat/config.py`, verify the container search directory and bind setting.

```python
NODE_CONTAINER_PATH = ['/fred/oz341/skavya/scripts/containers/', CWD]
BIND = '/fred:/fred'
```

Set `POLANG_NAME` to the polarisation-angle calibrator's exact MS field name and `POLANG_DIR` to its direction in the CASA format shown in the config. The fork includes examples for 3C286 and 3C138. If you switch calibrators, check the matching `POLANG_MOD` and `XF_TARGET_POLANG` as well. Record the checkout commit and container filename with the run.

## 3. Generate and run INFO

```bash
apptainer exec --bind /fred:/fred "$SIF" python3 setups/0_GET_INFO.py node
less submit_info_job.sh
```

The setup command writes a shell script. Running that script prepares the working MS and project metadata. In `node` mode the generated commands run within the wrapper’s allocation and invoke `singularity exec`. The wrappers below check for the compatibility command after loading Apptainer and fall back to the Singularity module used in the original workflow. The child Bash enables `pipefail` so a failed command piped through `tee` propagates to Slurm.

Save as `run_info.slurm`.

```bash
#!/bin/bash
#SBATCH --job-name=polkat_info
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=240G
#SBATCH --time=10:00:00
#SBATCH --output=polkat_info_%j.out
#SBATCH --error=polkat_info_%j.err

set -eo pipefail
module load apptainer
command -v singularity >/dev/null || module load singularity
singularity --version
cd "$SLURM_SUBMIT_DIR"
unset LD_PRELOAD
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

echo "POLKAT info | job $SLURM_JOB_ID | $(hostname) | $OMP_NUM_THREADS CPUs"
echo "Started $(date) in $PWD"
bash -eo pipefail submit_info_job.sh
echo "POLKAT info finished $(date)"
```

```bash
sbatch run_info.slurm
```

## 4. Inspect the INFO results

After the INFO job completes successfully, open the metadata.

```bash
less project_info.json
```

Check the master and working MS, target identities, primary/bandpass calibrator, phase calibrator, polarisation-angle calibrator, observing band and intended channel count against the MS inspection. Review any excluded scans. For 2-second integrations, check whether the short-scan metadata workaround affected genuine science scans. Resolve field assignments before starting 1GC.

## 5. Generate and submit 1GC

```bash
apptainer exec --bind /fred:/fred "$SIF" python3 setups/1GC.py node
less submit_1GC_jobs.sh
```

Save as `run_1GC.slurm`.

```bash
#!/bin/bash
#SBATCH --job-name=polkat_1GC
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=240G
#SBATCH --time=1-00:00:00
#SBATCH --output=polkat_1GC_%j.out
#SBATCH --error=polkat_1GC_%j.err

set -eo pipefail
module load apptainer
command -v singularity >/dev/null || module load singularity
singularity --version
cd "$SLURM_SUBMIT_DIR"
unset LD_PRELOAD
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

echo "POLKAT 1GC | job $SLURM_JOB_ID | $(hostname) | $OMP_NUM_THREADS CPUs"
echo "Started $(date) in $PWD"
bash -eo pipefail submit_1GC_jobs.sh
echo "POLKAT 1GC finished $(date)"
```

```bash
sbatch run_1GC.slurm
```

## 6. Generate and submit 2GC

After 1GC completes successfully, check the calibration logs and confirm the target MS files listed in `project_info.json` exist. Generate the 2GC commands.

```bash
apptainer exec --bind /fred:/fred "$SIF" python3 setups/2GC.py node
less submit_2GC_jobs.sh
```

Save as `run_2GC.slurm`.

```bash
#!/bin/bash
#SBATCH --job-name=polkat_2GC
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=240G
#SBATCH --time=1-00:00:00
#SBATCH --output=polkat_2GC_%j.out
#SBATCH --error=polkat_2GC_%j.err

set -eo pipefail
module load apptainer
command -v singularity >/dev/null || module load singularity
singularity --version
cd "$SLURM_SUBMIT_DIR"
unset LD_PRELOAD
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

echo "POLKAT 2GC | job $SLURM_JOB_ID | $(hostname) | $OMP_NUM_THREADS CPUs"
echo "Started $(date) in $PWD"
bash -eo pipefail submit_2GC_jobs.sh
echo "POLKAT 2GC finished $(date)"
```

```bash
sbatch run_2GC.slurm
```

## 7. Check job status and find the images

Use the ID printed by `sbatch` to check the job and its exit status. For example, for 2GC:

```bash
squeue -u "$USER"
JOBID=12345678  # Replace with your job ID
sacct -j "$JOBID" --format=JobID,State,ExitCode,Elapsed
tail -f "polkat_2GC_${JOBID}.out"
```

The wrapper writes its standard output and errors to the observation directory. POLKAT writes individual step logs under `LOGS/`. After imaging, inspect the products under `IMAGES/` in the same working directory.
