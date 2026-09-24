# Wake Handshake Prototype

Independent Android MVP inspired by the accepted WebView Dashboard speech path. It does not update or modify the Dashboard or Persian Voice Keyboard.

Flow:

`operator speech -> Perplexity session credential -> Soniox realtime STT -> local silence hold -> latest emitted chunk -> wake classification -> local ding(s)`

Behavior in v0.1.1:
- editable wake phrase, default `خط باز`;
- local silence choices `0 / 800 / 1200 / 1500 / 2000 / 2500 ms`;
- each committed chunk replaces the prior displayed chunk;
- exact wake phrase, or wake phrase followed only by whitespace/punctuation, produces **one ding**;
- wake phrase followed by actual letter/digit content produces **two dings**;
- wake phrase occurring later in the chunk does not trigger;
- optional **Keep listening when screen is locked** checkbox:
  - if a listening session is already active and the phone is then locked/screen-off, a microphone foreground service + partial wake lock keeps the session alive;
  - switching to another app while the screen remains on still stops listening;
  - the microphone foreground service is started while the Activity is visible, before the lock transition;
- no TTS;
- recognized transcript is not intentionally persisted or logged;
- visible Perplexity setup uses normal user sign-in/verification only;
- UI uses system-bar/display-cutout insets and a scroll container for safe-area access.

Identity:
- package: `com.homayounisaghar.wakehandshakeprobe`
- versionCode: `2`
- versionName: `0.1.1`
- expected signer certificate SHA-256: `b8bfbfb9d7962afd739c990d661e94c457dfb37cb6ab8516cdb54c3f95b9d2ec`
- source/build branch: `project/wake-handshake-prototype`

The repository workflow builds an unsigned aligned release signing kit. Final signing is a separate promotion step with the pinned prototype signer; signer private material and credentials are not committed to Git. The public certificate pin is stored in `signing/EXPECTED_SIGNING_SHA256.txt`.
