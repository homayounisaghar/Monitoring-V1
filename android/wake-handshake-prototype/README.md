# Wake Handshake Prototype

Independent Android MVP inspired by the accepted WebView Dashboard speech path. It does not update or modify the Dashboard or Persian Voice Keyboard.

Flow:

`operator speech -> Perplexity session credential -> Soniox realtime STT -> phase-selected local silence hold -> latest emitted chunk -> wake/command state machine -> local ding(s)`

Behavior in v0.1.2:
- editable wake phrase, default `خط باز`;
- two independent silence controls with the same choices `0 / 800 / 1200 / 1500 / 2000 / 2500 ms`:
  - **Wake delay** while searching for the wake phrase;
  - **Command delay** after a wake-only acknowledgement, while capturing the next command;
- each committed chunk replaces the prior displayed chunk;
- state starts in **WAKE**;
- in WAKE:
  - wake phrase alone, or followed only by whitespace/punctuation -> one ding, then state becomes **COMMAND**;
  - wake phrase followed by actual letter/digit content in the same chunk -> two dings and state stays/returns **WAKE**;
  - wake phrase later in a chunk -> no trigger;
- in COMMAND:
  - the first non-empty committed chunk is treated as the command;
  - it produces two dings;
  - state immediately returns to **WAKE**;
- COMMAND has no separate expiry timeout; it remains armed until the next committed chunk or until listening is stopped/reset;
- optional **Keep listening when screen is locked** behavior from v0.1.1 is preserved:
  - an active session can continue through lock/screen-off using the microphone foreground service + partial wake lock;
  - switching to another app while the screen stays on still stops listening;
- no TTS;
- recognized transcript is not intentionally persisted or logged;
- UI keeps system-bar/display-cutout safe-area handling and scrolling.

Identity:
- package: `com.homayounisaghar.wakehandshakeprobe`
- versionCode: `3`
- versionName: `0.1.2`
- expected signer certificate SHA-256: `b8bfbfb9d7962afd739c990d661e94c457dfb37cb6ab8516cdb54c3f95b9d2ec`
- source/build branch: `project/wake-handshake-prototype`

The repository workflow builds an unsigned aligned release signing kit. Final signing is a separate promotion step with the pinned prototype signer; signer private material and credentials are not committed to Git. The public certificate pin is stored in `signing/EXPECTED_SIGNING_SHA256.txt`.
