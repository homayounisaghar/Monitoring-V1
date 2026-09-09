#!/usr/bin/env python3
from pathlib import Path

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'

tracker=(PKG/'CorrelatedAssistantReplyTrackerV1.java').read_text()
wait=(PKG/'AssistantReplyWaitJournalV1.java').read_text()
speech=(PKG/'SpeechOutputSessionV1.java').read_text()
chunk=(PKG/'SpeechTextChunkerV1.java').read_text()

for x in [
    'WAIT_USER_RECEIPT','WAIT_ASSISTANT_START','WAIT_ASSISTANT_STABLE','CAPTURED','UNCERTAIN',
    'expectedUserExactHash.equals(s.lastUserExactHash)',
    's.userTurnCount >= baselineUserTurnCount + 1',
    's.assistantTurnCount >= baselineAssistantTurnCount + 1',
    's.stopCandidateCount > 0',
    's.completionCandidateCount < 1',
    'stableHits < 2',
    'ExactTextV1.sha256(s.lastAssistantExactText)',
    'CORRELATED_USER_NO_LONGER_LAST_USER',
]: assert x in tracker,x
assert 'interpret' not in tracker.lower()

for x in [
    'target_path_hash','expected_user_exact_hash','baseline_user_turn_count','baseline_assistant_turn_count',
    'expires_at_epoch_ms','REPLY_CAPTURED','reply_exact_sha256','restoreTracker','applyObservation',
    'ExactTextV1.sha256(text).equals(digest)',
]: assert x in wait,x

for x in [
    'interface SpeechOutputProviderFactoryV1',
    'AndroidTtsSpeechOutputFactoryV1',
    'SpeechOutputSessionV1 implements SpeechOutputAdapterV1.Listener',
    'SpeechTextChunkerV1.chunk',
    'sourceDigest = ExactTextV1.sha256(canonical)',
    'onSessionDone',
    'onSessionFailed',
    'activeUtteranceId = sessionId + ":chunk:" + index',
]: assert x in speech,x

for x in ['bestBoundary','\\n\\n','c == \'؟\'','Character.isWhitespace']:
    assert x in chunk,x
assert 'summar' not in chunk.lower()

print('PASS reply-correlation + receipt-bearing speech-output infrastructure v1 invariants')
