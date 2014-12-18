#!/usr/bin/env python

import subprocess
print "test"


def runCommand( command  ):
    process = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE )
    output = ''

    for line in process.stdout:
        output += line

    process.wait()
    return output


command = "ls /home/roei"
print runCommand( command )
