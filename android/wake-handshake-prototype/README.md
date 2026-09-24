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
- expected signer certificate SHA-256: `b8bfbfb9d7962afd739c990d661e94c457dfb37cb6ab8516cdb54c3f95b9d2ec`
- source/build branch: `project/wake-handshake-prototype`

The repository workflow builds an unsigned release signing kit. Final signing is a separate promotion step with the durable prototype signer; signer private material is not committed to Git.
