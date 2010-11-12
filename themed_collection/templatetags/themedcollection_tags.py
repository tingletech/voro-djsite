import math
#from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Library

register = Library()

def calcResizeMin(w_img, h_img, w_min, h_min=None):
    if not h_min:
        h_min = w_min
    ratio_img = h_img/float(w_img)
    ratio_min = h_min/float(w_min)
    if (ratio_img > ratio_min): #image taller
        img_width = w_min
        img_height = int(math.floor(img_width*ratio_img))
    elif (ratio_img < ratio_min):
        img_height = h_min
        img_width = int(math.floor(img_height/ratio_img))
    else:
        img_width = w_min
        img_height = h_min
    return int(img_width), int(img_height)

@register.simple_tag
def imgSizeToMin(w_img, h_img, w_min, h_min=None):
    '''Tag to resize an img to a minimum height/width while retaining the 
    aspect ratio.
    Renders to  width="<XX>px" height="<XX>px"
    '''
    img_width, img_height = calcResizeMin(w_img, h_img, w_min, h_min)
    return ''.join((' width="', str(img_width), 'px" height="', str(img_height), 'px" '))

@register.simple_tag
def mosaicImageStyle(w_img, h_img, w_min, h_min=None):
    '''Creates the style attr for the mosaic images'''
    if not h_min:
        h_min = w_min
    img_width, img_height = calcResizeMin(w_img, h_img, w_min, h_min)
    # now use margin tags to center the image in h_min, w_min
    margin_height = (img_height-h_min)/2.0
    margin_width = (img_width-w_min)/2.0
    margins = ''.join(('margin:-', str(margin_height), 'px -', str(margin_width), 'px;'))
    return ''.join(('style="width: ', str(img_width), 'px; height: ', str(img_height), 'px; ', margins, '"'))
