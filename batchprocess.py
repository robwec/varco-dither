import cv2
import numpy as np
from subprocess import call
import os
from callclahe import mainthing, showImage, sshow, recon, fastfloat
import ctypes
#from ctypes import POINTER, c_double, WinDLL
from ctypes import POINTER, c_double, CDLL
import time
from timeit import timeit
import sys

def justpyclaheditherit_csharpwrites(infolder, file, outfolder, pycoloroption, cscoloroption):
    #call("python \"callclahe.py\" \""+infolder+"\\"+file+"\" \""+cscoloroption+"\"", shell=True)
        #1.07 seconds per image gray.
    #mainthing(infolder + "\\" + file, cscoloroption)
        #0.57 seconds per image. Much faster.
    '''
    clahename = infolder+"\\"+file+"_clahe.jpg"
    call("mv \""+clahename+"\" \""+outfolder+"\"", shell=True)
    clahename_out = outfolder+"\\"+file+"_clahe.jpg"
    call("ren \""+clahename_out+"\" \""+file+"\"", shell=True)
    '''
        #removing this move+rename saves ~0.06 seconds per image.
    edited_image = mainthing(infolder + "\\" + file, cscoloroption, writeimage = False)
    filename_aspng = ".".join(file.split(".")[:-1]) + ".png"
    outpath = outfolder + "\\" + filename_aspng
    cv2.imwrite(outpath, edited_image)
    mycommand = "\"cs_dither.exe\" \""+outpath+"\" \""+pycoloroption+"\""
    call(mycommand, shell=True)
    ditheredfilename = ".".join(filename_aspng.split(".")[:-1]) + "_cs.png"
    nextname = ditheredfilename[:-7]+".png"
    '''
    call ("del \""+outfolder+"\\"+file+"\"", shell = True)
    nextname = ditheredfilename[:-7]+".png"
    call ("move /y \""+outfolder+"\\"+ditheredfilename+"\" \""+outfolder+"\\"+nextname+"\"", shell = True)
    call ("convert \""+outfolder+"\\"+nextname+"\" \""+outfolder+"\\"+nextname+"\"", shell = True)
    '''
        #removing this move saves ~0.047 seconds per image.
    call("convert \""+outfolder+"\\"+ditheredfilename+"\" \""+outfolder+"\\"+nextname+"\"", shell = True)
        #why is this samller? it's because imagemagick sets the bit depth to 1. (4 for the color images).
    call("del \""+outfolder+"\\"+ditheredfilename+"\"", shell = True)
    #input()
    return
def justpyclaheditherit_cpp(infolder, file, outfolder, pycoloroption, cscoloroption, mycpplib, size = "receipt"):
    edited_image = mainthing(infolder + "\\" + file, cscoloroption, writeimage = False, fourbysixlabel = (size == "fourbysix"))
    #timeit(lambda: mainthing(infolder + "\\" + file, cscoloroption, writeimage = False), number = 10)
    edited_image_float = fastfloat(edited_image)
    filename_aspng = ".".join(file.split(".")[:-1]) + ".png"
    outpath = outfolder + "\\" + filename_aspng
    dithered_image_float = ctypes_ditherVarcoBreak(edited_image_float, mycpplib)
        #0.280 gray, 0.368 color
    #dithered_image_float = ctypes_ditherVarcoBlue(edited_image_float, mycpplib)
        #0.253 gray, 0.239 color. most processing time is in the auxiliary stuff.
        #is that right? color taking less time then gray? Maybe one of the image-stacking things slowed it down, like the reshape. Whatever.
    dithered_image_int = recon(dithered_image_float)
    cv2.imwrite(outpath, dithered_image_int)
        #can't write 4-bit PNG...
    call("convert \""+outpath+"\" \""+outpath+"\"", shell = True)
        #why is this smaller? it's because imagemagick sets the bit depth to 1. (4 for the color images).
        #0.1 seconds
    return
def ctypes_ditherVarcoBreak(myimage_orig, mylib):
    myimage = myimage_orig.copy()
    imageisgray = (len(myimage.shape) == 2)
    if imageisgray:
        myimage = myimage.reshape((myimage.shape[0], myimage.shape[1], 1))
    for c in range(myimage.shape[2]):
        thischannel = myimage[:,:,c].copy()
        myimage_pointers = [np.ctypeslib.as_ctypes(x) for x in thischannel]
        myimage_pointers = (POINTER(c_double) * thischannel.shape[0])(*myimage_pointers)
        mylib.dither_VarcoBreak(myimage_pointers, ctypes.c_int(thischannel.shape[0]), ctypes.c_int(thischannel.shape[1]), ctypes.c_double(2))
        myimage[:,:,c] = thischannel
    if imageisgray:
        myimage = myimage[:,:,0]
    return myimage
def ctypes_ditherVarcoBlue(myimage_orig, mylib):
    myimage = myimage_orig.copy()
    imageisgray = (len(myimage.shape) == 2)
    if imageisgray:
        myimage = myimage.reshape((myimage.shape[0], myimage.shape[1], 1))
    for c in range(myimage.shape[2]):
        thischannel = myimage[:,:,c].copy()
        myimage_pointers = [np.ctypeslib.as_ctypes(x) for x in thischannel]
        myimage_pointers = (POINTER(c_double) * thischannel.shape[0])(*myimage_pointers)
        mylib.dither_VarcoBlue(myimage_pointers, ctypes.c_int(thischannel.shape[0]), ctypes.c_int(thischannel.shape[1]), ctypes.c_double(2), ctypes.c_bool(False))
        myimage[:,:,c] = thischannel
    if imageisgray:
        myimage = myimage[:,:,0]
    return myimage
#
def justcucuu_gray(infolder, file, outfolder, mycpplib, size = "receipt"):
    justpyclaheditherit_cpp(infolder, file, outfolder, "gray", "graycucuu", mycpplib, size)
    #justpyclaheditherit_csharpwrites(infolder, file, outfolder, "gray", "graycucuu")
def justcuu_gray(infolder, file, outfolder, mycpplib, size = "receipt"):
    justpyclaheditherit_cpp(infolder, file, outfolder, "gray", "graycuu", mycpplib, size)
    #justpyclaheditherit_csharpwrites(infolder, file, outfolder, "gray", "graycuu")
def justcucuu_color(infolder, file, outfolder, mycpplib, size = "receipt"):
    justpyclaheditherit_cpp(infolder, file, outfolder, "color", "colorcucuu", mycpplib, size)
    #justpyclaheditherit_csharpwrites(infolder, file, outfolder, "color", "colorcucuu")
def justcuu_color(infolder, file, outfolder, mycpplib, size = "receipt"):
    justpyclaheditherit_cpp(infolder, file, outfolder, "color", "colorcuu", mycpplib, size)
    #justpyclaheditherit_csharpwrites(infolder, file, outfolder, "color", "colorcuu")
def ditherallstuff_alg(infolder, myfilelist, outfolder, algfunc, mycpplib, size = "receipt"):
    time_start = time.time()
    junko = [algfunc(infolder, x, outfolder, mycpplib, size) for x in myfilelist]
    time_end = time.time()
    print(round(time_end - time_start, 2), "seconds to dither all", len(myfilelist), "images. That's", round((time_end - time_start) / len(myfilelist), 6), "seconds per image!")
#
def keepExtensions(myfilelist, keepextslist):
    return list(filter(lambda x: x.split(".")[-1] in keepextslist, myfilelist))

def main(alg = "cucuu", size = "receipt"):
    infolder = "in_images"
    if not os.path.exists(infolder):
        print("Put your images in the folder called in_images. Then re-run.")
        os.makedirs(infolder, exist_ok = True)
        return
    myfilelist = os.listdir(infolder)
    keepextslist = ["jpg", "JPG", "jpeg", "png"]
    myfilelist = keepExtensions(myfilelist, keepextslist)
    #<>mycpplib = WinDLL("cpp_dither.dll")
    mycpplib = CDLL("./cpp_dither.so")
    if alg == "cuu":
        outfolder_gray_cuu = "out_gray_cuu"
        os.makedirs(outfolder_gray_cuu, exist_ok = True)
        outfolder_color_cuu = "out_color_cuu"
        os.makedirs(outfolder_color_cuu, exist_ok = True)
        ditherallstuff_alg(infolder, myfilelist, outfolder_gray_cuu, justcuu_gray, mycpplib, size)
        ditherallstuff_alg(infolder, myfilelist, outfolder_color_cuu, justcuu_color, mycpplib, size)
    else:
        outfolder_gray_cucuu = "out_gray_cucuu"
        os.makedirs(outfolder_gray_cucuu, exist_ok = True)
        outfolder_color_cucuu = "out_color_cucuu"
        os.makedirs(outfolder_color_cucuu, exist_ok = True)
        ditherallstuff_alg(infolder, myfilelist, outfolder_gray_cucuu, justcucuu_gray, mycpplib, size)
        ditherallstuff_alg(infolder, myfilelist, outfolder_color_cucuu, justcucuu_color, mycpplib, size)
    return

def cmdlinemain_cpp(imagename, colortype = "graycucuu", size = "fourbysix"):
    if size == "fourbysix":
        fourbysix = True
    else:
        fourbysix = False
    clahe_image = mainthing(imagename, colortype, writeimage = False, fourbysixlabel = fourbysix)
    edited_image_float = fastfloat(clahe_image)
    #<>mycpplib = WinDLL("cpp_dither.dll")
    mycpplib = CDLL("./cpp_dither.so")
    dithered_image_float = ctypes_ditherVarcoBreak(edited_image_float, mycpplib)
    dithered_image_int = recon(dithered_image_float)
    suffix = "_dithered"
    if size == "fourbysix":
        suffix += "_label"
    else:
        suffix += "_receipt"
    if colortype[:4] == "gray":
        suffix += "_gray"
    else:
        suffix += "_color"
    outfilename = ".".join(imagename.split(".")[:-1]) + suffix + ".png"
    cv2.imwrite(outfilename, dithered_image_int)
    call("convert -units PixelsPerInch -density 203 \""+outfilename+"\" \""+outfilename+"\"", shell = True)
    return