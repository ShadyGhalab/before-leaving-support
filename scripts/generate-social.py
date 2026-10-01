#!/usr/bin/env python3
"""Rebuild the 1200x630 social image from the supplied ReadyKin artwork.
Optional maintainer utility: python -m pip install Pillow. Normal builds need no Pillow.
Only rendered artwork is exported; font files are never copied into the project.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]

def font(size: int, bold: bool=False):
    names = (['DejaVuSans-Bold.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if bold else ['DejaVuSans.ttf','/System/Library/Fonts/Supplemental/Arial.ttf'])
    for name in names:
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default(size=size)

def main():
    canvas=Image.new('RGB',(1200,630),'#fbfaf7');d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((811,30,1170,600),radius=40,fill='#e9dff4')
    d.ellipse((830,400,1280,820),fill='#e0efa6')
    icon=Image.open(ROOT/'images/readykin/brand-icon-220.webp').convert('RGB').resize((76,76),Image.Resampling.LANCZOS)
    mask=Image.new('L',icon.size,0);ImageDraw.Draw(mask).rounded_rectangle((0,0,75,75),radius=20,fill=255)
    canvas.paste(icon,(54,44),mask)
    d.text((148,47),'ReadyKin',font=font(44,True),fill='#2d1736')
    d.text((150,103),'Formerly Before Leaving',font=font(17),fill='#685b72')
    d.text((54,177),'A little more ready.',font=font(57,True),fill='#2d1736')
    d.text((54,260),'For your trip.',font=font(48),fill='#2d1736')
    d.text((54,325),'For your everyday.',font=font(48),fill='#2d1736')
    d.rounded_rectangle((54,430,265,474),radius=15,fill='#e2eeaa')
    d.text((72,439),'Smart reminders',font=font(20,True),fill='#2d1736')
    d.rounded_rectangle((280,430,458,474),radius=15,fill='#eee4f7')
    d.text((298,439),'Packing lists',font=font(20,True),fill='#2d1736')
    d.rounded_rectangle((473,430,652,474),radius=15,fill='#eee4f7')
    d.text((491,439),'Shared trips',font=font(20,True),fill='#2d1736')
    d.text((54,551),'beforeleaving.app',font=font(22),fill='#62526c')
    shot=Image.open(ROOT/'images/readykin/story-travel.webp').convert('RGB')
    shot=ImageOps.contain(shot,(258,536),Image.Resampling.LANCZOS)
    canvas.paste(shot,(862+(258-shot.width)//2,48))
    out=ROOT/'images/social/readykin-social.jpg';out.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(out,quality=90,optimize=True,progressive=True)
    print(f'Wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)')
if __name__=='__main__':main()
