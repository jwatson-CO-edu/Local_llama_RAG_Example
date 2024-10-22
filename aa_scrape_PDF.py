from os import environ, path, makedirs, walk
import shutil

def copy_pdfs():
    """ Recursively copy PDFs according to the env vars """
    # https://chatgpt.com/share/67156f25-6a98-800d-9c9b-a4b8184cdd46
    source_dir = environ["_RAG_PDF_SOURCE"]
    dest_dir   = environ["_RAG_PDF_DESTIN"]
    verbose    = bool( environ["_RAG_VERBOSE"] )
    count      = int( environ["_RAG_DOCDB_COUNT" ] )
    rem        = int( environ["_RAG_DOCDB_REMAIN"] )

    

    # Create destination directory if it doesn't exist
    if not path.exists( dest_dir ):
        makedirs( dest_dir )

    # Walk through the source directory
    i =  0
    d = 50
    for dirpath, dirnames, filenames in walk( source_dir ):
        for file in filenames:
            if file.lower().endswith('.pdf'):

                i += 1
                if i <= count:
                    continue
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
                        rem -= 1
                        if rem <= 0:
                            return None
                    else:
                        if verbose:
                            print(f"Exists: {destPath}")
                except Exception as e:
                    print(f"Error copying {src_file}: {e}")
                
    if not verbose:
        print()


