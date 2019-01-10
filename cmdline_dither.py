from batchprocess import cmdlinemain_cpp
import sys
import os
import re

def getUnditheredFilesInDir():
    filelist = os.listdir()
    filelist = list(filter(lambda x: x.split(".")[-1] in ["jpg", "jpeg", "JPG", "png"], filelist))
    ditherednames = list(filter(lambda x: "_dithered_" in x, filelist))
    orignames = [getOrigName(x) for x in ditherednames]
    filelist = list(filter(lambda x: "_dithered_" not in x, filelist))
    filelist = list(filter(lambda x: ".".join(x.split(".")[:-1]) not in orignames, filelist))
    return filelist
def getOrigName(ditheredname):
    return re.sub("_dithered_.*?$", "", ".".join(ditheredname.split(".")[:-1]))

if __name__ == "__main__":
    #cmdlinemain_cpp(sys.argv[1], colortype = sys.argv[2], size = sys.argv[3])
    files = getUnditheredFilesInDir()
    _ = [cmdlinemain_cpp(x, colortype = sys.argv[1], size = sys.argv[2]) for x in files]
