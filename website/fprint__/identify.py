import sys
import os
import subprocess
from API import fp
import json

def identify(file):

    ecb = './echoprint-codegen'

    path = file

    #path = self.master_path

    print 'path: %s' % path

    p = subprocess.Popen([
        ecb, path, '5', '20',
    ], stdout=subprocess.PIPE)
    stdout = p.communicate()        
    d = json.loads(stdout[0])

    # id = 'XYZ'

    #print fp.fp_code_for_track_id('XYZ')

    # sys.exit()
    try:
        code = d[0]['code']
        version = d[0]['metadata']['version']
        duration = d[0]['metadata']['duration']
    except Exception, e:
        print e
        code = None
        version = None
        duration = None

    print code
        
        
    if code:

        #code = fp.decode_code_string(code)
        
        res = fp.best_match_for_query(code, elbow=10)

        print res.message()
        print res.match()
        print res.score
        print res.TRID


        code = fp.decode_code_string(code)
        res = fp.query_fp(code)
        
        print res.results



            

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: %s <audio file>" % sys.argv[0]
        sys.exit(1)
    identify(sys.argv[1])



