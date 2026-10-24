"""Rarity + recessive-model filter on VEP-annotated, protein-altering variants.

Input : results/coding.tsv   (from bcftools +split-vep, see run_pipeline.sh)
Output: results/candidates.tsv
"""
import pandas as pd

MAX_AF_CUTOFF = 0.01          # max population AF across gnomAD exomes/genomes
KNOWN_MVA_GENES = ["BUB1B", "CEP57", "TRIP13"]

cols = ["CHROM", "POS", "REF", "ALT", "SYMBOL", "Consequence", "IMPACT",
        "BIOTYPE", "MAX_AF", "SIFT", "PolyPhen", "GT"]
df = pd.read_csv("results/coding.tsv", sep="\t", names=cols, dtype=str)
print("HIGH/MODERATE impact:", len(df))

# 1) Protein-coding genes with a gene symbol (drops pseudogenes / non-coding transcripts)
df = df[(df["BIOTYPE"] == "protein_coding") & (df["SYMBOL"] != ".")]
print("Protein-coding:", len(df))

# 2) Rarity: absent from gnomAD ('.') or MAX_AF < 1%
df["MAX_AF"] = pd.to_numeric(df["MAX_AF"].replace(".", "0"))
df = df[df["MAX_AF"] < MAX_AF_CUTOFF]
print(f"Rare (MAX_AF < {MAX_AF_CUTOFF}):", len(df))

# 3) Recessive model: homozygous alt, or >=2 rare heterozygous variants in the same gene
gt = df["GT"].str.replace("|", "/", regex=False)
homo = df[gt == "1/1"]
het = df[gt.isin(["0/1", "1/0"])]
counts = het["SYMBOL"].value_counts()
comphet = het[het["SYMBOL"].isin(counts[counts >= 2].index)]
print("Homozygous:", len(homo))
print("Candidate compound-het:", len(comphet), "variants in", comphet["SYMBOL"].nunique(), "genes")

cand = pd.concat([homo.assign(MODEL="homozygous"),
                  comphet.assign(MODEL="compound_het")])
cand = cand.sort_values(["IMPACT", "SYMBOL"])
cand.to_csv("results/candidates.tsv", sep="\t", index=False)
print("Total candidates:", len(cand), "-> results/candidates.tsv")

print("\nRare variants in known MVA genes:")
for g in KNOWN_MVA_GENES:
    print(" ", g, ":", (df["SYMBOL"] == g).sum())
