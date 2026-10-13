from pathlib import Path
import csv, json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data'/'processed'
def read(n):
 with (p/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
channels=read('mart_by_channel.csv'); months=read('mart_by_month_category.csv'); facts=read('fact_campaign_contact.csv'); q=json.loads((p/'quality_report.json').read_text(encoding='utf-8'))
contact_bins={}
for r in facts:
 k='5+' if int(r['campaign_contact_number'])>=5 else str(r['campaign_contact_number'])
 a=contact_bins.setdefault(k,[0,0]); a[0]+=1; a[1]+=int(r['subscribed_term_deposit'])
contact_bins={k:v for k,v in sorted(contact_bins.items(),key=lambda x: (6 if x[0]=='5+' else int(x[0])))}
W,H=1600,1200; im=Image.new('RGB',(W,H),'#f3f6fa');d=ImageDraw.Draw(im)
try:
 reg=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19); small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16); tiny=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14); big=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',34); title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30); bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',20)
except: reg=small=tiny=big=title=bold=ImageFont.load_default()
nav='#10243a'; blue='#2864dc'; teal='#20a88a'; orange='#f3a83b'; red='#d95862'; ink='#18283b'; muted='#64748b'; line='#e2e9f1'; white='#ffffff'; pale='#eaf1fb'
d.rectangle((0,0,W,105),fill=nav);d.text((46,22),'CAMPAIGN OPERATIONS  /  DATA ENGINEERING DEMO',font=bold,fill=white);d.text((46,58),'UCI BANK MARKETING • REAL PUBLIC PHONE-CAMPAIGN DATA • 45,211 CAMPAIGN RECORDS',font=small,fill='#b7c7d8');d.text((1340,43),'2008–2010*',font=reg,fill=white)
d.text((48,132),'Outbound Campaign Performance',font=title,fill=ink);d.text((48,174),'Validated phone-campaign data modeled for operational reporting',font=small,fill=muted)
subs=q['subscription_count']; n=q['processed_records']; overall=q['subscription_rate_pct']; avg=q['avg_call_duration_seconds']; unknown=q['unknown_value_counts_by_field'].get('contact',0)
metrics=[('Campaign records',f'{n:,}','One row per campaign record',blue),('Subscriptions',f'{subs:,}',f'{overall:.1f}% of campaign records',teal),('Avg. last-call duration',f'{avg/60:.1f} min','Duration of last contact in source',orange),('Unknown contact channel',f'{unknown:,}',f'{unknown/n*100:.1f}% retained as category',red)]
for j,(lab,val,sub,col) in enumerate(metrics):
 x=48+j*378;y=220;d.rounded_rectangle((x,y,x+350,y+132),radius=15,fill=white,outline=line,width=2);d.rectangle((x,y+20,x+6,y+107),fill=col);d.text((x+24,y+17),lab,font=small,fill=muted);d.text((x+24,y+45),val,font=big,fill=ink);d.text((x+24,y+100),sub,font=tiny,fill=muted)
# chart panels
x,y=48,385;d.rounded_rectangle((x,y,x+735,y+370),radius=15,fill=white,outline=line,width=2);d.text((x+24,y+22),'Records and subscriptions by channel',font=bold,fill=ink);d.text((x+24,y+57),'Bars = campaign records  •  Labels = subscription rate',font=tiny,fill=muted)
maxc=max(int(r['contacts']) for r in channels)
for j,r in enumerate(sorted(channels,key=lambda r:int(r['contacts']),reverse=True)):
 yy=y+115+j*70; lab=r['contact_channel'].title(); count=int(r['contacts']); d.text((x+24,yy),lab,font=reg,fill=ink); d.rounded_rectangle((x+195,yy+2,x+195+int(350*count/maxc),yy+31),radius=9,fill=blue if lab.lower()!='unknown' else '#9fb0c4'); d.text((x+565,yy),f'{count:,}',font=small,fill=ink);d.text((x+565,yy+27),f'{float(r["subscription_rate_pct"]):.1f}% subscribed',font=tiny,fill=muted)
# month category chart (categorical not chronological)
x2=817;d.rounded_rectangle((x2,y,x2+735,y+370),radius=15,fill=white,outline=line,width=2);d.text((x2+24,y+22),'Campaign records by month label',font=bold,fill=ink);d.text((x2+24,y+57),'The source has month names but no year; shown as categories',font=tiny,fill=muted)
month_ord=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']; mvals={r['contact_month']:int(r['contacts']) for r in months}; maxm=max(mvals.values())
for j,m in enumerate(month_ord):
 col=j%6; row=j//6; xx=x2+25+col*114; yy=y+116+row*93; val=mvals.get(m,0); d.text((xx,yy),m.upper(),font=tiny,fill=muted); d.rounded_rectangle((xx,yy+22,xx+92,yy+42),radius=7,fill='#dce5f1'); d.rounded_rectangle((xx,yy+22,xx+max(6,int(92*val/maxm)),yy+42),radius=7,fill=teal); d.text((xx,yy+51),f'{val:,}',font=small,fill=ink)
# repeat contact table
x,y=48,775;d.rounded_rectangle((x,y,1552,1075),radius=15,fill=white,outline=line,width=2);d.text((x+24,y+22),'Contact frequency profile',font=bold,fill=ink);d.text((x+24,y+55),'The campaign field counts calls to a client in the campaign; the dataset does not expose a client ID.',font=tiny,fill=muted)
headers=['CALLS IN CURRENT CAMPAIGN','CAMPAIGN RECORDS','SUBSCRIPTIONS','SUBSCRIPTION RATE']; widths=[420,330,330,350];xx=x+24;yy=y+99
for h,wid in zip(headers,widths):d.text((xx,yy),h,font=tiny,fill=muted);xx+=wid
d.line((x+24,yy+28,1526,yy+28),fill=line,width=2)
for k,(cnt,sy) in contact_bins.items():
 yy+=31;rate=sy/cnt*100 if cnt else 0;vals=[k if k!='5+' else '5 or more',f'{cnt:,}',f'{sy:,}',f'{rate:.1f}%'];xx=x+24
 for val,wid in zip(vals,widths):d.text((xx,yy),val,font=reg,fill=ink);xx+=wid
 d.line((x+24,yy+30,1526,yy+30),fill='#edf1f5',width=1)
# footnote box
foot='*Dataset rows do not include year or an agent identifier. Call duration is known after a call and is descriptive, not a pre-call targeting feature.'
d.rounded_rectangle((48,1075,1552,1153),radius=12,fill=pale);d.text((70,1092),'DATA LIMITS',font=small,fill=ink);d.text((70,1122),foot,font=tiny,fill=muted)
d.text((48,1172),'Source: Moro, Rita & Cortez (2014), UCI Bank Marketing dataset • CC BY 4.0 • This is outbound telemarketing, not inbound customer support.',font=tiny,fill=muted)
im.save(ROOT/'call_campaign_dashboard_preview.png')
print(ROOT/'call_campaign_dashboard_preview.png')


