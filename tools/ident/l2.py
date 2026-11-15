import sys
from PIL import Image, ImageDraw, ImageFont
RAMP = "@%#*+=-:. "
def render(text, font_path, cols, rows, size=300, pad=8, tracking=0):
    f = ImageFont.truetype(font_path, size)
    tmp = Image.new("L",(10,10),255)
    d0 = ImageDraw.Draw(tmp)
    if tracking:
        widths=[d0.textlength(c,font=f) for c in text]
        w=int(sum(widths)+tracking*(len(text)-1))+pad*2
        bb=d0.textbbox((0,0),text,font=f); h=bb[3]-bb[1]+pad*2
        im=Image.new("L",(w,h),255); d=ImageDraw.Draw(im); x=pad
        for c,cw in zip(text,widths):
            d.text((x,pad-bb[1]),c,font=f,fill=0); x+=cw+tracking
    else:
        bb=d0.textbbox((0,0),text,font=f)
        w,h=bb[2]-bb[0]+pad*2,bb[3]-bb[1]+pad*2
        im=Image.new("L",(w,h),255)
        ImageDraw.Draw(im).text((pad-bb[0],pad-bb[1]),text,font=f,fill=0)
    im=im.resize((cols,rows),Image.LANCZOS)
    px=list(im.getdata()); lo,hi=min(px),max(px); sp=max(1,hi-lo)
    out=[]
    for y in range(rows):
        out.append("".join(RAMP[min(9,int((px[y*cols+x]-lo)/sp*10))] for x in range(cols)).rstrip())
    return out
if __name__=="__main__":
    t,fo,c,r = sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
    tr = float(sys.argv[5]) if len(sys.argv)>5 else 0
    print("\n".join(render(t,fo,c,r,tracking=tr)))
