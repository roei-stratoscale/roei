#!/usr/bin/python

import subprocess
from strato.tests.kvm.mountguestdisk import MountGuestDisk
import sys
import os

dest = None
assert len( sys.argv ) <= 2
if len( sys.argv ) == 2 and ( '/' in sys.argv[ 1 ] or '.' in sys.argv[ 1 ] ):
	imageFile = sys.argv[ 1 ]
else:
	flavor = '-%s-' % sys.argv[ 1 ] if len( sys.argv ) == 2 else '-'
	imageFile = '/home/vm_template/strato%svanilla.qcow2' % flavor
try:
    with MountGuestDisk( imageFile ) as mount:
        dest = mount.destination()
        print 'Mounting: %s' % dest
        subprocess.call( [ 'bash' ], cwd = dest )
finally:
    if dest:
        os.rmdir( dest )
