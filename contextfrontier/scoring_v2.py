"""Predeclared answer extraction; the parser never sees the expected answer."""
import re
from .scoring import grade as strict_grade
VERSION='score-v2'


def final_line_answer(text,k):
    lines=[line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:return None
    candidate=lines[-1]
    # Only complete single-line backtick/bold wrappers are normalized.
    for marker in ('**','`'):
        if candidate.startswith(marker) and candidate.endswith(marker) and len(candidate)>2*len(marker):
            candidate=candidate[len(marker):-len(marker)].strip()
    pattern=r'(?:UNKNOWN|[A-Z]{4}(?:\|[A-Z]{4}){'+str(k-1)+r'})'
    return candidate if re.fullmatch(pattern,candidate) else None


def grade(text,expected,*,symbols_per_answer=None):
    k=symbols_per_answer or len(expected[0].split('|'))
    result=strict_grade(text,expected,symbols_per_answer=k)
    answer=final_line_answer(text,k)
    result.update(scoring_version=VERSION,final_line_answer=answer,
                  final_line_correct=len(expected)==1 and answer==expected[0])
    return result
