#!/usr/bin/env bash
# MVA Hackathon 2026 - Track 1: variant prioritisation pipeline
#
# Reproduces results/candidates.tsv and the submission CSV from the hackathon VCF.
#
# Requirements (see README.md):
#   - conda env "mva": bcftools, htslib, python 3.11, pandas, huggingface_hub
#   - conda env "vep": ensembl-vep (run used release 116)
#   - VEP indexed cache, release 116, GRCh38, unpacked in ~/vep_cache
#
# Run from the repository root with the "mva" env active:
#   conda activate mva && bash scripts/run_pipeline.sh
set -euo pipefail

VCF=data/WGS_EX2312012_HGWCNDSX7.vcf.gz
VEP_CACHE=${VEP_CACHE:-$HOME/vep_cache}
mkdir -p data results

# 0) Download input data (gated dataset; access must be approved first).
#    Raw FASTQ files are not used: the provided VCF is the starting point.
if [ ! -f "$VCF" ]; then
  hf download SageBio/mva-hackathon-2026-data \
    WGS_EX2312012_HGWCNDSX7.vcf.gz WGS_EX2312012_HGWCNDSX7.vcf.gz.tbi \
    Challenge_Clinical_Phenotype_1.docx \
    --repo-type dataset --local-dir ./data
fi

# 1) Phenotype: extract HPO terms from the clinical document
pip install -q docx2txt
docx2txt data/Challenge_Clinical_Phenotype_1.docx > data/phenotype.txt
grep -o "HP:[0-9]\{7\}" data/phenotype.txt | sort -u > data/hpo.txt

# 2) Quality filter: keep only variants with FILTER=PASS
bcftools view -f PASS -Oz -o data/pass.vcf.gz "$VCF"
bcftools index -t data/pass.vcf.gz

# 3) Functional annotation with Ensembl VEP (offline cache, GRCh38)
#    Variants on decoy/unplaced contigs are skipped by VEP (no annotation).
conda run -n vep vep -i data/pass.vcf.gz -o results/vep.vcf.gz \
  --cache --offline --dir_cache "$VEP_CACHE" --assembly GRCh38 --cache_version 116 \
  --vcf --symbol --canonical --pick --variant_class \
  --af_gnomade --af_gnomadg --max_af \
  --sift b --polyphen b \
  --fork 4 --compress_output bgzip \
  --stats_file results/vep_stats.html \
  --force_overwrite
bcftools index -t results/vep.vcf.gz

# 4) Keep protein-altering variants (VEP IMPACT = HIGH or MODERATE) as a flat table
bcftools +split-vep results/vep.vcf.gz \
  -i 'IMPACT="HIGH" || IMPACT="MODERATE"' \
  -f '%CHROM\t%POS\t%REF\t%ALT\t%SYMBOL\t%Consequence\t%IMPACT\t%BIOTYPE\t%MAX_AF\t%SIFT\t%PolyPhen[\t%GT]\n' \
  > results/coding.tsv

# 5) Rarity + recessive inheritance model -> results/candidates.tsv
python scripts/filter.py

# 6) Detail view of the top candidate (consequence, protein change, read support)
bcftools +split-vep results/vep.vcf.gz -r 15:40209701,15:40220612 \
  -f '%POS\t%Consequence\t%Feature\t%EXON\t%Protein_position\t%Amino_acids\t%Existing_variation[\t%GT\t%AD\t%DP\t%GQ]\n'

# 7) Submission file
python scripts/make_submission.py
