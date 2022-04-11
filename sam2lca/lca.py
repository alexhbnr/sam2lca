#!/usr/bin/env python3

from functools import partial
from taxopy import find_lca
from taxopy.core import TaxidError
from tqdm.contrib.concurrent import thread_map
import logging


def taxids_to_lca(read_dict_item, taxo_db, unclassified_taxid=12908):
    """Run LCA on list of TAXID

    Args:
        taxids (frozenset): frozenset of taxids
    """
    read, taxids = read_dict_item
    try:
        taxids.remove(0)
    except KeyError:
        pass
    if len(taxids) == 1:
        ancestor = tuple(taxids)[0].taxid
    elif len(taxids) > 1:
        try:
            ancestor = find_lca(tuple(taxids), taxo_db).taxid
        except TaxidError as e:
            logging.error(e)
            logging.error(taxids)
            ancestor = unclassified_taxid
    else:
        ancestor = unclassified_taxid

    ANCESTORS_DICT.update({read: ancestor})


def compute_lca(read_dict, process, nb_steps, taxo_db):

    global ANCESTORS_DICT
    ANCESTORS_DICT = dict()  # dict(read : lca)

    logging.info(
        f"Step {5 if nb_steps == 7 else 6 }/{nb_steps}: Assigning LCA to reads"
    )

    if process == 1:
        for read in read_dict.items():
            taxids_to_lca(read, taxo_db)

    else:
        get_taxids_partial = partial(taxids_to_lca, taxo_db=taxo_db)
        thread_map(
            get_taxids_partial,
            read_dict.items(),
            chunksize=1,
            max_workers=process,
        )

    return ANCESTORS_DICT
