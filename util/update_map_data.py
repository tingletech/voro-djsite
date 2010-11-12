'''Uses make_map_data.py to create a new institutes list. It then smartly puts
in place. It copies it to the proper directory then checks the corresponding map
web page. If OK, it commits the file to cvs. If not, it overwrites the file with
the cvs version.
'''
import sys
import os
import shutil

DIR_PYTHON_CODE = '/findaid/code/dlxs-fa/oac4/djsite/util/'
DIR_RUN = '/findaid/var/map_data/'
DIR_WEB = '/findaid/code/dlxs-fa/oac4/htdocs/map'

FILE_RESULTS = 'institutes.js'

URL_CHECK = 'http://oac4.cdlib.org/map'

CVS_SERVER = 'cvs.cdlib.org'
CVS_USER = ''
CVS_PASSWD = ''


# a little magic to make the import work
sys.path.insert(0, DIR_PYTHON_CODE)
import make_map_data

def main(argv):
    '''Main controller function'''
    # move to running dir
    os.chdir(DIR_RUN)
    # run make map data
    make_map_data.main(argv)
    # check for result file
    if os.path.getsize(FILE_RESULTS) == 0: # throw os.error if file not exist
        raise os.error(FILE_RESULTS + 'is zero size')

    # move into map directory
    shutil.copy(FILE_RESULTS, DIR_WEB)
    # check map url
    # commit to cvs or recover ealier version
   

if __name__=='__main__':
    main(sys.argv)
