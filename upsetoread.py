import re
import os.path

def print_manifest(manifiest, gap=0):
    with open(manifest) as f:
        line = f.readlines()
        line = line[1:]
        for i in xrange(0, len(line), 2):
            #hash_val, originURL = line[i], line[i+1]
            #print hash_val + ' => ' + originURL 
            
            hash_val = re.search('hash: (.*)', line[i]).group(1) 
            originURL = re.search('.*Stratoscale/(.*)[.]git', line[i+1]).group(1)
            print ' '*gap + hash_val + ' => ' + originURL
            filename = 'work/' + originURL + '/' + 'upseto.manifest'
            if os.path.isfile(filename):
                print "trying to print " + filename
                print_manifest(filename, gap+2)
            else:
                print "No such file: " + filename
            #print_manifest('work/' + originURL + '/' + 'upseto.manifest', gap + 2)
            

#print line[i], line[i+1]
	# = re.search('(?<=abc)def', 'abcdef')
        #m =m = re.search('hash: (.*)', content) re.search('hash: (.*)', content)
#hash: 227e7a8f4040e60a9c0109dcf90e1d66d7cc2f11
    #originURL: https://github.com/Stratoscale/northbound.git



manifest = 'upseto.manifest'
manifest = 'work/dc/' + manifest
print_manifest(manifest)
