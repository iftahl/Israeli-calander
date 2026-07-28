import json
from datetime import date, timedelta
from pyluach import dates

START_YEAR=2025
END_YEAR=2035

def g_from_h(hy, hm, hd):
    g=dates.HebrewDate(hy,hm,hd).to_greg()
    return date(g.year,g.month,g.day)

def add(events, d, name, category, description):
    events.append({"date": d.isoformat(), "name": name, "category": category, "description": description})

def israel_independence_day(hy):
    d=g_from_h(hy,2,5)  # Iyar=2 in pyluach Nissan-based month numbering
    # Python weekday Mon=0 ... Sun=6
    if d.weekday()==4: # Friday
        return d-timedelta(days=1)
    if d.weekday()==5: # Saturday
        return d-timedelta(days=2)
    if d.weekday()==0: # Monday
        return d+timedelta(days=1)
    return d

def holocaust_day(hy):
    d=g_from_h(hy,1,27) # Nisan=1
    if d.weekday()==4:
        return d-timedelta(days=1)
    if d.weekday()==6:
        return d+timedelta(days=1)
    return d

events=[]
# Hebrew years overlapping range
for hy in range(5785, 5797):
    fixed=[
      (7,1,'ראש השנה – יום א׳','off','יום מנוחה רשמי לעובדים שבחרו בחגי ישראל.'),
      (7,2,'ראש השנה – יום ב׳','off','יום מנוחה רשמי לעובדים שבחרו בחגי ישראל.'),
      (7,10,'יום הכיפורים','off','יום מנוחה רשמי.'),
      (7,15,'סוכות – יום ראשון','off','יום מנוחה רשמי.'),
      (7,22,'שמיני עצרת / שמחת תורה','off','יום מנוחה רשמי בישראל.'),
      (1,15,'פסח – יום ראשון','off','יום מנוחה רשמי.'),
      (1,21,'שביעי של פסח','off','יום מנוחה רשמי.'),
      (3,6,'שבועות','off','יום מנוחה רשמי.'),
      (11,15,'ט״ו בשבט','observance','מועד יהודי, אך אינו יום חופש כללי לפי החוק.'),
      (12,14,'פורים','observance','מועד יהודי, אך אינו יום חופש כללי לפי החוק.'),
      (1,18,'יום השואה','observance','יום זיכרון ממלכתי, אך אינו יום חופש כללי.'),
      (2,18,'ל״ג בעומר','observance','מועד יהודי, אך אינו יום חופש כללי.'),
      (2,28,'יום ירושלים','observance','יום ציון ממלכתי, אך אינו יום חופש כללי.'),
      (9,25,'חנוכה – יום ראשון','observance','חנוכה אינו חופשה כללית מעבודה.'),
    ]
    for hm,hd,name,cat,desc in fixed:
        try: add(events,g_from_h(hy,hm,hd),name,cat,desc)
        except: pass
    # eves / shortened days
    eves=[(6,29,'ערב ראש השנה'),(7,9,'ערב יום הכיפורים'),(7,14,'ערב סוכות'),(7,21,'הושענא רבה / ערב שמיני עצרת'),(1,14,'ערב פסח'),(1,20,'ערב שביעי של פסח'),(3,5,'ערב שבועות')]
    for hm,hd,name in eves:
        try: add(events,g_from_h(hy,hm,hd),name,'short','בדרך כלל יום עבודה מקוצר; אינו יום חופש מלא אוטומטי לכל עובד.')
        except: pass
    # Independence and memorial
    try:
        ind=israel_independence_day(hy)
        add(events,ind,'יום העצמאות','off','יום חג מדינה ויום מנוחה רשמי לכלל הדתות.')
        add(events,ind-timedelta(days=1),'יום הזיכרון','observance','יום זיכרון ממלכתי; בדרך כלל אינו יום חופש מלא במשק.')
        hd=holocaust_day(hy)
        # replace fixed rough entry for this Hebrew year/date if duplicates possible
        events=[e for e in events if not (e['name']=='יום השואה' and e['date'] in {g_from_h(hy,1,27).isoformat(), g_from_h(hy,1,18).isoformat()})]
        add(events,hd,'יום השואה','observance','יום זיכרון ממלכתי, אך אינו יום חופש כללי.')
    except: pass

# Filter date range and sort
lo=date(START_YEAR,1,1); hi=date(END_YEAR,12,31)
events=[e for e in events if lo <= date.fromisoformat(e['date']) <= hi]
# de-dupe
seen=set(); out=[]
for e in sorted(events,key=lambda x:(x['date'],x['name'])):
    k=(e['date'],e['name'])
    if k not in seen:
        seen.add(k); out.append(e)
with open('/mnt/data/israel-calendar-pwa/events.js','w',encoding='utf-8') as f:
    f.write('window.HOLIDAY_EVENTS = ' + json.dumps(out,ensure_ascii=False,indent=2) + ';\n')
print(len(out))
