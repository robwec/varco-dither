import cv2
import numpy as np
from subprocess import call
#import time
import os
import sys
import math

#########
##usage##
#########
#this is the main function:
    #mainthing(imagename, dithertype = "colorcucuu", writeimage = True)
#run at command,
    #python "callclahe.py" imagename colortype
#valid dither types are:
    #colorcucuu
    #colorcuu
    #graycucuu
    #graycuu
#(Here c stands for CLAHE and u stands for unsharp. Mostly CUCUU looks fine, but for images with fine details or tiny text the CUU algorithm is less likely to obscure the text by sharpening background noise.)

############
##algorithms
def CUCUU(myimage):
    myimage = apply_CLAHE(myimage, 2.0)
    myimage = tweak_saturation(myimage, 0.2)
    myimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
    myimage = apply_CLAHE(myimage, 2.0)
    myimage = tweak_saturation(myimage, 0.2)
    myimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
    myimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
    return myimage
def CUU(myimage):
    myimage = apply_CLAHE(myimage, 2.0)
    myimage = tweak_saturation(myimage, 0.2)
    myimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
    myimage = clip_bottom_percent_black(myimage, -0.4)
    myimage = tweak_gamma(myimage, 0.6)
    myimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
    #myimage = cv2.cvtColor(myimage, cv2.COLOR_BGR2GRAY)
    return myimage
#
def apply_CLAHE(myimage, cliplimit): #values of 0.x-2.0 seem alright. 0, negative, and big values look bad.
    clahe = cv2.createCLAHE(clipLimit = cliplimit, tileGridSize = (8,8))
    if len(myimage.shape) < 3:
        myimage = cv2.cvtColor(myimage, cv2.COLOR_GRAY2BGR)
    lab = cv2.cvtColor(myimage, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(lab)
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    outimage = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return outimage
def tweak_saturation(myimage, sat_jack):
    #clahe = cv2.createCLAHE(clipLimit = cliplimit, tileGridSize = (8,8))
    if len(myimage.shape) < 3:
        myimage = cv2.cvtColor(myimage, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(myimage, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = s.astype(np.int32)
    #s = (s + 70) % 255
    s = np.clip(s*(1.+sat_jack), 0, 255)
    s = s.astype("uint8")
    hsv_out = cv2.merge((h, s, v))
    outimage = cv2.cvtColor(hsv_out, cv2.COLOR_HSV2BGR)
    return outimage
def tweak_gamma(myimage, gamma=1.0):
    invGamma = 1.0/gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0,256)]).astype(np.uint8)
    return cv2.LUT(myimage, table)
def unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.01):
    mygauss = cv2.GaussianBlur(myimage, (radius, radius), sigma)
    unsharp_image = cv2.addWeighted(myimage, 1+gain, mygauss, -gain, 0, mygauss)
    if threshold == 0.:
        unsharp_masked = unsharp_image
    else:
        maskit = np.greater(np.abs(myimage.astype(int) - mygauss.astype(int)), threshold)
        unsharp_masked = np.where(maskit, unsharp_image, myimage)
    return unsharp_masked
''' #nope. different than what I want.
def tweak_brightness_hsv(myimage, bright):
    hsv = cv2.cvtColor(myimage, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = v.astype(int)
    if bright > 0:
        v = np.where(v < bright, bright, v)
    elif bright < 0:
        v = np.where(v > 255 + bright, 255 + bright, v)
    v = v.astype("uint8")
    hsv = cv2.merge((h, s, v))
    outimage = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return outimage
'''
def brightness_contrast(myimage, brightness = 0.0, contrast = 1.0):
    outimage = myimage.astype(float)
    if brightness >= 0:
        outimage = outimage * (255. - brightness) / 255.
        outimage = (outimage - 127.5) * contrast + 127.5
        outimage = np.clip(outimage + brightness, 0, 255)
    else:
        outimage = (outimage - 127.5) * contrast + 127.5
        outimage *= (255 + brightness) / 255.
        outimage = np.clip(outimage, 0, 255)
    outimage = outimage.astype("uint8")
    return outimage
def clip_bottom_percent_black(myimage, minusblackpercent):
    return (myimage*(1. + minusblackpercent) - (minusblackpercent)*255.).astype("uint8")
'''
def clip_top_percent_white(myimage, minuswhitepercent):
    return (myimage*(1. + minuswhitepercent)).astype("uint8")
'''

############################
##black reduction algorithms
#so I have this cheap receipt printer that freezes if there's a horizontal black line.
#these algorithms are a combination of reducing overall image brightness, and then replacing long, thin, black lines with gray. It pretty much always allows the image to print, and doesn't look so bad.

def reduceBlack_forCheapThermalPrinter(myimage, maxallowedblackpercent = 0.72, region_width = 96, region_height = 20):
    """
    create a filter that will reduce the max black percent of the blackest region to under maxallowedblackpercent
    let's say there's 76% black, or 24% white. Then I want to reduce the white proportion to at least 34%. What if I set a floor of 0.34 on the pixel values? Then the sum of the region is necessarily at least 34% white, though at a loss of contrast.
    """
    if len(myimage.shape) > 2:
        print("it's gotta be grayscale")
        return myimage
    maxblackpercent = getMaxBlackPercent(myimage, region_width, region_height)
    if maxblackpercent > maxallowedblackpercent:
        #outimage = clip_bottom_percent_black(myimage, -0.34)
            #nope.
        #outimage = (np.clip(myimage.astype(float) / 255., 0.34, 1.00)*255).astype("uint8")
            #loses lots of details.
        outimage = binarySearch_deblack(myimage, maxallowedblackpercent, region_width, region_height)
            #ok.
    else:
        outimage = myimage
    maxblackpercent_2 = getMaxBlackPercent(outimage, region_width, region_height)
    return outimage
def binarySearch_deblack(myimage, maxallowedblackpercent, region_width, region_height, param = 0.5, min_param = 0., max_param = 1.):
    min_step = 2./255
    propimage = brightness_contrast(myimage, param*255.)
    #propimage = clip_bottom_percent_black(myimage, -param) #same effect as brightness
    #propimage = unsharp_mask(myimage, radius = 9, sigma = 6.0, gain = 0.5, threshold = 0.00)
        #infinite loop!
    newblackpercent = getMaxBlackPercent(propimage, region_width, region_height)
    if newblackpercent <= maxallowedblackpercent and (max_param - min_param < min_step):
        return propimage
    else:
        if newblackpercent > maxallowedblackpercent:
            min_param = param
        else:
            max_param = param
        param = (max_param + min_param) / 2.
        return binarySearch_deblack(myimage, maxallowedblackpercent, region_width, region_height, param, min_param, max_param)
def getMaxBlackPercent(myimage, region_width, region_height):
    maxblackpercent = 0.
    for i in range(math.ceil(myimage.shape[0] / region_height)):
        for j in range(math.ceil(myimage.shape[1] / region_width)):
            thisregion = myimage[region_height*i:region_height*(i+1), region_width*j:region_width*(j+1)]
            whitepercent = np.sum(thisregion.astype(float) / 255.) / (thisregion.shape[0] * thisregion.shape[1])
            blackpercent = 1. - whitepercent
            maxblackpercent = max(maxblackpercent, blackpercent)
            #oprint(blackpercent, maxblackpercent, i, j, thisregion.shape)
    return maxblackpercent
#
def stripBlackLines(myimage, maxallowedblackpercent = 0.66, region_width = 96, region_height = 2):
    for i in range(math.ceil(myimage.shape[0] / region_height)):
        for j in range(math.ceil(myimage.shape[1] / region_width)):
            thisregion = myimage[region_height*i:region_height*(i+1), region_width*j:region_width*(j+1)]
            floatregion = fastfloat(thisregion)
            whitepercent = np.sum(floatregion) / (thisregion.shape[0] * thisregion.shape[1])
            blackpercent = 1. - whitepercent
            #print(blackpercent, maxblackpercent, i, j, thisregion.shape)
            if blackpercent > maxallowedblackpercent:
                thisregion = (np.clip(floatregion, (1 - maxallowedblackpercent), 1.00)*255).astype("uint8")
                myimage[region_height*i:region_height*(i+1), region_width*j:region_width*(j+1)] = thisregion
    return myimage

##################
##image utilities
def showImage(myimage, mypath = "zzztestcoords.jpg", show = True):
    if mypath == None:
        mypath = "zzztestcoords.jpg"
    cv2.imwrite(mypath, myimage)
    if show:
        call(mypath, shell=True)
    return
def sshow(image, name = None, showit = True):
    if type(name) == type(None):
        showImage(recon(image), mypath = None, show = showit)
    else:
        showImage(recon(image), name, showit)
    return
def recon(myimage_float):
    dst = np.empty(myimage_float.shape)
    return cv2.normalize(myimage_float, dst = dst, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX).astype(np.uint8)
def fastfloat(myuint8image):
    return myuint8image * (1/255.)
#
def transparentToWhite(myimage, alpha_thresh=200):
    alpha_channel = myimage[:,:,3]
    mask = (alpha_channel > alpha_thresh).astype("uint8")
    color = myimage[:,:,0:3]
    allwhite = np.tile(255, (myimage.shape[0], myimage.shape[1], 3)).astype("uint8")
    new_img = cv2.bitwise_not(cv2.bitwise_not(color), allwhite, mask)
    return new_img
#
def scale_toFit1200By800(myimage):
    return scale_maxSide_toMinDims(myimage, 800., 1200.)
def scale_maxSide_toMinDims(myimage, mindim_1, mindim_2):
    H, W = myimage.shape[0:2]
    longside = max(H, W)
    shortside = min(H, W)
    longtarget = max(mindim_1, mindim_2)
    shorttarget = min(mindim_1, mindim_2)
    scale_longside_tolongtarget = longtarget / longside
    scale_shortside_toshorttarget = shorttarget / shortside
    scalefactor = min(scale_longside_tolongtarget, scale_shortside_toshorttarget)
    myimage = stretchImage(myimage, scalefactor, scalefactor)
    return myimage
def rotateSoVerticalSideIsLonger(myimage):
    H, W = myimage.shape[0:2]
    if H < W:
        myimage = cv2.rotate(myimage, cv2.ROTATE_90_CLOCKWISE)
    return myimage
#
def scale_minSide_to384(myimage):
    return scale_minSide_toMaxDim(myimage, 384.)
def scale_minSide_toMaxDim(myimage, maxdim):
    scaletomax_x = maxdim/myimage.shape[0]
    scaletomax_y = maxdim/myimage.shape[1]
    scalefactor = max(scaletomax_x, scaletomax_y)
    myimage = stretchImage(myimage, scalefactor, scalefactor)
    return myimage
def stretchImage(myimage, stretch_x, stretch_y):
    myimage = cv2.resize(myimage, None, fx=stretch_x, fy=1, interpolation = getScaleInterp(stretch_x))
    myimage = cv2.resize(myimage, None, fx=1, fy=stretch_y, interpolation = getScaleInterp(stretch_y))
    return myimage
def getScaleInterp(scalefactor):
    if scalefactor < 1:
        return cv2.INTER_AREA
    else:
        return cv2.INTER_LINEAR

######
##main

def mainthing(imagename, colortype = "color", writeimage = True, fourbysixlabel = False):
    myimage = cv2.imread(imagename, cv2.IMREAD_UNCHANGED)
    if len(myimage.shape) == 3 and myimage.shape[2] == 4: #it has alpha
        myimage = transparentToWhite(myimage, alpha_thresh = 200)
    #
    if type(fourbysixlabel) == type(False) and fourbysixlabel == True:
        myimage = scale_toFit1200By800(myimage)
        myimage = rotateSoVerticalSideIsLonger(myimage) #my printer sucks and won't auto-rotate properly, so just rotate to make it portrait.
    else:
        myimage = scale_minSide_to384(myimage)
    #
    #printing program auto-rotates, and images were resized to 384 on the shortest side without rotating, so I might have to rotate the image here so the 384x dimension gets scanned and dithered.
    wide_rotated_image = False
    if (myimage.shape[1] > myimage.shape[0]):
        wide_rotated_image = True
        myimage = np.swapaxes(myimage, 0, 1)
    #
    if colortype == "graycucuu":
        #testo = tweak_saturation(testo, 0.2)
        testo = CUCUU(myimage)
        testo = cv2.cvtColor(testo, cv2.COLOR_BGR2GRAY)
        usingcheapoprinter = (fourbysixlabel == False)
        if usingcheapoprinter:
            testo = reduceBlack_forCheapThermalPrinter(testo, maxallowedblackpercent = 0.72, region_width = 96, region_height = 20)
            testo = stripBlackLines(testo, maxallowedblackpercent = 0.72, region_width = 384, region_height = 2)
        #testo2 = reduceBlack_forCheapThermalPrinter(testo, maxallowedblackpercent = 0.72, region_width = 96, region_height = 4)
        #testo3 = reduceBlack_forCheapThermalPrinter(testo2, maxallowedblackpercent = 0.72, region_width = 384, region_height = 2)
            #nope. brightens the whole image.
        #testo3 = stripBlackLines(testo2, maxallowedblackpercent = 0.66, region_width = 96, region_height = 2)
            #works, but ugly.
    elif colortype == "graycuu":
        testo = CUU(myimage)
        testo = cv2.cvtColor(testo, cv2.COLOR_BGR2GRAY)
        usingcheapoprinter = (fourbysixlabel == False)
        if usingcheapoprinter:
            testo = reduceBlack_forCheapThermalPrinter(testo, maxallowedblackpercent = 0.72, region_width = 96, region_height = 20)
            testo = stripBlackLines(testo, maxallowedblackpercent = 0.72, region_width = 384, region_height = 2)
    elif colortype == "colorcucuu":
        testo = CUCUU(myimage)
    elif colortype == "colorcuu":
        testo = CUU(myimage)
    #
    if wide_rotated_image == True:
        testo = np.swapaxes(testo, 0, 1)
    #
    if writeimage == True:
        #cv2.imwrite(imagename + "_clahe.jpg", testo)
        cv2.imwrite(imagename + "_clahe.png", testo)
            #this looks slightly different than writing as .jpg. Weird. I think .png looks better.
        return
    else:
        return testo

if __name__ == "__main__":
    imagename = sys.argv[1]
    colortype = sys.argv[2]
    if len(sys.argv) > 3:
        fourbysixlabel = sys.argv[3]
    else:
        fourbysixlabel = False
    mainthing(imagename, colortype, writeimage = True, fourbysixlabel = fourbysixlabel)

#######
##BONUS
#mygauss = cv2.GaussianBlur(myimage, (9, 9), 10.0)
#showImage(tweak_gamma(myimage, -100)*420 - mygauss*100)
#vary the second parameter of GaussianBlur for more weirdness. This is caused by uint8 overflow wraparound, so only multiply by ints. No floats!
def trip_sharpred(myimage):
    mygauss = cv2.GaussianBlur(myimage, (9, 9), 10.0)
    return tweak_gamma(myimage, -100)*420 - mygauss*100
def gauss_acidtrip(myimage):
    mygauss = cv2.GaussianBlur(myimage, (9, 9), 6.0)
    trippy = mygauss - myimage
    showImage(trippy)
    return trippy
def custom_acidtrip(myimage):
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100.0)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=0.08)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = gauss_acidtrip(myimage)
    showImage(myimage)
    myimage = tweak_gamma(myimage, gamma=-100)
    showImage(myimage)
    return myimage