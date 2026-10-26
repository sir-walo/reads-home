"""Offline reading metrics (same idea as /reading/calculate_metrics in READS)."""
import re
from difflib import SequenceMatcher


def words_of(text):
    return [w for w in re.sub(r"[^\w\s'’-]", " ", text.lower()).split() if w]


def calculate(original, spoken, seconds):
    orig = words_of(original)
    spk_raw = words_of(spoken)

    # repetitions = same word said twice in a row; keep one copy for alignment
    spk, repetitions = [], 0
    for w in spk_raw:
        if spk and spk[-1] == w:
            repetitions += 1
        else:
            spk.append(w)

    correct = omissions = insertions = mispronounced = 0
    orig_marks, spk_marks = [], []
    sm = SequenceMatcher(a=orig, b=spk, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            correct += i2 - i1
            orig_marks += [("correct", w) for w in orig[i1:i2]]
            spk_marks += [("correct", w) for w in spk[j1:j2]]
        elif tag == "delete":
            omissions += i2 - i1
            orig_marks += [("omitted", w) for w in orig[i1:i2]]
        elif tag == "insert":
            insertions += j2 - j1
            spk_marks += [("inserted", w) for w in spk[j1:j2]]
        else:  # replace -> pair up as mispronounced, rest omitted / inserted
            n = min(i2 - i1, j2 - j1)
            mispronounced += n
            orig_marks += [("mispronounced", w) for w in orig[i1:i1 + n]]
            spk_marks += [("mispronounced", w) for w in spk[j1:j1 + n]]
            omissions += (i2 - i1) - n
            orig_marks += [("omitted", w) for w in orig[i1 + n:i2]]
            insertions += (j2 - j1) - n
            spk_marks += [("inserted", w) for w in spk[j1 + n:j2]]

    minutes = max(seconds, 1) / 60.0
    return {
        "wpm": round(len(spk_raw) / minutes),
        "accuracy": round(100.0 * correct / len(orig), 1) if orig else 0,
        "omissions": omissions,
        "insertions": insertions,
        "repetitions": repetitions,
        "mispronounced": mispronounced,
        "original": orig_marks,
        "spoken": spk_marks,
    }
