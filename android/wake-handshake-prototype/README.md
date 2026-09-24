# Wake Handshake Prototype

Independent Android MVP inspired by the accepted WebView Dashboard speech path. It does not update or modify the Dashboard or Persian Voice Keyboard.

Flow:

`operator speech -> Perplexity session credential -> Soniox realtime STT -> local silence hold -> latest emitted chunk -> wake-prefix test -> ding`

Behavior:
- editable wake phrase, default `خط باز`;
- local silence choices 800 / 1200 / 1500 / 2000 / 2500 ms;
- each committed chunk replaces the prior displayed chunk;
- wake reaction fires when the emitted chunk is exactly the wake phrase or begins with it at a word/punctuation boundary;
- response is a short local ding; no TTS;
- recognized transcript is not persisted or logged;
- leaving the Activity stops/relinquishes capture;
- visible Perplexity setup uses normal user sign-in/verification only.

Identity:
- package: `com.homayounisaghar.wakehandshakeprobe`
- versionCode: `1`
- versionName: `0.1.0`
- expected signer certificate SHA-256: `e59c1bea6876f1c1d0aba3c9f23d788e93f3ca015cd0e8371e3b80c20c020a0d`
- source/build branch: `project/wake-handshake-prototype`

The repository workflow builds an unsigned release signing kit. Final signing is a separate promotion step with the pinned prototype signer; signer private material and credentials are not committed to Git. The public certificate pin is also stored in `signing/EXPECTED_SIGNING_SHA256.txt`.
