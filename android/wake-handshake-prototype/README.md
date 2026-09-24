# Wake Handshake Prototype

Independent Android MVP inspired by the accepted WebView Dashboard speech path. It does not update or modify the Dashboard or Persian Voice Keyboard.

Flow:

`operator speech -> Perplexity session credential -> Soniox realtime STT -> phase-selected local silence hold -> latest emitted chunk -> WAKE/COMMAND state machine -> local ding(s)`

Behavior in v0.1.6:
- editable wake phrase, default `خط باز`;
- two independent silence controls with choices `0 / 800 / 1200 / 1500 / 2000 / 2500 ms`:
  - **Wake delay** while searching for the wake phrase;
  - **Command delay** after a wake-only acknowledgement;
- wake-only -> one ding -> COMMAND;
- punctuation/whitespace-only chunks in COMMAND are ignored and COMMAND remains armed;
- first later chunk containing at least one letter/digit -> two dings -> WAKE;
- wake phrase + command in the same chunk -> two dings -> WAKE;
- locked-screen listening behavior remains available;
- latest emitted chunk replaces the prior display;
- no TTS and transcript is not intentionally persisted/logged.

Perplexity/session rollback in v0.1.6:
- the v0.1.5 default-UA/session-reset experiment is fully removed;
- `MainActivity.java`, `SetupActivity.java`, `LockedListeningService.java`, and `AndroidManifest.xml` are restored exactly to the pre-v0.1.5 runtime baseline at commit `d710b9b975846280572fbf833a0bfbdfc0e40142`;
- that baseline uses the original hard-coded mobile SamsungBrowser User-Agent and original cookie/session behavior;
- there is no automatic cookie/WebStorage clearing and no manual session-reset button;
- normal Perplexity sign-in / human verification remains user-driven.

Identity:
- package: `com.homayounisaghar.wakehandshakeprobe`
- versionCode: `7`
- versionName: `0.1.6`
- expected signer certificate SHA-256: `b8bfbfb9d7962afd739c990d661e94c457dfb37cb6ab8516cdb54c3f95b9d2ec`
- source/build branch: `project/wake-handshake-prototype`

The repository workflow builds an unsigned aligned release signing kit. Final signing is a separate promotion step with the pinned prototype signer; signer private material and credentials are not committed to Git.
