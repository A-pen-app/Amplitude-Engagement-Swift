#!/usr/bin/env python3
"""Penpeer patch: let card-embed survey steps lock a lifecycle ID when they render.

Upstream engagement.js skips markSeen/saveSeen/lockLifecycleId/reportSeen for card
steps and waits for a STEP_VISIBLE event that neither the JS nor the native SDK ever
sends. Without a lifecycle ID, reportSurveyResponse drops every answer, so
`[Guides-Surveys] Survey Viewed` and `Survey Submitted` never fire for card embeds.

    python3 scripts/penpeer-card-visibility-patch.py          # apply (idempotent)
    python3 scripts/penpeer-card-visibility-patch.py --check  # exit 1 if not patched

After pulling a new upstream release, run it without --check. If upstream changed
the code around the guards, it fails loudly instead of leaving the fix half applied.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = sorted(ROOT.glob("Sources/AmplitudeEngagementSwift.xcframework/*/AmplitudeEngagementSwift.framework/engagement.js"))

# (unpatched, patched) pairs; each unpatched string must occur exactly once.
EDITS = [
    # "Render Loop" entry: markSeen, saveSeen, lockLifecycleId.
    ('&&!r({type:"isCardStep"})&&(n({type:"markSeen"})', '&&(n({type:"markSeen"})'),
    # "Rendering" entry: reportSeen (Survey Viewed), markStepViewed.
    ('&&!r({type:"isCardStep"})&&(n({type:"reportSeen"})', '&&(n({type:"reportSeen"})'),
]


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    if not FILES:
        print("error: no engagement.js found under Sources/")
        return 1
    ok = True
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for old, new in EDITS:
            if text.count(old) == 1:
                if check_only:
                    print(f"not patched: {path.relative_to(ROOT)}")
                    ok = False
                    continue
                text = text.replace(old, new)
            elif text.count(old) == 0 and new in text:
                continue  # already patched
            else:
                print(f"error: guard not found as expected in {path.relative_to(ROOT)}: {old}")
                ok = False
        if not check_only:
            path.write_text(text, encoding="utf-8")
    if ok:
        print(f"{'verified' if check_only else 'patched'}: {len(FILES)} engagement.js file(s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
