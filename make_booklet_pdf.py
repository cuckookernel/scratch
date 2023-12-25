"""Created on Wed Mar 13 18:12:01 2019

@author: mrestrepo
"""
import math
from typing import List, Tuple

import PyPDF2 as p

#%%
offset_pairs =[
        ( 31 ,  0 ),(  1 , 30 ),
        ( 29 ,  2 ),(  3 , 28 ),
        ( 27 ,  4 ),(  5 , 26 ),
        ( 25 ,  6 ),(  7 , 24 ),
        ( 23 ,  8 ),(  9 , 22 ),
        ( 21 , 10 ),( 11 , 20 ),
        ( 19 , 12 ),( 13 , 18 ),
        ( 17 , 14 ),( 15 , 16 ),
   ]
#%%
def make_offset_pairs( n : int ) -> List[Tuple[int]]:
    """Expect n to be a multiple of 4"""
    assert n % 4 == 0

    offset_pairs = []

    for i in range( 0, n//2 - 1, 2 ) :
        offset_pairs.append( (n - i - 1, i) )
        offset_pairs.append( (i + 1, n - i - 2 )  )

    return offset_pairs
#%%
# make_offset_pairs( 32 )
#%%
def main() :
    #%%
    with open("c:/Users/mrestrepo/downloads/nns.pdf", "rb") as f_in :
        inp = p.PdfFileReader( f_in )
        out = make_new_pdf( inp, start_page=242, last_page=287 )

        print( "done constructing" )

        # It is important that this is written before source is
        # closed. Otherwise, fonts appear garbled...
        with open("c:/Users/mrestrepo/downloads/nns2_no_rot.pdf", "wb") as f_out :
            out.write( f_out )
    #%%

def test() :
    #%%
    f_in =  open("c:/Users/mrestrepo/downloads/nns.pdf", "rb")
    inp = p.PdfFileReader( f_in )
    pg = inp.getPage( 242 )

    #f_in.close()

    #%%

def vert_to_horiz_ratio( media_box ) :
    height = media_box.upperRight[1]
    width  = media_box.upperRight[0]

    return height/width

def transform_page( p, half_page_width, half_page_height ) :
    p.scaleTo( half_page_width, half_page_height )
    return p
    #if out_pi % 2 == 0 :
    #    return p.rotateClockwise( 90 )
    #else :
    #    return p.rotateCounterClockwise( 90 )


#%%
def make_new_pdf( inp : p.PdfFileReader,
                  start_page : int = 0,
                  last_page : int = 31, # included in output
                  out_width : int = 792, out_height : int=612 ) :
    """Letter size  height = 792, widht = 612  (inches * 72)"""
    out = p.PdfFileWriter( )

    n_pages = int( math.ceil ( (last_page + 1 - start_page) / 4.0 ) * 4 )
    end_page = start_page + n_pages # end_page is not included in output
    assert n_pages % 4 == 0, "n_pages should be a multiple of 4"

    target_ratio = vert_to_horiz_ratio( inp.getPage(start_page).mediaBox )
    half_page_width  = out_width // 2
    half_page_height = int( half_page_width * target_ratio )
    assert half_page_height < out_height, "hph %f >=  h %f "

    y_offset = (out_height - half_page_height) // 2

    for i in range( start_page, end_page, 32 ) :

        n_pages = 32 if (i + 32 < end_page) else end_page - i
        print( "i=%d n_pages=%d" % (i, n_pages))
        offset_pairs = make_offset_pairs( n_pages )

        for out_pi, (ofs1, ofs2) in enumerate( offset_pairs ) :

        #out.addPage( inp.getPage(228) )
            pg = out.addBlankPage(width=out_width, height=out_height)
            p1 = inp.getPage( i + ofs1 )
            p1 = transform_page( p1, half_page_width, half_page_height )
            #p1.scaleBy( scale_by )
            pg.mergePage( p1 )

            p2 = inp.getPage( i + ofs2 )
            #p2.scaleBy( scale_by )
            p2 = transform_page( p2, half_page_width, half_page_height )

            pg.mergeTranslatedPage( p2, tx=out_width// 2, ty=y_offset )
            #if out_pi % 2 == 1 :
            #    pg.rotateClockwise( 180 )

            print( i + ofs1, i + ofs2 )

    return out

#f_out.close()
#%%
