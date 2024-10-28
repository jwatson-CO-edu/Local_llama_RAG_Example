########## INIT ####################################################################################

### Standard ###
import json, os, base64, io, shutil
from os import environ, path, makedirs, walk
from uuid import uuid4

### Special ###
import fitz, pymupdf
from PIL import Image

########## DATABASE OPS ############################################################################


def copy_pdfs( source_dir, dest_dir, N_add, verbose = 1  ):
    """ Recursively copy PDFs according to the env vars """
    # https://chatgpt.com/share/67156f25-6a98-800d-9c9b-a4b8184cdd46
    # source_dir = environ["_RAG_PDF_SOURCE"]
    # dest_dir   = environ["_RAG_PDF_DESTIN"]
    # verbose    = bool( environ["_RAG_VERBOSE"] )
    # count      = int( environ["_RAG_DOCDB_COUNT" ] )
    # rem        = int( environ["_RAG_DOCDB_REMAIN"] )

    # Create destination directory if it doesn't exist
    if not path.exists( dest_dir ):
        makedirs( dest_dir )

    # Walk through the source directory
    i =  0
    d = 50
    for dirpath, dirnames, filenames in walk( source_dir ):
        dirnames.sort()  # Sort subdirectories in-place
        filenames.sort()  # Sort files in-place
        for file in filenames:
            if file.lower().endswith('.pdf') and (N_add > 0):
                i += 1
                if (not verbose) and (i % d == 0):
                    print( '.', end='', flush = True )
                
                # Full path of the source PDF file
                src_file = path.join( dirpath, file )
                
                # Copy the PDF to the destination directory
                try:
                    destPath = path.join( dest_dir, file )
                    if not path.isfile( destPath ):
                        shutil.copy( src_file, dest_dir )
                        if verbose:
                            print(f"Copied: {src_file}")
                        N_add -= 1
                    else:
                        if verbose:
                            print(f"Exists: {destPath}")
                except Exception as e:
                    print(f"Error copying {src_file}: {e}")
                
    if not verbose:
        print()


    
########## APPLICATION STATE #######################################################################


class RAG_State:
    """ Track state for the workflow """

    @classmethod
    def load_state( cls, path ):
        dct = None
        try:
            with open( path, 'r' ) as f:
                dct = json.load(f)
            if dct is not None:
                return RAG_State(
                    docPaths   = dct['libDocs'],
                    pageImages = dct['pages']
                )
        except FileNotFoundError as e:
            print( f"Could not load {path}!\n{e}" )
            return RAG_State()
        except Exception as e:
            print( f"There was a problem!\n{e}" )
            return None
            
    
    def __init__( self, docPaths = None, pageImages = None ):
        """ Init state """
        self.docPaths : list[str] = list() if (docPaths is None) else docPaths
        self.pgImgs   : dict      = dict() if (pageImages is None) else pageImages

    
    def save_state( self, path ):
        with open( path, 'w' ) as f:
            json.dump( {
                'libDocs' : self.docPaths,
                'pages'   : self.pgImgs,
            }, f, indent = 4 )



########## DATABASE OPS ############################################################################

def safe_str( data ):
    """Filters out invalid UTF-8 characters from a string."""
    return str( data ).encode( 'utf-8', 'ignore' ).decode( 'utf-8' )

def gen_ID():
    """ Generate a unique ID """
    return safe_str( uuid4() )



########## MODELS ##################################################################################

def pull_ollama_model( modelStr ):
    """ Pull a named model from Ollama and store it wherever """
    print( f"About to save '{modelStr}'.\nThis will spew a lot of text on the first run..." )
    os.system( f"ollama pull {modelStr}" )



########## IMAGE DATA ##############################################################################

def pdf_page_to_base64( pdf_path: str, page_number: int ):
    zoom_x       = 1.5  # horizontal zoom
    zoom_y       = 1.5  # vertical zoom
    mat          = pymupdf.Matrix( zoom_x, zoom_y )
    pdf_document = fitz.open( pdf_path )
    page         = pdf_document.load_page(page_number - 1)  # input is one-indexed
    pix          = page.get_pixmap( matrix = mat )
    img          = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer       = io.BytesIO()
    
    img.save( buffer, format="PNG" )

    return base64.b64encode( buffer.getvalue() ).decode("utf-8")



########## SPARE PARTS #############################################################################

def get_page_meta_key( source, page ):
    """ Generate a (probably not) unique page key with useful data that can also be used for sorting """
    return str( source ).split('/')[-1].replace(' ','') + '_' + str( page )