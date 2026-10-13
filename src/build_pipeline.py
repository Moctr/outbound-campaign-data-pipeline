import csv, json, hashlib, sys
from pathlib import Path
from collections import Counter
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ['age','job','marital','education','default','balance','housing','loan','contact','day','month','duration','campaign','pdays','previous','poutcome','y']
MONTHS = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

def run(input_path=None):
    source = Path(input_path) if input_path else ROOT / 'data' / 'raw' / 'bank-full.csv'
    if not source.exists():
        raise SystemExit(f'Missing source CSV: {source}. Download bank-full.csv from the UCI source listed in README.md.')
    raw = source.read_bytes()
    raw_hash = hashlib.sha256(raw).hexdigest()
    with source.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        headers = [h.strip() for h in (reader.fieldnames or [])]
        if headers != EXPECTED:
            raise ValueError(f'Unexpected source schema. Expected {EXPECTED}; got {headers}')
        records = list(reader)
    if len(records) != 45211:
        raise ValueError(f'Expected UCI full bank dataset with 45,211 records; found {len(records)}')
    seen = set(); exact_duplicates = 0; unknown_counts = Counter(); invalid = []
    clean=[]
    for idx, r in enumerate(records, start=2):
        vals={k:(r.get(k) or '').strip() for k in EXPECTED}
        sig=tuple(vals[k] for k in EXPECTED)
        if sig in seen: exact_duplicates += 1
        seen.add(sig)
        try:
            age=int(vals['age']); balance=Decimal(vals['balance']); day=int(vals['day']); duration=int(vals['duration']); campaign=int(vals['campaign']); pdays=int(vals['pdays']); previous=int(vals['previous'])
            if vals['y'] not in {'yes','no'}: raise ValueError('invalid target')
            if vals['month'] not in MONTHS: raise ValueError('invalid month')
            if age < 18 or age > 120 or duration < 0 or campaign < 1 or day < 1 or day > 31: raise ValueError('out-of-range numeric value')
        except Exception as e:
            invalid.append({'line':idx,'reason':str(e)}); continue
        for k in ['job','marital','education','default','housing','loan','contact','poutcome']:
            if vals[k].lower() == 'unknown': unknown_counts[k] += 1
        clean.append({
            'campaign_record_id':len(clean)+1, 'age':age, 'job':vals['job'].lower(), 'marital_status':vals['marital'].lower(),
            'education':vals['education'].lower(), 'credit_default':vals['default'].lower(), 'account_balance_eur':str(balance),
            'housing_loan':vals['housing'].lower(), 'personal_loan':vals['loan'].lower(), 'contact_channel':vals['contact'].lower(),
            'contact_day_of_month':day, 'contact_month':vals['month'].lower(), 'call_duration_seconds':duration,
            'campaign_contact_number':campaign, 'days_since_previous_contact':None if pdays == -1 else pdays,
            'previous_campaign_contacts':previous, 'previous_campaign_outcome':vals['poutcome'].lower(),
            'subscribed_term_deposit':1 if vals['y']=='yes' else 0,
            'previously_contacted':1 if pdays != -1 else 0,
            'duration_minutes':str((Decimal(duration)/Decimal(60)).quantize(Decimal('0.01')))
        })
    if invalid: raise ValueError(f'{len(invalid)} invalid rows; first errors: {invalid[:5]}')
    out=ROOT/'data'/'processed'; out.mkdir(parents=True,exist_ok=True)
    fact_path=out/'fact_campaign_contact.csv'
    fields=list(clean[0].keys())
    with fact_path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(clean)
    by_channel=Counter(); by_job=Counter(); by_month=Counter(); durations=Counter(); campaigns=Counter()
    for x in clean:
        ch=x['contact_channel']; by_channel[ch]+=1; by_job[x['job']]+=1; by_month[x['contact_month']]+=1
        durations[ch]+=x['call_duration_seconds']; campaigns[ch]+=x['subscribed_term_deposit']
    def rate(subscribed,total): return round(100*subscribed/total,2) if total else 0
    channel_rows=[]
    for ch,total in sorted(by_channel.items()):
        subs=sum(x['subscribed_term_deposit'] for x in clean if x['contact_channel']==ch)
        call_secs=sum(x['call_duration_seconds'] for x in clean if x['contact_channel']==ch)
        channel_rows.append({'contact_channel':ch,'contacts':total,'subscriptions':subs,'subscription_rate_pct':rate(subs,total),'avg_call_duration_seconds':round(call_secs/total,2)})
    job_rows=[]
    for job,total in sorted(by_job.items()):
        subs=sum(x['subscribed_term_deposit'] for x in clean if x['job']==job)
        job_rows.append({'job':job,'contacts':total,'subscriptions':subs,'subscription_rate_pct':rate(subs,total)})
    month_rows=[]
    for m in MONTHS:
        grp=[x for x in clean if x['contact_month']==m]
        if grp:
            subs=sum(x['subscribed_term_deposit'] for x in grp)
            month_rows.append({'contact_month':m,'contacts':len(grp),'subscriptions':subs,'subscription_rate_pct':rate(subs,len(grp))})
    def write_csv(name,rows):
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    write_csv('mart_by_channel.csv',channel_rows); write_csv('mart_by_job.csv',job_rows); write_csv('mart_by_month_category.csv',month_rows)
    subs=sum(x['subscribed_term_deposit'] for x in clean)
    report={'dataset':'UCI Bank Marketing bank-full.csv','source_sha256':raw_hash,'source_records':len(records),'processed_records':len(clean),'rejected_records':len(invalid),'exact_duplicate_rows_observed':exact_duplicates,'duplicate_rows_removed':0,'unknown_value_counts_by_field':dict(unknown_counts),'subscription_count':subs,'subscription_rate_pct':rate(subs,len(clean)),'avg_call_duration_seconds':round(sum(x['call_duration_seconds'] for x in clean)/len(clean),2),'month_is_category_not_year_month':True,'limitations':['No agent identifier','No unique customer identifier','No year or timestamp field in bank-full.csv','Call duration is known only after contact and should not be used as a pre-call predictor']}
    (out/'quality_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else None)


