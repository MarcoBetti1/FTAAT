import json
import pytest
from contextfrontier.tasks import make_case, make_suite, TASKS
from contextfrontier.scoring import grade, wilson

@pytest.mark.parametrize("task", TASKS)
@pytest.mark.parametrize("depth", [0, .1, .5, .9, 1])
def test_generated_answers_follow_records(task, depth):
    case = make_case(task, n=20, seed=8, depth=depth)
    records = case.prompt.split("BEGIN RECORDS\n")[1].split("\nEND RECORDS")[0].splitlines()
    assert len(records) == 20
    assert case == make_case(task, n=20, seed=8, depth=depth)
    assert grade("\n".join(case.expected), case.expected)["exact"]
    for e in case.evidence:
        assert case.prompt[e['char_start']:e['char_end']] == e['text'] == records[e['line']]
    if task == "updates":
        revisions = {}
        for line in records:
            prefix, assignment = line.split(": ")
            key, val = assignment.split(" => ")
            rev = int(prefix.split()[1])
            if rev > revisions.get(key, (-1, None))[0]:
                revisions[key] = (rev, val)
        q = case.prompt.rsplit("for ", 1)[1].rstrip("?")
        assert revisions[q][1] == case.expected[0]
    else:
        mapping = dict(line.split(" => ") for line in records)
        if task == "needle":
            q = case.prompt.rsplit("for ", 1)[1].rstrip("?")
            assert mapping[q] == case.expected[0]
        elif task == "two_hop":
            q = case.prompt.split("Starting at ")[1].split(",")[0]
            assert mapping[mapping[q]] == case.expected[0]
        else:
            keys = case.prompt.split("in this order:\n")[1].splitlines()
            assert [mapping[k] for k in keys] == case.expected

def test_absent_and_position_controls():
    absent = make_case("needle", absent=True)
    assert absent.expected == ["UNKNOWN"]
    assert absent.evidence == []
    a, b = [make_case("needle", depth=d) for d in (0, 1)]
    assert a.expected == b.expected
    assert a.evidence[0]['text'] == b.evidence[0]['text']

@pytest.mark.parametrize("text,expected,exact,acc", [
    ("A", ["A", "B"], False, .5), ("", ["A"], False, 0),
    ("A\nA", ["A", "B"], False, .5), ("A\nEXTRA", ["A"], False, 1),
    ("A", ["A|B"], False, 0), (" A\nB\n", ["A", "B"], True, 1),
])
def test_grading_denominators(text, expected, exact, acc):
    result = grade(text, expected)
    assert result['exact'] is exact
    assert result['sequence_accuracy'] == acc

def test_symbol_denominator_and_intervals():
    assert grade("A", ["A|B"])["symbol_accuracy"] == .5
    assert wilson(0, 0) is None
    assert wilson(3, 3)[0] < .5
    assert wilson(0, 3)[1] > .5
    assert wilson(100, 100)[0] > .95
