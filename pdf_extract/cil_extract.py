
from pprint import pformat, pprint
import fitz
from fitz.fitz import Document, Page

FILE = "/home/mateo/Downloads/cert CIL - TOMAS PEREZ RESTREPO.pdf"
# %%

def _main():
    # %%
    doc: Document = fitz.open(FILE)

    type(doc)
    # %%
    print( "page_count:", doc.page_count )
    print( "metadata:\n", pformat(doc.metadata) )
    print( "TOC:\n", pformat( doc.get_toc() ) )
    # %%
    page0: Page = doc.load_page(0)

    displayed_text = page0.get_text()
    # %%
    pprint( page0.get_links() )
    # %%
    pprint( list(page0.annots()) )

    pprint( list( page0.widgets() ) )
    # %%
    pix = page0.get_pixmap()
    # %%
    d: dict = page0.get_text("dict")
    print( d.keys() )
    # %%
    print( len(d['blocks']) )

    blks = d['blocks']
    # %%
    blk = blks[0]
    # %%
    print_line_span( blks[0], 0)
    print_line_span( blks[1], 1)
    # %%
    for b_idx, blk in enumerate(blks):
        print_line_span(blk, b_idx)
    # %%


def print_line_span( blk, b_idx ):
    if 'image' in blk:
        print(f'block {b_idx} is image')
        return

    if 'lines' in blk:
        for l_idx, line in enumerate(blk['lines']):
            for s_idx, span in enumerate(line['spans']):
                print(f'block[{b_idx}].line[{l_idx}].span[{s_idx}]: ({span.get("text")})')
    else:
        pprint(blk)
        assert False
    # %%