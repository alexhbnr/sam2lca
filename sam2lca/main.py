from sam2lca.sam_pysam import Alignment
from sam2lca.ncbi_to_taxid import get_mapping
from sam2lca.mapfiles import map_db
from sam2lca.sam_ete import compute_lca_multi
from sam2lca import utils
from sam2lca.config import NCBI
from sam2lca.write_alignment import write_bam_tags
from pathlib import Path
import logging


def sam2lca(
    sam, mappings, tree, process, identity, length, conserved, dbdir, output, bam_out
):
    """Performs LCA on SAM/BAM/CRAM alignment file

    Args:
        sam (str): Path to SAM/BAM/CRAM alignment file
        mappings (str): Type of Acc2Tax mapping
        tree (str): Optional taxonomic tree
        process (int): Number of process for parallelization
        identity(float): Minimum identity
        length(int): Minimum alignment length
        dbdir (str): Path to database stroring directory
        output(str): Path to sam2lca output file
        bam_out(bool): Write BAM output file with XT tag for TAXID
    """
    if not output:
        output = utils.output_file(sam)
    utils.check_extension(sam)
    logging.info("Step 1/6: Parsing alignment file")
    al = Alignment(al_file=sam)
    read_dict = al.get_reads(
        process=process, identity=identity, minlength=length, check_conserved=conserved
    )
    acc2tax_db = f"{dbdir}/{map_db[mappings]}"
    p = Path(acc2tax_db)
    if not p.exists():
        logging.info(
            f"\t'{acc2tax_db}' database seems to be missing, I'm creating it for you."
        )
        get_mapping(mappings, dbdir=dbdir, update=False)
    reads_taxid_dict = compute_lca_multi(read_dict, al.refs, acc2tax_db, tree, process)
    taxid_counts, taxid_reads = utils.count_reads_taxid(reads_taxid_dict)
    utils.taxid_to_lineage(taxid_counts, output["sam2lca"])
    if bam_out:
        write_bam_tags(sam, output["bam"], reads_taxid_dict)


def update_database(mappings, dbdir, ncbi):
    """Performs LCA on SAM/BAM/CRAM alignment file

    Args:
        mappings (str): Type of Acc2Tax mapping
        dbdir (str): Path to database stroring directory
        ncbi (bool): Updates NCBI taxonomic tree
    """
    logging.info("Downloading/updating database")
    NCBI
    if ncbi:
        NCBI.update_taxonomy_database()
    get_mapping(mappings, dbdir=dbdir, update=True)
