"""Write the Track 1 predictions CSV.

The top-ranked prediction is the BUB1B compound-heterozygous pair selected by
filter.py and confirmed by manual review (see report). Coordinates are GRCh38.
"""
import csv
import os

PROBAND_ID = "EX2312012"   # sample identifier from the dataset file names
OUT = "submission/nilsugungor6450_vep-recessive-filter.csv"

FIELDS = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1",
          "chrom_2", "pos_2", "ref_2", "alt_2", "epcr", "finding_type", "notes"]

rows = [
    {
        "proband_id": PROBAND_ID,
        "chrom_1": "chr15", "pos_1": 40209701, "ref_1": "T", "alt_1": "G",
        "chrom_2": "chr15", "pos_2": 40220612, "ref_2": "T", "alt_2": "G",
        "epcr": 0.95,
        "finding_type": "primary",
        "notes": "BUB1B candidate compound het: p.Leu737Ter (stop_gained) + p.Asn1002Lys "
                 "(missense, absent from gnomAD). BUB1B is the gene for MVA type 1; "
                 "phase not confirmed (no parental data).",
    },
]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
print("Wrote", OUT)
