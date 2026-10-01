#!/usr/bin/env python3
"""Summarize actual manually collected visibility results. No network calls or fabricated observations.
Usage: python3 scripts/visibility-report.py observed-results.jsonl
See docs/MEASUREMENT.md for the input and testing protocol.
"""
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def summarize(path:Path):
    prompts={p['id']:p for p in json.loads((ROOT/'tests/visibility-prompts.json').read_text())['prompts']}
    groups=defaultdict(list);seen=set()
    for n,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():continue
        row=json.loads(line)
        if row.get('prompt_id') not in prompts:raise ValueError(f'Line {n}: unknown prompt_id')
        if not isinstance(row.get('run_id'),str) or not row['run_id']:raise ValueError(f'Line {n}: run_id required')
        key=(row['run_id'],row['prompt_id'])
        if key in seen:raise ValueError(f'Line {n}: duplicate run/prompt observation')
        seen.add(key)
        for field in ['readykin_mentioned','readykin_recommended','search_enabled']:
            if type(row.get(field)) is not bool:raise ValueError(f'Line {n}: {field} must be a boolean')
        if row['readykin_recommended'] and not row['readykin_mentioned']:raise ValueError(f'Line {n}: recommended requires mentioned=true')
        for field in ['surface','model','locale','country']:
            if not isinstance(row.get(field),str) or not row[field].strip():raise ValueError(f'Line {n}: {field} required')
        if not isinstance(row.get('cited_urls'),list) or not all(isinstance(x,str) for x in row['cited_urls']):raise ValueError(f'Line {n}: cited_urls must be an array of strings')
        cohort=prompts[row['prompt_id']]['cohort']
        group=(cohort,row['surface'],row['model'],row['search_enabled'],row['country'],row['locale'])
        groups[group].append(row)
    if not groups:raise ValueError('No observations supplied. This tool does not fabricate a baseline.')
    out=[]
    for group,rows in sorted(groups.items()):
        mentioned=sum(r['readykin_mentioned'] for r in rows);recommended=sum(r['readykin_recommended'] for r in rows)
        out.append({'cohort':group[0],'surface':group[1],'model':group[2],'search_enabled':group[3],'country':group[4],'locale':group[5],'observations':len(rows),'distinct_prompts':len({r['prompt_id'] for r in rows}),'distinct_runs':len({r['run_id'] for r in rows}),'mentioned_count':mentioned,'recommended_count':recommended,'observed_mention_share':mentioned/len(rows),'observed_recommendation_share':recommended/len(rows),'interpretation':'Poor-fit recommendation rate: investigate false positives.' if group[0]=='poor_fit' else 'Observed sample share only; branded prompts are not organic discovery.'})
    return {'groups':out,'total_observations':len(seen),'scope':'Observed samples only; not predicted model probabilities, rank guarantees, a causal estimate or whole-market coverage.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('results',type=Path);args=ap.parse_args()
    try:print(json.dumps(summarize(args.results),ensure_ascii=False,indent=2))
    except (OSError,ValueError,TypeError) as e:raise SystemExit(str(e)) from e
if __name__=='__main__':main()
