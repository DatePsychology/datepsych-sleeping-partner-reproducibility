#!/usr/bin/env python3
"""Independent aggregate reconstruction and figure reproduction for Date Psychology critique.

Source inputs: source-traced CSVs, not respondent-level data. All assumptions documented
in SOURCE_AUDIT.md. Re-run from the repository root:

    python reproduce_sleep_figures.py
    python reproduce_sleep_figures.py --out reproduced_figures

The default run never touches article_figures/. Requires Python 3.10+.
"""
from __future__ import annotations

import argparse
import csv
import math
from itertools import product
from pathlib import Path

from scipy.stats import chi2_contingency, fisher_exact, norm

ROOT = Path(__file__).resolve().parent


def read_csv(name: str):
    with (ROOT / name).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise ValueError('Refusing to save an empty table')
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def compatible_counts(n: int, reported_pct: float, decimals: int):
    """All k whose 100*k/n rounds to p at displayed precision.

    Uses half-open mathematical rounding intervals; no special banker's rounding.
    """
    radius = 0.5 * 10.0**(-decimals)
    return [k for k in range(n + 1)
            if reported_pct-radius-1e-12 <= 100*k/n < reported_pct+radius-1e-12]


def pub_percent(sex: str, measure: str):
    matches=[r for r in read_csv('published_sample_percentages.csv')
             if r['group']==sex and r['measure']==measure]
    if len(matches)!=1: raise ValueError(f'Expected unique published percent for {sex} / {measure}')
    return float(matches[0]['published_percent']), int(matches[0]['decimals'])


def event_yes(period: str, sex: str):
    matches=[r for r in read_csv('published_event_counts.csv')
             if r['relationship']==period and r['sex']==sex]
    if len(matches)!=1: raise ValueError(f'Missing event count: {period} / {sex}')
    return int(matches[0]['label_yes_count'])


def published_test(key: str):
    matches=[r for r in read_csv('published_tests.csv') if r['key']==key]
    if len(matches)!=1:raise ValueError(f'Missing test: {key}')
    return matches[0]


def reconstruct_size_candidates():
    """Test the two sex splits implied by the rounded 24.9% figure.

    Require the CURRENT relationship status/waking percentages of BOTH sexes to
    be compatible with whole-person counts and ordinary rounding.
    """
    study_totals=read_csv('published_study_totals.csv')
    total=int(next(r['reported_total'] for r in study_totals if r['study']=='datepsych_2023'))
    women_pct,wd=pub_percent('women','female_share')
    men_status,md=pub_percent('men','not_currently_partnered')
    women_status,wd2=pub_percent('women','not_currently_partnered')
    men_waking,mwd=pub_percent('men','current_waking')
    women_waking,wwd=pub_percent('women','current_waking')
    candidates=[]
    for women in compatible_counts(total,women_pct,wd):
        men=total-women
        for m_not in compatible_counts(men,men_status,md):
            for w_not in compatible_counts(women,women_status,wd2):
                mc=men-m_not;wc=women-w_not
                for m_yes in compatible_counts(mc,men_waking,mwd):
                    for w_yes in compatible_counts(wc,women_waking,wwd):
                        candidates.append(dict(men=men,women=women,current_men=mc,current_women=wc,
                                               current_woken_men=m_yes,current_woken_women=w_yes))
    return candidates


def group_sizes():
    candidates = reconstruct_size_candidates()
    if len(candidates) != 1:
        raise RuntimeError(f'Cannot uniquely infer current-group sizes: {candidates}')
    s = candidates[0].copy()
    # The following conditional approximations assume no missing answers to
    # the gender-specific past-relationship-status and past-waking items.
    men=s['men']; women=s['women']
    past_m_pct,pm_d=pub_percent('men','never_past_relationship')
    past_w_pct,pw_d=pub_percent('women','never_past_relationship')
    m_never=compatible_counts(men,past_m_pct,pm_d)
    w_never=compatible_counts(women,past_w_pct,pw_d)
    if len(m_never)!=1 or len(w_never)!=1:
        raise RuntimeError('Past status is not uniquely resolved')
    s['past_men']=men-m_never[0]
    s['past_women']=women-w_never[0]
    m_pct,m_d=pub_percent('men','past_waking')
    w_pct,w_d=pub_percent('women','past_waking')
    mm=compatible_counts(s['past_men'],m_pct,m_d)
    ww=compatible_counts(s['past_women'],w_pct,w_d)
    if len(mm)!=1 or not ww: raise RuntimeError('Cannot reconstruct past waking')
    s['past_woken_men']=mm[0]
    s['past_woken_women_assumed']=220  # one of 219, 220, 221; explicit choice
    s['past_woken_women_candidates']=ww
    return s


def chi_stats(m_yes, m_total, w_yes, w_total):
    table=[[m_yes,m_total-m_yes],[w_yes,w_total-w_yes]]
    yc,yp,_,_=chi2_contingency(table,correction=True)
    pc,pp,_,_=chi2_contingency(table,correction=False)
    fp=fisher_exact(table).pvalue
    return dict(yates_chi=yc,yates_p=yp,pearson_chi=pc,pearson_p=pp,fisher_p=fp)


def comparative_tests(s):
    # Cases and denominators are INFERRED unless otherwise noted. Source values are
    # in published_tests.csv; this output documents the scenario analyzed.
    cases=[
        ('current_waking',s['current_woken_men'],s['current_men'],s['current_woken_women'],s['current_women'],
         'rounded percentages uniquely reconstruct; validation test'),
        ('current_assault_exposed',event_yes('current','men'),s['current_woken_men'],event_yes('current','women'),s['current_woken_women'],
         '8 published events; denominator conditional on exposure is inferred'),
        ('current_assault_partnered',event_yes('current','men'),s['current_men'],event_yes('current','women'),s['current_women'],
         'alternative denominator, not declared as authors calculation'),
        ('current_flirting_inferred_missingness',451,681,134,236,
         'one compatible solution; 4 fewer female responses; near-match'),
        ('past_waking_default',515,839,s['past_woken_women_assumed'],289,
         'assumes 220 female cases out of 289; rounded 76% permits 219 and 221 too'),
        ('past_assault_inferred_valid',event_yes('past','men'),830,event_yes('past','women'),280,
         'denominators inferred because this nearly exactly reproduces published chi-square'),
        ('past_assault_exposed_alternative',event_yes('past','men'),515,event_yes('past','women'),220,
         'conditional alternative; may overstate valid exposure responses'),
        ('past_assault_all_prior_alternative',event_yes('past','men'),839,event_yes('past','women'),289,
         'prior partnered respondents before apparent item-level nonresponse'),
    ]
    out=[]
    for key,mc,mn,wc,wn,note in cases:
        v=chi_stats(mc,mn,wc,wn)
        out.append(dict(key=key,men_yes=mc,men_total=mn,women_yes=wc,women_total=wn,
                        **{k:format(vv,'.12g') for k,vv in v.items()},assumption=note))
    return out


def valid_triplets(max_n,pct,places):
    solutions=[]
    for n in range(1,max_n+1):
        counts=[compatible_counts(n, p, d) for p,d in zip(pct,places)]
        if any(not cs for cs in counts):continue
        for vals in product(*counts):
            if sum(vals)==n:solutions.append((n,*vals))
    return solutions


def evaluation_candidates(s):
    eligible=[('current','men',s['current_woken_men']),
              ('current','women',s['current_woken_women']),
              ('past','men',s['past_woken_men']),
              ('past','women',max(s['past_woken_women_candidates']))]
    tab={(r['relationship'],r['group']):r for r in read_csv('published_evaluation_percentages.csv')}
    rows=[]
    for period,sex,maximum in eligible:
        inp=tab[(period,sex)]
        ps=[float(inp[f'{cat}_percent']) for cat in ('positive','neutral','negative')]
        ds=[int(inp[f'{cat}_decimals']) for cat in ('positive','neutral','negative')]
        candidates=valid_triplets(maximum,ps,ds)
        for n,a,b,c in candidates:
            rows.append(dict(relationship=period,sex=sex,maximum_exposed=maximum,
                valid_denominator=n,positive_count=a,neutral_count=b,negative_count=c,
                result_type='candidate among purportedly exposed respondents'))
        if not candidates:
            rows.append(dict(relationship=period,sex=sex,maximum_exposed=maximum,
                valid_denominator='NONE',positive_count='',neutral_count='',negative_count='',
                result_type='NO single unweighted denominator exists within exposed group'))
    # Current female rates exactly reproduce among all partnered women.
    candidates=valid_triplets(s['current_women'],[62.1,27.1,10.8],[1,1,1])
    for n,a,b,c in candidates:
        if n>s['current_woken_women']:
            rows.append(dict(relationship='current full partnered sensitivity',sex='women',
                             maximum_exposed=s['current_women'],valid_denominator=n,
                             positive_count=a,neutral_count=b,negative_count=c,
                             result_type='unexposed-inclusive denominator candidate'))
    return rows


def wilcoxon_bounds(label, n1,n2,W,p_reported,assumption):
    N=n1+n2
    ulo,uhi=0,n1*n2
    r1lo=n1*(n1+1)//2
    r1hi=n1*(2*N-n1+1)//2
    r2lo=n2*(n2+1)//2
    r2hi=n2*(2*N-n2+1)//2
    sd=math.sqrt(n1*n2*(N+1)/12)
    def pvalue_if_valid(stat,lo,hi,null):
        return f'{2*norm.sf(abs((stat-null)/sd)):.6g}' if lo<=stat<=hi else ''
    return dict(label=label,n1=n1,n2=n2,N=N,reported_W=W,reported_p=p_reported,
        U_min=ulo,U_max=uhi,W_compatible_with_U=(ulo<=W<=uhi),
        raw_rank_1_min=r1lo,raw_rank_1_max=r1hi,W_compatible_raw_rank_1=(r1lo<=W<=r1hi),
        raw_rank_2_min=r2lo,raw_rank_2_max=r2hi,W_compatible_raw_rank_2=(r2lo<=W<=r2hi),
        untied_p_if_U=pvalue_if_valid(W,ulo,uhi,uhi/2),
        untied_p_if_raw_1=pvalue_if_valid(W,r1lo,r1hi,n1*(N+1)/2),
        untied_p_if_raw_2=pvalue_if_valid(W,r2lo,r2hi,n2*(N+1)/2),
        assumptions=assumption)


def wilcoxon_checks(s):
    return [
        wilcoxon_bounds('current positivity, exposed',453,154,int(published_test('current_positivity')['statistic_reported']),float(published_test('current_positivity')['p_reported']),'Expected comparison among woken respondents; W impossible under common conventions'),
        wilcoxon_bounds('current positivity, all partnered alternative',681,240,int(published_test('current_positivity')['statistic_reported']),float(published_test('current_positivity')['p_reported']),'W possible as women raw rank sum; untied p very different; ties/order unresolved'),
        wilcoxon_bounds('male satisfaction, exposed vs not',453,228,int(published_test('men_satisfaction')['statistic_reported']),float(published_test('men_satisfaction')['p_reported']),'W in bounds for certain conventions; inferential test not reproducible'),
        wilcoxon_bounds('female satisfaction, exposed vs not',154,86,int(published_test('women_satisfaction')['statistic_reported']),float(published_test('women_satisfaction')['p_reported']),'W impossible within 240 women'),
        wilcoxon_bounds('past positivity, exposed',515,220,int(published_test('past_positivity')['statistic_reported']),float(published_test('past_positivity')['p_reported']),'W impossible among described exposed groups'),
        wilcoxon_bounds('past positivity, all past partnered alternative',839,289,int(published_test('past_positivity')['statistic_reported']),float(published_test('past_positivity')['p_reported']),'W still impossible under these two group definitions'),
    ]


def past_waking_rounding(s):
    rows=[]
    for w in s['past_woken_women_candidates']:
        st=chi_stats(s['past_woken_men'],s['past_men'],w,s['past_women'])
        rows.append(dict(men_exposed=s['past_woken_men'],men_total=s['past_men'],
             women_exposed=w,women_total=s['past_women'],
             reconstructed_yates_chi=f'{st["yates_chi"]:.10f}',
             reconstructed_yates_p=f'{st["yates_p"]:.10g}',
             published_yates_chi='3.7084',published_p='0.05414',
             status='discrepancy under no-missingness assumption'))
    return rows


def wilson_interval(k,n,z=1.959963984540054):
    p=k/n
    denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return center-half,center+half


def fig_data(s):
    plot2=[]
    for sex,k,n in [('Men',s['past_woken_men'],s['past_men']),
                    ('Women',s['past_woken_women_assumed'],s['past_women'])]:
        a,b=wilson_interval(k,n)
        plot2.append(dict(sex=sex,cases=k,denominator=n,percent=100*k/n,
            wilson95_lo_pct=100*a,wilson95_hi_pct=100*b,
            note='reconstructed count; binomial interval not corrected for non-probability sampling'))
    plot3=[]
    for sex,k,n,exposed in [('Men',event_yes('past','men'),830,515),('Women',event_yes('past','women'),280,220)]:
        plot3.append(dict(sex=sex,assault_yes=k,all_valid_past_assault_responses=n,
                          exposure_count_estimate=exposed,unconditional_pct=100*k/n,
                          conditional_pct_estimate=100*k/exposed,
                          note='Conditional percentage assumes all affirmative responses are in exposed group and that exposure denominator has no further missingness'))
    drouin={r['response']:r for r in read_csv('drouin_2026_table3.csv')}
    selected=['Started actively participating','Allowed to finish but did not participate',
              'Told them to stop, but they did not stop','Told partner wanted it again']
    plot4=[]
    for label in selected:
        r=drouin[label]
        for group in ('partner','nonpartner'):
            k=int(r[f'{group}_n']);n=int(r[f'{group}_denominator'])
            plot4.append(dict(response=label,group=group,cases=k,denominator=n,
                              percent=100*k/n,reported_rounding_decimals=1,
                              source='Drouin & Cornelius (2026), Table 3; multiple choices allowed'))
    return plot2,plot3,plot4


def render_figures(out,s,plot2,plot3,plot4):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import numpy as np
    NAVY='#23415A';TEAL='#287C83';MAROON='#B1615E';GREY='#707985';LIGHT='#E3E8EB';BG='#FFFFFF'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,
            'axes.spines.right':False,'figure.facecolor':BG,'axes.facecolor':BG,
            'savefig.facecolor':BG})
    def save(fig,name):
        fig.savefig(out/name,dpi=200,bbox_inches='tight',pad_inches=.25)
        plt.close(fig)
    # Figure 1 — concept/comparability visual, not a test of a common estimand.
    vf = {r['measure']: r for r in read_csv('victimfocus_published_comparison.csv')}
    vfp = int(float(vf['woke_to_sexual_activity_underway']['published_percent']))
    waking = [float(r['published_percent']) for r in read_csv('published_sample_percentages.csv')
              if r['measure']=='current_waking']
    min_waking, max_waking = math.floor(min(waking)), math.ceil(max(waking))
    fig,ax=plt.subplots(figsize=(11.6,4.1));ax.set_xlim(0,12);ax.set_ylim(-.35,4.4);ax.axis('off')
    for x,color,title,desc,bottom in [
       (.25,NAVY,'VictimFocus (2021)','Wake to find sexual activity\nalready under way',f'Published result: {vfp}%'),
       (6.2,TEAL,'Date Psychology (2023)','Partner touches someone\nto wake them for sex',f'Published results: {min_waking}–{max_waking}% currently partnered')]:
        patch=FancyBboxPatch((x,1.25),5.55,2.65,boxstyle='round,pad=0.13,rounding_size=.14',
                             linewidth=1.5,edgecolor=color,facecolor='#F6F8FA')
        ax.add_patch(patch)
        ax.text(x+.25,3.50,title,fontsize=16,weight='bold',color=color,va='center')
        ax.text(x+.25,2.64,desc,fontsize=14,color=NAVY,linespacing=1.5,va='center')
        ax.text(x+.25,1.55,bottom,fontsize=11.2,color=GREY,va='center')
    save(fig,'figure_01_measure_mismatch.png')
    # Figure 2 — uses actual reconstructed counts and Wilson intervals.
    fig,ax=plt.subplots(figsize=(10.7,5.0));y=np.array([1,0]);cols=[NAVY,TEAL]
    for i,ob in enumerate(plot2):
        a=ob['percent'];lo=ob['wilson95_lo_pct'];hi=ob['wilson95_hi_pct']
        ax.errorbar(a,y[i],xerr=[[a-lo],[hi-a]],fmt='o',capsize=7,markersize=13,
                    linewidth=2.4,color=cols[i])
        ax.annotate(f'{a:.1f}%  ({ob["cases"]}/{ob["denominator"]})',(a,y[i]),
                    xytext=(10,10),textcoords='offset points',fontsize=13,weight='bold',color=cols[i])
    ax.set_yticks(y,['Men','Women']);ax.set_xlim(50,90);ax.set_ylim(-.5,1.7)
    ax.set_xticks([50,60,70,80,90]);ax.set_xlabel('Reported having been awakened for sex in a past relationship (%)',labelpad=14,color=NAVY)
    ax.grid(axis='x',color=LIGHT,linewidth=.9);ax.set_axisbelow(True);ax.tick_params(axis='both',length=0,pad=10)
    ax.text(.02,.98,'Article: χ² = 3.708; p = .054',transform=ax.transAxes,fontsize=14,color=MAROON,va='top') # published_test('past_waking') gives 3.7084 / 0.05414
    stat=chi_stats(515,839,220,289)
    ax.text(.02,.86,f'Reconstructed: χ² ≈ {stat["yates_chi"]:.3f}; p ≈ {stat["yates_p"]:.6f}',
            transform=ax.transAxes,fontsize=14,color=TEAL,va='top',weight='bold')
    ax.text(0,-.28,'95% Wilson intervals. Values use reconstructed counts; not representative population estimates.',
            transform=ax.transAxes,fontsize=10.3,color=GREY)
    save(fig,'figure_02_past_relationship_waking.png')
    # Figure 3 — denominator comparison conditional vs unconditional.
    x=np.arange(2);w=.33
    fig,ax=plt.subplots(figsize=(10.4,5))
    bars1=ax.bar(x-w/2,[q['unconditional_pct'] for q in plot3],w,color=NAVY,
                 label='All valid respondents (inferred)')
    bars2=ax.bar(x+w/2,[q['conditional_pct_estimate'] for q in plot3],w,color=TEAL,
                 label='Those reporting waking (estimated)')
    for r in list(bars1)+list(bars2):
        ax.annotate(f'{r.get_height():.1f}%',(r.get_x()+r.get_width()/2,r.get_height()),
                    ha='center',va='bottom',xytext=(0,6),textcoords='offset points',fontsize=12,weight='bold')
    ax.set_xticks(x,['Men','Women']);ax.set_ylim(0,26);ax.set_yticks([0,5,10,15,20,25])
    ax.set_ylabel('Labeled experience sexual assault (%)',color=NAVY)
    ax.tick_params(length=0);ax.grid(axis='y',color=LIGHT);ax.set_axisbelow(True)
    ax.legend(loc='upper left',frameon=False,fontsize=10.8)
    ax.text(0,-.20,'Published rates use inferred denominators 830/280. Exposed denominators 515/220 are approximate.',
            transform=ax.transAxes,color=GREY,fontsize=10)
    save(fig,'figure_03_assault_label_denominators.png')
    # Figure 4 — all bars derived from Table 3 integer counts, never hard-coded percentages.
    selected=['Started actively participating','Allowed to finish but did not participate',
              'Told them to stop, but they did not stop','Told partner wanted it again']
    labels=['Actively\nparticipated','Allowed person\nto finish','Asked to stop;\nnot respected','Told them they\nwanted it again']
    p=[next(x['percent'] for x in plot4 if x['response']==key and x['group']=='partner') for key in selected]
    n=[next(x['percent'] for x in plot4 if x['response']==key and x['group']=='nonpartner') for key in selected]
    xx=np.arange(4);width=.35
    fig,ax=plt.subplots(figsize=(11.8,5.3))
    a=ax.bar(xx-width/2,p,width,color=NAVY,label='Partner (n = 143)')
    b=ax.bar(xx+width/2,n,width,color=MAROON,label='Nonpartner (n = 29)')
    for rect in list(a)+list(b):
        ax.annotate(f'{rect.get_height():.1f}%',(rect.get_x()+rect.get_width()/2,rect.get_height()),
                    ha='center',va='bottom',xytext=(0,5),textcoords='offset points',fontsize=10.8,weight='bold')
    ax.set_xticks(xx,labels);ax.set_ylim(0,78);ax.set_yticks([0,20,40,60])
    ax.set_ylabel('Respondents selecting response (%)',color=NAVY)
    ax.legend(frameon=False,loc='upper right');ax.grid(axis='y',color=LIGHT);ax.set_axisbelow(True);ax.tick_params(length=0)
    ax.text(0,-.23,'Multiple responses allowed; last-incident subsample. Nonpartner group is small.',
            transform=ax.transAxes,color=GREY,fontsize=10.1)
    save(fig,'figure_04_reactions_by_relationship.png')


def make_report(s,comp,rounding,evaluation,wilcoxon):
    d={r['key']:r for r in comp}
    text=[]
    text.append('DATE PSYCHOLOGY SLEEPING-PARTNER SURVEY — INDEPENDENT PUBLISHED-AGGREGATE AUDIT')
    text.append('No microdata, original questionnaire dataset, or original analysis code was available.')
    text.append('')
    text.append('1. RECONSTRUCTED SAMPLE (assuming no status-item nonresponse)')
    for key in ['men','women','current_men','current_women','current_woken_men','current_woken_women','past_men','past_women','past_woken_men']:
        text.append(f'  {key}: {s[key]}')
    text.append(f'  past_woken_women: {s["past_woken_women_candidates"]} fit rounded 76%; chart scenario uses 220')
    text.append('')
    text.append('2. PUBLISHED VS RECONSTRUCTED CHI-SQUARE')
    original={x['key']:x for x in read_csv('published_tests.csv')}
    for k in ['current_waking','current_assault_exposed','current_flirting_inferred_missingness',
              'past_waking_default','past_assault_inferred_valid']:
        published={'current_assault_exposed':'current_assault',
                   'current_flirting_inferred_missingness':'current_flirting',
                   'past_waking_default':'past_waking',
                   'past_assault_inferred_valid':'past_assault'}.get(k,k)
        row=d[k]
        text.append(f'  {k}: authors chi={original[published]["statistic_reported"]}, p={original[published]["p_reported"]}; '
                    f'Yates chi={float(row["yates_chi"]):.6f}, p={float(row["yates_p"]):.9g}; '
                    f'Fisher p={float(row["fisher_p"]):.9g}.')
        text.append(f'    assumptions: {row["assumption"]}')
    text.append('')
    text.append('3. PAST-WAKING 76% ROUNDING SENSITIVITY')
    for row in rounding:
        text.append(f'  women {row["women_exposed"]}/289: Yates chi={float(row["reconstructed_yates_chi"]):.6f}, '
                    f'p={float(row["reconstructed_yates_p"]):.8g}')
    text.append('')
    text.append('4. FEMALE CURRENT EVALUATION')
    womens=[r for r in evaluation if r['relationship']=='current' and r['sex']=='women']
    text.append(f'  eligible women who reported waking: {s["current_woken_women"]}; '
                f'compatible full 3-category denominator among exposed: {sum(isinstance(x["valid_denominator"],int) for x in womens)}')
    full=[r for r in evaluation if r['relationship']=='current full partnered sensitivity' and r['sex']=='women' and r['valid_denominator']==240]
    text.append(f'  all-partnered compatible example: {[(x["positive_count"],x["neutral_count"],x["negative_count"]) for x in full]} / 240')
    text.append('')
    text.append('5. WILCOXON/MANN-WHITNEY STATISTIC BOUNDS')
    for row in wilcoxon:
        text.append(f'  {row["label"]}: W={row["reported_W"]}; U possible={row["W_compatible_with_U"]}; '
                    f'raw rank group1 possible={row["W_compatible_raw_rank_1"]}; '
                    f'raw rank group2 possible={row["W_compatible_raw_rank_2"]}; reported p={row["reported_p"]}.')
    text.append('  Note: R wilcox.test uses a U-type statistic; rank-sum conventions vary. No tied-Likert test is recreated.')
    text.append('')
    text.append('6. INTERPRETATION')
    text.append('  Reproducibility of an aggregate statistic does not verify response definitions or sample selection.')
    text.append('  Inconsistent values are not evidence of intentional wrongdoing.')
    text.append('  The two underlying surveys operationalize different phenomena; plots are not a direct prevalence comparison.')
    return '\n'.join(text)+'\n'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='reproduced_figures',help='Output directory (relative to repo root unless absolute)')
    args=parser.parse_args(argv)
    out=Path(args.out)
    if not out.is_absolute():out=ROOT/out
    out=out.resolve()
    if out==(ROOT/'article_figures').resolve():
        parser.error('Do not overwrite article_figures; use reproduced_figures or another directory')
    out.mkdir(exist_ok=True,parents=True)
    s=group_sizes()
    c=comparative_tests(s)
    es=evaluation_candidates(s)
    w=wilcoxon_checks(s)
    r=past_waking_rounding(s)
    plot2,plot3,plot4=fig_data(s)
    write_csv(out/'reconstructed_chi_square.csv',c)
    write_csv(out/'past_waking_rounding_sensitivity.csv',r)
    write_csv(out/'evaluation_denominator_candidates.csv',es)
    write_csv(out/'wilcoxon_statistic_bounds.csv',w)
    write_csv(out/'sample_size_reconstruction.csv',[{k:str(v) for k,v in s.items()}])
    write_csv(out/'figure_02_plot_data.csv',plot2)
    write_csv(out/'figure_03_plot_data.csv',plot3)
    write_csv(out/'figure_04_plot_data.csv',plot4)
    render_figures(out,s,plot2,plot3,plot4)
    report=make_report(s,c,r,es,w)
    (out/'reconstruction_results.txt').write_text(report,encoding='utf-8')
    (ROOT/'reconstruction_results.txt').write_text(report,encoding='utf-8')
    print(report)
    print(f'Wrote {len(list(out.glob("*.png")))} PNGs + CSVs in {out}')


if __name__ == '__main__':
    main()
