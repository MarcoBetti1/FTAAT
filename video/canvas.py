"""Logical-coordinate drawing at native output resolution."""
from functools import lru_cache
from PIL import ImageDraw

@lru_cache(maxsize=128)
def resized_font(font,size):
    return font.font_variant(size=size)

class Canvas:
    def __init__(self,image,scale=1):
        self.draw=ImageDraw.Draw(image);self.scale=scale
    def coords(self,value):
        if isinstance(value,(tuple,list)):return tuple(self.coords(v) for v in value)
        return value*self.scale
    def text(self,xy,text,**kw):
        if kw.get('font'):kw['font']=resized_font(kw['font'],round(kw['font'].size*self.scale))
        if 'stroke_width' in kw:kw['stroke_width']=round(kw['stroke_width']*self.scale)
        self.draw.text(self.coords(xy),text,**kw)
    def __getattr__(self,name):
        def call(xy,*args,**kw):
            for k in ('width','radius'):
                if k in kw:kw[k]=round(kw[k]*self.scale)
            return getattr(self.draw,name)(self.coords(xy),*args,**kw)
        return call
