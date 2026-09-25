# Wake Handshake Prototype

Independent Android MVP inspired by the accepted WebView Dashboard speech path. It does not update or modify the Dashboard or Persian Voice Keyboard.

Flow:

`operator speech -> Perplexity session credential -> Soniox realtime STT -> phase-selected local silence hold -> latest emitted chunk -> WAKE/COMMAND state machine -> local ding(s)`

Behavior in v0.1.7:
- two editable wake aliases: Wake phrase 1 keeps the existing/default value (`خط باز` by default), and Wake phrase 2 is optional for an alternate transcription such as `Mika` alongside `میکا`;
- wake matching is case-insensitive for scripts with letter case (`Mika`, `mika`, `MIKA` all match the same alias) while retaining the existing Persian/Arabic normalization and punctuation/whitespace boundary rules;
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

Perplexity/session rollback retained from v0.1.6:
- the v0.1.5 default-UA/session-reset experiment is fully removed;
- `MainActivity.java`, `SetupActivity.java`, `LockedListeningService.java`, and `AndroidManifest.xml` are restored exactly to the pre-v0.1.5 runtime baseline at commit `d710b9b975846280572fbf833a0bfbdfc0e40142`;
- that baseline uses the original hard-coded mobile SamsungBrowser User-Agent and original cookie/session behavior;
- there is no automatic cookie/WebStorage clearing and no manual session-reset button;
- normal Perplexity sign-in / human verification remains user-driven.

Identity:
- package: `com.homayounisaghar.wakehandshakeprobe`
- versionCode: `8`
- versionName: `0.1.7`
- expected signer certificate SHA-256: `98fb854378d390f32267acfbc23e82be6d267cae7049b3c7ae0894752897080c`
- source/build branch: `project/wake-handshake-prototype`

Signer line note: v0.1.7 was installed and accepted by the operator on 2026-09-25 with signer v2 (`98fb854378d390f32267acfbc23e82be6d267cae7049b3c7ae0894752897080c`). The earlier signer line is retired for future updates. Future successors must keep this v2 signer and use a higher versionCode.\n\nThe repository workflow builds an unsigned aligned release signing kit. Final signing is a separate promotion step with the pinned prototype signer; signer private material and credentials are not committed to Git.
