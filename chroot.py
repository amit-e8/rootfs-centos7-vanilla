#!/usr/bin/python
import os
import sys
import subprocess
import time


def mount():
    output = subprocess.check_output(["mount"])
    result = []
    for line in output.strip().split("\n"):
        fields = line.split(" ")
        assert fields[1] == "on", "'mount' output line is in wrong format"
        result.append(dict(type=fields[4], path=fields[2]))
    return result


def mountedUnder(dir):
    realPath = os.path.realpath(dir)
    return [m for m in mount() if m['path'].startswith(realPath)]


def umountUnder(dir):
    for i in xrange(100):
        mounts = mountedUnder(dir)
        if len(mounts) == 0:
            print "Successfully unmounted everything"
            return
        result = subprocess.call(["sudo", "umount", mounts[-1]['path']])
        if result != 0:
            print "Unable to umount '%(path)s'" % dict(path=mounts[-1]['path'])
            time.sleep(0.2)
    raise Exception("Unable to unmount even after many retries: %s" % (mounts,))


if len(sys.argv) < 2:
    print "Invalid usage: chroot.py <root dir> [command]"
    sys.exit(2)
root = sys.argv[1]
if os.getuid() != 0:
    print "This script requires root privileges"
    sys.exit(1)
try:
    subprocess.check_call(["mount", "-o", "bind", "/proc", os.path.join(root, "proc")])
    subprocess.check_call("cp -a /dev/* %s/dev/" % root, shell=True)
    subprocess.check_call(["mount", "-o", "bind", "/sys", os.path.join(root, "sys")])
    result = subprocess.call(["chroot", root] + sys.argv[2:])
finally:
    umountUnder(root)
