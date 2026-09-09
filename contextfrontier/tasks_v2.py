"""Nested records and paired prompt wording, preserving games-v1 unchanged."""
from dataclasses import asdict, dataclass
import random
import string
from .tasks import digest, SYSTEM

VERSION='games-v2'

@dataclass(frozen=True)
class CaseV2:
    id:str
    task:str
    seed:int
    n:int
    k:int
    depth:float
    absent:bool
    system:str
    prompt:str
    expected:list[str]
    evidence:list[dict]
    conditions:dict
    nested_family:str
    version:str=VERSION
    def to_dict(self):return asdict(self)


def make_case(task,*,seed,n,k=2,depth=.5,absent=False,query_style='baseline'):
    if task not in ('needle','two_hop','updates') or type(n) is not int or not 4<=n<=100000:
        raise ValueError('Unsupported task or record count')
    if type(k) is not int or not 1<=k<=32 or not 0<=depth<=1:
        raise ValueError('Invalid symbols/depth')
    if query_style not in ('baseline','reminder') or (absent and task!='needle'):
        raise ValueError('Invalid query style or absence control')
    # N, depth and wording are intentionally absent from the random seed.
    family=digest([VERSION,task,seed,k]);rng=random.Random(family);used=set()
    def code():
        while True:
            value='|'.join(''.join(rng.choices(string.ascii_uppercase,k=4)) for _ in range(k))
            if value not in used:used.add(value);return value
    pairs=[(code(),code()) for _ in range(n)]
    key,value=pairs[0]
    if task=='needle':
        records=pairs[1:];records.insert(round(depth*(n-1)),pairs[0])
        lines=[f'{a} => {b}' for a,b in records]
        query=code() if absent else key
        question=f'What is the value for {query}?'
        expected=['UNKNOWN' if absent else value]
        selected=[] if absent else [f'{key} => {value}']
        rule='Each key has exactly one value.';layout='target_depth'
    else:
        depth=.25  # nominal position of the first/current evidence record
        if task=='two_hop':
            first=f'{key} => {value}';second=f'{value} => {pairs[1][1]}'
            distractors=[f'{a} => {b}' for a,b in pairs[2:]]
            rule='Records form directed links. Follow the number of arrows requested.'
            question=f'Starting at {key}, follow exactly TWO arrows. What value do you reach?'
            expected=[pairs[1][1]]
        else:
            # Distractor revisions use a separate RNG: adding records cannot alter
            # revisions of earlier records or either target fact.
            revisions=random.Random(digest([family,'revisions']))
            first=f'revision 9: {key} => {value}';second=f'revision 2: {key} => {pairs[1][1]}'
            distractors=[f'revision {revisions.randrange(1,10)}: {a} => {b}' for a,b in pairs[2:]]
            rule='The highest revision number for a key is current, regardless of line order.'
            question=f'What is the CURRENT value for {key}?';expected=[value]
        # Exact final line positions; position and separation are fixed in the
        # wording experiment, whose only manipulated variable is query_style.
        positions=[round(.25*(n-1)),round(.75*(n-1))]
        lines=[];other=iter(distractors)
        for i in range(n):lines.append(first if i==positions[0] else second if i==positions[1] else next(other))
        selected=[first,second];layout='quarter_three_quarters'
    if query_style=='reminder':
        question+='\n\nFinal answer format: Return only the requested code, on one line, with no explanation, labels, or Markdown.'
    header=f'{rule}\n\nBEGIN RECORDS\n';prompt=header+'\n'.join(lines)+'\nEND RECORDS\n\n'+question
    evidence=[];offset=len(header)
    for i,line in enumerate(lines):
        if line in selected:evidence.append(dict(line=i,text=line,char_start=offset,char_end=offset+len(line),record_depth=i/(n-1)))
        offset+=len(line)+1
    params=dict(task=task,seed=seed,n=n,k=k,depth=depth,absent=absent,system=SYSTEM,prompt=prompt,
                expected=expected,evidence=evidence,conditions=dict(query_style=query_style,evidence_layout=layout,sampling='nested_records'),
                nested_family=family,version=VERSION)
    return CaseV2(id=digest(params),**params)


def make_suite(config):
    cases=[]
    for block in config['blocks']:
        for seed in block['seeds']:
            for depth in block.get('depths',[.5]):
                for style in block.get('query_styles',['baseline']):
                    cases.append(make_case(block['task'],seed=seed,n=block['n'],k=block.get('k',2),depth=depth,
                                           absent=block.get('absent',False),query_style=style))
    if len({c.id for c in cases})!=len(cases):raise ValueError('Duplicate v2 cases')
    return cases
