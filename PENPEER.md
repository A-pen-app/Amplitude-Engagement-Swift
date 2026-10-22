# Penpeer fork

Fork of [amplitude/Amplitude-Engagement-Swift](https://github.com/amplitude/Amplitude-Engagement-Swift) with one patch to `engagement.js`. Used by PenpeerKit until Amplitude ships a fix; switch back to upstream then.

## The bug

Card-embed surveys (`amplitudeView` / `amplitudeTarget`) never submit answers on iOS:

- For card steps, `engagement.js` skips `markSeen` / `saveSeen` / `lockLifecycleId` / `reportSeen` and waits for a `STEP_VISIBLE` event.
- Nothing sends `STEP_VISIBLE`, neither the JS nor any native → JS call.
- With no lifecycle ID, `reportSurveyResponse` returns early ("Cannot submit survey response: no locked lifecycle ID").
- Result: `[Guides-Surveys] Survey Viewed` and `Survey Submitted` never fire, and answers never reach Amplitude. `Survey Completed` still fires.

Present in 4.1.0 and 4.2.0, whose `engagement.js` files are identical.

## The patch

`scripts/penpeer-card-visibility-patch.py` removes the two `!isCardStep` guards, so card steps lock a lifecycle ID and report "viewed" when they render.

Side effect: a card counts as viewed when it is rendered, even before it is scrolled into view.

Verified on the iOS simulator (A-Pen, survey in the post list and in a plain SwiftUI screen). The full sequence fires with a non-empty lifecycle ID: Viewed → Submitted (with `Survey Response`) → Step Completed → Completed.

## Releases

Tags are `<upstream version>-penpeer.<n>`, for example `4.1.0-penpeer.1`. Consumers pin them with `exact:`.

To move to a new upstream release:

1. `git fetch upstream --tags`
2. Branch from the upstream tag and cherry-pick the Penpeer commit, or rerun the script.
3. Run `python3 scripts/penpeer-card-visibility-patch.py`, then rerun it with `--check`.
4. Tag `<version>-penpeer.1` and push.
