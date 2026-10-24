# MVA Hackathon 2026 – Track 1 Methods Report

**Participant:** nilsugungor6450 (individual)
**Code:** https://github.com/nilsugungor6450/mva-hackathon
**Proband:** EX2312012 · **Reference:** GRCh38

## 1. Summary
Starting from the provided whole-genome VCF, a transparent filtering pipeline (quality →
functional annotation → rarity → recessive inheritance model → phenotype-guided review) reduced
~5.0 million variants to 65 candidates. Among them, **BUB1B** – the gene for mosaic variegated
aneuploidy type 1 (MVA1) – carries two rare heterozygous variants, consistent with
compound heterozygosity:

| | Variant 1 | Variant 2 |
|---|---|---|
| Position | chr15:40209701 T>G | chr15:40220612 T>G |
| Transcript | ENST00000287598 (canonical) | ENST00000287598 |
| Consequence | stop_gained, exon 17/23 | missense, exon 23/23 |
| Protein | p.Leu737Ter | p.Asn1002Lys |
| dbSNP | rs759242053 | – |
| gnomAD max AF | 9.98 × 10⁻⁵ | absent |
| SIFT / PolyPhen | n/a | deleterious (0.01) / probably damaging (0.997) |
| Genotype, reads ref/alt, DP, GQ | 0/1, 21/25, 46, 99 | 0/1, 15/13, 28, 99 |

This pair is submitted as the single primary prediction (EPCR 0.95).

## 2. Phenotype
The clinical document lists eight HPO terms: short stature (HP:0004322), failure to thrive
(HP:0001508), skeletal muscle atrophy (HP:0003202), premature birth (HP:0001622), small for
gestational age (HP:0001518), parental recurrent spontaneous abortion (HP:0200067),
rhabdomyosarcoma (HP:0002859) and nephrocalcinosis (HP:0000121). Following the organisers'
guidance, the constellation (cancer predisposition, pre- and postnatal growth restriction, renal
involvement, adverse perinatal history, reproductive loss in the family) was read as a whole and
points to a chromosomal-instability / mitotic-checkpoint disorder. This informed the recessive
model and the gene-level review; the HPO terms were not used for automated scoring in this
version.

## 3. Methods
All commands are in `scripts/run_pipeline.sh`.

1. **Quality filter** – `bcftools view -f PASS`: 5,012,204 → 4,740,790 variants. The failing
   variants were mostly flagged for low mapping quality (MQ40) in repetitive regions.
2. **Annotation** – Ensembl VEP 116, offline cache GRCh38, options `--pick --canonical --symbol
   --af_gnomade --af_gnomadg --max_af --sift b --polyphen b`. 4,690,308 variants were annotated;
   the remainder lie on decoy/unplaced contigs with no gene models.
3. **Protein-altering variants** – VEP IMPACT HIGH (stop, frameshift, splice site) or MODERATE
   (missense, in-frame indel): 11,583. Restricting to protein-coding biotypes removes pseudogenes
   and non-coding transcripts: 10,836.
4. **Rarity** – max population AF across gnomAD exomes and genomes < 1% (variants absent from
   gnomAD kept): 335. The 1% threshold is permissive enough for recessive carrier frequencies.
5. **Inheritance model** – MVA is autosomal recessive, so only genes that could be biallelically
   affected were kept: homozygous alternate variants (11) or ≥2 rare heterozygous variants in the
   same gene (54 variants in 19 genes) → 65 candidates.
6. **Review** – candidates were reviewed against the phenotype and the known MVA genes
   (BUB1B, CEP57, TRIP13). BUB1B was the only known MVA gene with rare variants (2); CEP57 and
   TRIP13 had none.

## 4. Interpretation of the BUB1B pair
- **Gene–phenotype fit.** BUB1B encodes BUBR1, a core component of the spindle assembly
  checkpoint that prevents chromosome mis-segregation. Biallelic BUB1B variants cause MVA1, in
  which growth restriction and childhood cancers, including rhabdomyosarcoma, are reported –
  matching the proband's presentation.
- **Variant 1 (p.Leu737Ter)** introduces a premature stop codon in exon 17 of 23, i.e. not in the
  last exon, so the transcript is expected to undergo nonsense-mediated decay (loss of function).
  It is very rare in gnomAD.
- **Variant 2 (p.Asn1002Lys)** is absent from gnomAD and predicted damaging by both SIFT and
  PolyPhen. It lies in the C-terminal region encoded by the last exon (the BUBR1 kinase-like
  domain region).
- **Mechanism.** One null allele combined with one hypomorphic missense allele is a typical
  configuration for MVA1: complete loss of both alleles is generally not compatible with life,
  while reduced BUBR1 dosage causes checkpoint failure and mosaic aneuploidy.
- **Data quality.** Both calls are PASS with allele balances consistent with heterozygosity
  (25/46 and 13/28 alternate reads) and GQ 99, arguing against sequencing artefacts.

## 5. Limitations
- **Phase is not confirmed.** Without parental data, I cannot show that the two variants are on
  different chromosomes (in trans). The ~11 kb distance is too large for read-based phasing with
  short reads. Parental testing or long-read sequencing would resolve this.
- **Missense effect is predicted, not measured.** Functional evidence would be needed.
- **Variant classes not assessed:** structural variants/CNVs, low-level mosaic variants, deep
  intronic and non-canonical splice variants (no SpliceAI), and variants on non-canonical
  transcripts (`--pick`). Raw FASTQ files were not re-analysed.
- **No automated phenotype ranking.** HPO terms guided manual review; running a
  phenotype-driven prioritiser (e.g. Exomiser) on the 65 candidates would make the ranking
  fully automated and is the main planned extension.
- The 1% AF threshold and the "≥2 hets per gene" rule may admit false positives (e.g. two
  variants in cis), which is why manual review is part of the pipeline.

## 6. Scalability
The pipeline uses only standard, open tools (bcftools, Ensembl VEP, pandas), runs on a modest
cloud VM (4 vCPU, 16 GB RAM; VEP annotation of the whole genome took ~15 minutes), and needs no
case-specific code apart from the gene list used in the review step. It can be applied unchanged
to other single-sample WGS VCFs on GRCh38.

## 7. Use of AI assistance
An AI assistant was used for guidance on tooling, command construction, and drafting this report:
**Anthropic claude.ai, Claude Opus 5.5, Claude Pro plan (consumer terms), "Help improve Claude"
model-training setting turned off.** Excerpts of the clinical phenotype document and individual
VCF/annotation lines were pasted into the chat during the analysis; the VCF and FASTQ files were
not uploaded. All analysis was run on my own cloud VM and all results were checked by me.
