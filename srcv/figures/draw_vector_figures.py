from pathlib import Path
from xml.sax.saxutils import escape
import math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

import argparse
parser=argparse.ArgumentParser(description='Generate editable SRCV vector figures as SVG and PDF.')
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
OUT=parser.parse_args().output
OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
INK='#172B4D';MUTED='#52647B';LINE='#C8D2DF'
BLUE='#1761A0';PURPLE='#6646AB';ORANGE='#A86117';GREEN='#25704E'

class Figure:
 def __init__(self,name,w,h,title):
  self.name=name;self.w=w;self.h=h;self.items=[]
  self.c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(w,h))
  self.c.setTitle(title);self.c.setAuthor('Zixuan Wang; Guangyao Dou')
  self.items.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">Vector diagram. All text, boxes, and arrows remain sharp at any scale.</desc>')
  self.rect(0,0,w,h,'#FFFFFF',None,0)
 def rect(self,x,y,w,h,fill='#FFFFFF',stroke=LINE,r=12,lw=1.6):
  self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}"/>')
  c=self.c;c.setLineWidth(lw)
  if fill:c.setFillColor(HexColor(fill))
  if stroke:c.setStrokeColor(HexColor(stroke))
  c.roundRect(x,self.h-y-h,w,h,r,fill=bool(fill),stroke=bool(stroke))
 def text(self,x,y,s,size=20,color=INK,bold=False,anchor='start'):
  self.items.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(s)}</text>')
  c=self.c;c.setFillColor(HexColor(color));c.setFont('DVB' if bold else 'DV',size)
  {'start':c.drawString,'middle':c.drawCentredString,'end':c.drawRightString}[anchor](x,self.h-y,s)
 def lines(self,x,y,lines,size=18,color=INK,bold=False,anchor='start',leading=None):
  for i,s in enumerate(lines):self.text(x,y+i*(leading or size*1.3),s,size,color,bold,anchor)
 def poly(self,points,fill=None,stroke=LINE,lw=1.7,closed=False,dash=False):
  p=' '.join(f'{x},{y}' for x,y in points);tag='polygon' if closed else 'polyline'
  self.items.append(f'<{tag} points="{p}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}" stroke-linecap="round" stroke-linejoin="round"'+(' stroke-dasharray="6 5"' if dash else '')+'/>')
  c=self.c;c.saveState();c.setLineWidth(lw)
  if dash:c.setDash(6,5)
  if stroke:c.setStrokeColor(HexColor(stroke))
  if fill:c.setFillColor(HexColor(fill))
  path=c.beginPath();path.moveTo(points[0][0],self.h-points[0][1])
  for x,y in points[1:]:path.lineTo(x,self.h-y)
  if closed:path.close()
  c.drawPath(path,stroke=bool(stroke),fill=bool(fill));c.restoreState()
 def arrow(self,points,color=INK,lw=2.3,dash=False):
  self.poly(points,stroke=color,lw=lw,dash=dash)
  x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px);d=8
  self.poly([(x-d*math.cos(a-.5),y-d*math.sin(a-.5)),(x,y),(x-d*math.cos(a+.5),y-d*math.sin(a+.5))],stroke=color,lw=lw)
 def badge(self,x,y,w,label,color):
  self.rect(x,y,w,29,color,None,7);self.text(x+12,y+20,label,15,'#FFFFFF',True)
 def save(self):
  self.c.showPage();self.c.save();(OUT/(self.name+'.svg')).write_text('\n'.join(self.items)+ '\n</svg>')

f=Figure('SRCV_vector',1200,720,'SRCV Harness')
f.text(600,43,'SRCV Harness',32,bold=True,anchor='middle')
# Main reasoning path.
f.rect(24,111,244,108,'#F6F8FB',LINE)
f.lines(146,155,['Task / Query','x'],23,bold=True,anchor='middle',leading=33)
f.rect(330,84,540,178,'#F4F0FA',PURPLE)
f.badge(348,101,354,'Main context  Cₜ = [x, Eₜ, Hₜ]',PURPLE)
f.text(356,174,'Solver Agent',28,bold=True)
f.lines(356,210,['Plan, use tools, and reason over evidence.'],20)
f.rect(932,84,244,178,'#F6F8FB',LINE)
f.text(1054,116,'Candidate answer  ŷₜ',18,bold=True,anchor='middle')
for y,label,color in [(133,'Evidence  Eₜ','#E7F1FB'),(173,'Reasoning','#FCF0DE'),(213,'Answer','#E6F4EC')]:
 f.rect(947,y,214,31,color,None,5);f.text(961,y+22,label,17,bold=True)
f.arrow([(268,166),(330,166)])
f.arrow([(870,166),(932,166)])
# Reader request and evidence return use separate routes.
f.arrow([(386,262),(386,294),(104,294),(104,390)],BLUE)
f.arrow([(314,390),(314,326),(446,326),(446,262)],BLUE)
f.text(88,350,'Query',18,BLUE,True,anchor='end')
f.lines(326,353,['Selected','evidence Eₜ'],17,BLUE,True)
# Compaction branch.
f.arrow([(568,262),(568,390)],ORANGE)
f.arrow([(632,390),(632,262)],ORANGE)
f.lines(554,345,['Compaction','request'],17,ORANGE,True,'end')
f.lines(646,345,['Compacted','context'],17,ORANGE,True)
# Independent verification.
f.arrow([(752,262),(752,326),(886,326),(886,390)],GREEN)
f.arrow([(1100,390),(1100,294),(812,294),(812,262)],GREEN)
f.text(875,360,'ŷₜ + Eₜ',19,GREEN,True,'end')
f.lines(1110,342,['Feedback','fₜ'],15,GREEN,True)

def role(x,w,color,fill,badge,title,desc):
 f.rect(x,390,w,280,fill,color)
 f.badge(x+16,405,215 if badge=='Independent context' else 145,badge,color)
 f.text(x+20,470,title,24,bold=True)
 f.text(x+20,499,desc,17)
role(24,360,BLUE,'#F0F7FD','Context branch','Reader Agent','Retrieve and filter evidence.')
f.rect(44,521,132,93,'#FFFFFF',LINE,7);f.lines(110,546,['Candidate','evidence'],16,bold=True,anchor='middle',leading=22)
f.lines(110,589,['statute /','web docs'],14,MUTED,anchor='middle',leading=18)
f.arrow([(187,567),(210,567)],BLUE)
f.rect(222,521,142,93,'#FFFFFF',BLUE,7);f.lines(293,546,['Selected','evidence'],16,bold=True,anchor='middle',leading=22)
f.lines(293,589,['excerpts +','citations'],14,MUTED,anchor='middle',leading=18)
f.text(204,648,'Only selected evidence enters solver.',15,BLUE,True,'middle')
role(420,360,ORANGE,'#FFF7EA','Context branch','Compaction Agent','Compress and preserve key state.')
f.rect(440,521,132,93,'#FFFFFF',LINE,7);f.lines(506,557,['Trajectory','history'],18,bold=True,anchor='middle',leading=26)
f.arrow([(583,567),(606,567)],ORANGE)
f.rect(618,521,142,93,'#FFFFFF',ORANGE,7);f.lines(689,557,['Compacted','context'],18,bold=True,anchor='middle',leading=26)
f.text(600,648,'Rebuild the main context.',16,ORANGE,True,'middle')
role(816,360,GREEN,'#F0F8F3','Independent context','Verifier Agent','Check the answer against evidence.')
f.rect(836,521,184,93,'#FFFFFF',LINE,7);f.text(848,545,'Rubrics',16,bold=True)
for i,label in enumerate(['Evidence coverage','Relevance','Grounded reasoning']):
 y=563+i*20;f.rect(848,y-10,8,8,'#FFFFFF',GREEN,1,1.1);f.text(864,y,label,13.5)
f.arrow([(1030,567),(1046,567)],GREEN)
f.rect(1056,521,100,93,'#FFFFFF',GREEN,7);f.lines(1106,547,['Verification','feedback','fₜ'],13.8,bold=True,anchor='middle',leading=24)
f.text(996,648,'Return feedback for revision.',16,GREEN,True,'middle')
f.text(600,704,'Read evidence, manage context, verify, and iteratively refine the answer.',18,bold=True,anchor='middle')
f.save()

f=Figure('Reader_vector',1200,600,'Selective Reader')
f.text(600,44,'Selective Reader',32,bold=True,anchor='middle')
f.rect(24,83,240,471,'#F0F7FD',BLUE)
f.text(144,126,'Retrieval',25,bold=True,anchor='middle')
# Corpus icon, pure vector.
for dx,dy in [(0,0),(10,7),(20,14)]:
 f.rect(82+dx,158+dy,105,62,'#FFFFFF','#93ABC6',5)
for y in [189,201,213]:f.poly([(118,y),(184,y)],stroke='#93ABC6',lw=3)
f.text(144,263,'Document corpus',19,bold=True,anchor='middle')
f.text(144,289,'100k+ documents',17,MUTED,anchor='middle')
f.arrow([(144,305),(144,332)],BLUE)
f.rect(68,344,152,44,'#FFFFFF',BLUE,8);f.text(144,373,'Search',19,bold=True,anchor='middle')
f.arrow([(144,400),(144,428)],BLUE)
f.rect(43,440,202,83,'#FFFFFF',LINE,7);f.text(144,471,'Top-k documents',18,bold=True,anchor='middle');f.lines(144,496,['Preview: first 512 tokens'],14.5,MUTED,anchor='middle')

f.rect(300,83,600,471,'#F7F4FB',PURPLE)
f.text(322,125,'Selective Reader',24,bold=True)
f.rect(323,150,554,44,'#FFFFFF','#CCBFDF',8)
f.text(600,179,'Task  |  Solver state  |  Query',18,bold=True,anchor='middle')
f.arrow([(600,194),(600,220)])
f.rect(449,226,302,65,'#EBF4FC',BLUE,9)
f.text(600,253,'Scan prefix',21,bold=True,anchor='middle')
f.text(600,278,'First 512 tokens',17,MUTED,anchor='middle')
f.arrow([(600,291),(600,310)])
f.poly([(600,310),(685,356),(600,402),(515,356)],'#FFF2D9','#BB8D2B',1.6,True)
f.lines(600,350,['Reader','decision'],17,bold=True,anchor='middle',leading=23)
f.arrow([(515,356),(391,356),(391,453)],'#AA4C3B')
f.arrow([(600,402),(600,453)],BLUE)
f.arrow([(685,356),(800,356),(800,453)],GREEN)
for x,w,label,color in [(325,134,'Irrelevant','#AA4C3B'),(518,164,'Need more evidence',BLUE),(748,110,'Sufficient',GREEN)]:
 f.rect(x,414,w,25,'#FFFFFF',None,3);f.text(x+w/2,431,label,13,color,True,'middle')
f.rect(320,458,142,75,'#FFFFFF','#AA4C3B',8)
f.text(391,488,'Drop',21,bold=True,anchor='middle');f.text(391,514,'No evidence',15,MUTED,anchor='middle')
f.rect(487,458,226,75,'#FFFFFF',BLUE,8)
f.text(600,484,'Explore',21,bold=True,anchor='middle')
f.text(600,506,'OPEN (lines)  /  FIND (phrase)',13.5,BLUE,anchor='middle')
f.text(600,525,'At most 3 extra actions / document',11.5,MUTED,anchor='middle')
f.rect(738,458,141,75,'#FFFFFF',GREEN,8)
f.text(808.5,488,'Return',21,bold=True,anchor='middle');f.text(808.5,514,'Selected lines',14.5,MUTED,anchor='middle')
# Dashed re-evaluation route; a small white bridge distinguishes the crossing
# from the sufficient branch. This is a loop, not another decision path.
f.arrow([(713,480),(725,480),(725,291)],PURPLE,lw=2,dash=True)
f.poly([(716,356),(734,356)],stroke='#F7F4FB',lw=7)
f.poly([(716,356),(734,356)],stroke=GREEN,lw=2.3)
f.text(741,321,'Reassess',12,PURPLE)

f.rect(936,83,240,471,'#F0F8F3',GREEN)
f.text(1056,126,'Solver',25,bold=True,anchor='middle')
f.text(1056,197,'Selected evidence',18,bold=True,anchor='middle')
f.rect(954,220,204,245,'#FFFFFF',LINE,9)
for y,tag in [(253,'Excerpt A + citation'),(350,'Excerpt B + citation')]:
 f.text(969,y,tag,14,MUTED)
 for j,w in enumerate([163,163,116]):f.rect(970,y+14+j*16,w,8,'#BFE0CD',None,2)
f.text(971,448,'…',24,GREEN,True)
f.lines(1056,502,['Verbatim source passages','enter the solver context.'],14,MUTED,anchor='middle',leading=22)
f.arrow([(264,335),(300,335)],BLUE)
f.arrow([(900,335),(936,335)],GREEN)
f.text(600,584,'Inspect selectively; keep intermediate reading outside the solver’s context.',17,bold=True,anchor='middle')
f.save()
print('Created vector SVG and PDF figures')
