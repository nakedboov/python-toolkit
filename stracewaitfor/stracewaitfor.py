#!/usr/bin/env python

import sys
import string
import subprocess
import itertools

def main(argv):
    argc = len(argv)

    if argc != 2:
        print 'Usage: %s <process name>' % (argv[0])
        sys.exit(1)

    process_name = argv[1]
    ps_out = ''

    signs_gen = itertools.cycle('-\|/')
    while True:
        ps_out = subprocess.Popen("ps aux | grep %s | grep -v grep | grep -v %s" % (process_name, argv[0]), stdout=subprocess.PIPE, shell=True).communicate()[0]

        if ps_out == '':
            sys.stdout.write('\r[%s] waiting for process: %s' % (signs_gen.next(), process_name))
            sys.stdout.flush()
        else:
            break

    pid = ''
    ps_out_splitted = string.split(ps_out)
    if len(ps_out_splitted) >= 2:
        pid = ps_out_splitted[1]
		
    if pid == '':
        print '[!] error finding the PID of process %s' % (process_name)
        sys.exit(1)

    strace_proc = subprocess.Popen(['strace', '-r', '-T', '-i', '-ff', '-a', '200', '-p %d' % (int(pid)), '-o', '/tmp/stracewaitfor.log'])
    strace_proc.wait()
 
if __name__ == '__main__':
    main(sys.argv)
sys.exit(0)
