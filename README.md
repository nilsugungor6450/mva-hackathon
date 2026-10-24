# MVA Hackathon 2026 – Track 1 (Variant Prediction)

A small, reproducible pipeline that goes from the provided whole-genome VCF to a ranked
candidate list for the *Rare Disease, Real Kid: MVA Hackathon 2026*.

**Result:** candidate compound-heterozygous variants in **BUB1B** (GRCh38):

| Variant | Consequence | Protein | gnomAD max AF | Reads (ref,alt) |
|---|---|---|---|---|
| chr15:40209701 T>G | stop_gained (exon 17/23) | p.Leu737Ter | 9.98e-05 | 21,25 |
| chr15:40220612 T>G | missense (exon 23/23) | p.Asn1002Lys | absent | 15,13 |

The full rationale and limitations are in [`report/nilsugungor6450_track1_report.md`](report/nilsugungor6450_track1_report.md).

## Data
The dataset is controlled-access (`SageBio/mva-hackathon-2026-data` on Hugging Face) and is
**not** included in this repository. Request access on the dataset page, then log in with
`hf auth login`. Only the VCF (+ index) and the clinical phenotype document are used; the FASTQ
files are not needed.

## Environment
Tested on a Google Cloud `e2-standard-4` VM (4 vCPU, 16 GB RAM, 150 GB disk, Ubuntu, x86-64).

```bash
# tools
conda create -n mva -c conda-forge -c bioconda bcftools htslib python=3.11 -y
conda create -n vep -c conda-forge -c bioconda "ensembl-vep>=113" -y   # run used VEP 116
conda activate mva && pip install pandas huggingface_hub docx2txt

# VEP offline cache (~26 GB), release must match the VEP version
mkdir -p ~/vep_cache && cd ~/vep_cache
wget -c https://ftp.ensembl.org/pub/release-116/variation/indexed_vep_cache/homo_sapiens_vep_116_GRCh38.tar.gz
tar xzf homo_sapiens_vep_116_GRCh38.tar.gz
```

VEP is kept in its own environment: installing it together with Python 3.11 made conda
resolve to a very old VEP release (88) with no matching cache.

## Run
```bash
conda activate mva
bash scripts/run_pipeline.sh
```

| Step | Tool | Variants left |
|---|---|---|
| Input VCF | – | 5,012,204 |
| FILTER = PASS | bcftools | 4,740,790 |
| Annotated (decoy/unplaced contigs skipped) | VEP 116 | 4,690,308 |
| IMPACT HIGH or MODERATE | bcftools +split-vep | 11,583 |
| Protein-coding genes | `filter.py` | 10,836 |
| gnomAD max AF < 1% | `filter.py` | 335 |
| Recessive model (hom or ≥2 het in a gene) | `filter.py` | 65 (11 hom + 54 het in 19 genes) |

## Files
- `scripts/run_pipeline.sh` – end-to-end commands
- `scripts/filter.py` – rarity and recessive-model filter
- `scripts/make_submission.py` – writes the predictions CSV
- `submission/` – predictions file submitted to the leaderboard
- `report/` – methods report

## License
Code and reports: CC BY 4.0, as required by the hackathon.
