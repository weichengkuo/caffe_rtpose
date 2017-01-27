#!/usr/bin/python

import os, tempfile, time, shutil
import pdb

FFMPEG_STATIC = "./ffmpeg/ffmpeg"

def isLocked(fn):
    if os.path.exists(fn):
        return True
    try:
        os.mkdir(fn)
        return False
    except:
        return True

def unlock(fn):
    os.rmdir(fn)

def uzVideo(vidSrc):
    frameFolder = tempfile.mkdtemp()
    ffmpegBase = "%s -hide_banner -loglevel panic " % FFMPEG_STATIC
    com = "%s -i %s -q 1 %s/frame%%06d.jpg" % (ffmpegBase, vidSrc, frameFolder)
    os.system(com)
    return frameFolder

def uzVideoSamp(vidSrc,nFr):
    #hacky, but simple and effective
    frameFolder = uzVideo(vidSrc)
    jpgs = os.listdir(frameFolder); jpgs.sort()
    for ji,j in enumerate(jpgs):
        if (ji+1) % nFr != 1:
            os.remove(frameFolder+"/"+j)
    return frameFolder


def closeVideo(frameFolder):
    # print "About to nuke %s" % frameFolder
    if not frameFolder.startswith("/tmp/"):
        print "Doesn't look right"
        raw_input()
    shutil.rmtree(frameFolder)


