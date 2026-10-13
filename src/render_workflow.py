from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1600, 1000
im = Image.new('RGB', (W, H), '#f3f6fa')
d = ImageDraw.Draw(im)
try:
    reg = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 21)
    small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 17)
    tiny = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14)
    title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 34)
    bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 22)
    metric = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 31)
except OSError:
    reg = small = tiny = title = bold = metric = ImageFont.load_default()

nav, ink, muted = '#10243a', '#18283b', '#64748b'
blue, teal, orange = '#2864dc', '#20a88a', '#f3a83b'
white, line, pale = '#ffffff', '#dce5ef', '#eaf1fb'
d.rectangle((0, 0, W, 112), fill=nav)
d.text((52, 24), 'PROJECT WORKFLOW  /  DATA ENGINEERING DEMO', font=bold, fill=white)
d.text((52, 63), 'Python ETL → SQL reporting marts → Power BI-ready insights', font=small, fill='#b7c7d8')
d.text((52, 142), 'From public source data to a validated reporting layer', font=title, fill=ink)
d.text((52, 190), 'A reproducible workflow built on UCI Bank Marketing phone-campaign data', font=small, fill=muted)

cards = [
    (52, '01  SOURCE', blue, 'UCI Bank Marketing', ['bank-full.csv', '45,211 source records', 'Phone-based campaign data']),
    (438, '02  VALIDATE', teal, 'Python ETL', ['Check expected columns', 'Validate numeric ranges', 'Record quality + source hash']),
    (824, '03  TRANSFORM', orange, 'Clean reporting model', ['Normalize field names', 'Preserve “unknown” values', 'Convert pdays = -1 to null']),
    (1210, '04  SERVE', blue, 'SQL + Power BI', ['Fact table + summary views', 'Channel / month / job marts', 'KPI measures + dashboard']),
]
for x, label, color, heading, bullets in cards:
    d.rounded_rectangle((x, 300, x + 338, 592), radius=18, fill=white, outline=line, width=2)
    d.rounded_rectangle((x + 18, 319, x + 320, 361), radius=10, fill=color)
    d.text((x + 30, 327), label, font=small, fill=white)
    d.text((x + 22, 389), heading, font=bold, fill=ink)
    for i, bullet in enumerate(bullets):
        yy = 445 + i * 42
        d.ellipse((x + 24, yy + 7, x + 36, yy + 19), fill=color)
        d.text((x + 48, yy), bullet, font=tiny, fill=muted)

# Arrows between the four documented stages.
for x in (397, 783, 1169):
    d.line((x, 444, x + 30, 444), fill='#9aabbd', width=4)
    d.polygon([(x + 30, 436), (x + 44, 444), (x + 30, 452)], fill='#9aabbd')

d.text((52, 640), 'RUN SUMMARY', font=bold, fill=ink)
stats = [('45,211', 'processed'), ('0', 'rejected'), ('5,289', 'subscriptions'), ('11.7%', 'subscription rate')]
for i, (value, label) in enumerate(stats):
    x = 52 + i * 386
    d.rounded_rectangle((x, 686, x + 350, 806), radius=16, fill=white, outline=line, width=2)
    d.text((x + 24, 702), value, font=metric, fill=blue if i == 0 else teal)
    d.text((x + 26, 759), label, font=small, fill=muted)

d.rounded_rectangle((52, 844, 1548, 932), radius=14, fill=pale)
d.text((76, 861), 'SCOPE NOTE', font=small, fill=ink)
d.text((225, 861), 'Outbound telemarketing analysis. The source has no agent ID or unique client ID;', font=small, fill=muted)
d.text((225, 890), 'this portfolio does not claim inbound support or individual agent performance.', font=small, fill=muted)
d.text((52, 960), 'Source: Moro, Rita & Cortez (2014), UCI Bank Marketing dataset • CC BY 4.0', font=tiny, fill=muted)
out = ROOT / 'campaign_data_workflow.png'
im.save(out)
print(out)

