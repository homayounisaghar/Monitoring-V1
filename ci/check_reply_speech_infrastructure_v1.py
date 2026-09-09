#!/usr/bin/env python3
from pathlib import Path

ROOT=Path('runtime_probes/chatgpt-webview-stable-probe')
PKG=ROOT/'app/src/main/java/com/homayounisaghar/chatgptwebviewprobe'

tracker=(PKG/'CorrelatedAssistantReplyTrackerV1.java').read_text()
wait=(PKG/'AssistantReplyWaitJournalV1.java').read_text()
speech=(PKG/'SpeechOutputSessionV1.java').read_text()
chunk=(PKG/'SpeechTextChunkerV1.java').read_text()
temp_dom=(PKG/'TemporaryChatDomV1.java').read_text()
temp_ctl=(PKG/'DisposablePlannerLifecycleControllerV1.java').read_text()
temp_journal=(PKG/'TemporaryPlannerJournalV1.java').read_text()

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
for forbidden in [
    'Levenshtein', 'fuzzyMatch', 'semanticScore', 'guessTarget',
    'startsWith("آسم', 'contains("آسم', 'contains("send to', 'contains("بفرست'
]: assert forbidden not in tracker,forbidden

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
    'onSessionDone','onSessionFailed',
    'activeUtteranceId = sessionId + ":chunk:" + index',
]: assert x in speech,x
for x in ['bestBoundary','\\n\\n','c == \'؟\'','Character.isWhitespace']:
    assert x in chunk,x
assert 'summarize(' not in chunk.lower() and 'summary=' not in chunk.lower()

for x in [
    'TemporaryChatSignaturesV1.NORMAL_LABEL_HASH',
    'TemporaryChatSignaturesV1.TEMP_LABEL_HASH',
    "reason:'EXACT_SIGNATURE_COUNT'",
    "urlhint!==EU",
    't.e.click()',
    'match_count:1',
]: assert x in temp_dom,x
assert temp_dom.count('t.e.click()')==1
for bad in ['elementFromPoint','document.evaluate','XPathResult','dispatchTouchEvent','performClick(']:
    assert bad not in temp_dom,bad

for x in [
    'REQUIRED_STABLE_HITS = 2',
    'pollNormalForEntry', 'dispatchEntry', 'pollTempReceipt',
    'beforePlannerSend', 'afterPlannerSendObserved', 'persistResultAndClose',
    'journal.persistResultReceipt', 'pollTempForExit', 'dispatchExit', 'pollNormalRestore',
    'TEMP_ENTRY_DISPATCH_UNCERTAIN_NO_REPLAY',
    'TEMP_EXIT_DISPATCH_UNCERTAIN_NO_REPLAY',
    'NORMAL_RESTORE_RECEIPT_UNRESOLVED_NO_REPLAY',
]: assert x in temp_ctl,x
assert 'persistResultAndClose' in temp_ctl
assert temp_ctl.index('journal.persistResultReceipt') < temp_ctl.index('pollTempForExit')

for x in [
    'PLANNER_SEND_IN_FLIGHT','WAITING_RESULT','RESULT_PERSISTED','CLAIMED_BEFORE_EXIT',
    'RECOVERY_RESULT_ONLY','RECOVERY_CLEANUP_ONLY','planner_dispatch_count',
    'persistResultReceipt','markCleanupUncertain',
]: assert x in temp_journal,x
assert 'planner_dispatch_count", 1' in temp_journal

print('PASS correlated reply + speech output + disposable Planner infrastructure v1 invariants')
