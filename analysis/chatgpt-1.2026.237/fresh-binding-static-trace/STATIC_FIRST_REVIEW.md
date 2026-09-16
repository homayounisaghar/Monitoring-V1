# Fresh-binding static-first review — ChatGPT Android 1.2026.237

Date: 2026-09-03

## Scope
This is a narrow follow-up on the unresolved fresh-conversation binding boundary. It does **not** reopen the closed broad APK census. The design rule from this point is **static-first -> runtime-last**: extract a concrete first-party contract from the exact APK evidence already persisted, then use one bounded runtime harness only to validate that contract.

Exact target remains:
- package `com.openai.chatgpt`
- versionName `1.2026.237`
- versionCode `2623716`
- APK SHA-256 `50e268c50255ab9aa48be49f0ba668c6f8ef97fd208f3826f19056698ea9f5a4`
- signer SHA-256 `b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c`

## Why the method changed
v0.17 did not disprove History binding. Its run reached the official History drawer and then stopped because the harness counted two exact semantic `New chat` nodes: one non-clickable label and one clickable container. The test therefore never switched away, reopened History, selected a conversation row, or verified the marker.

That failure is a useful warning: Accessibility-tree guessing should no longer drive design when the exact application artifacts can narrow the contract first.

## Exact-APK facts already persisted

### 1. A remote/native conversation identifier exists in first-party conversation state
`chatgpt_conversation.valdimodule` contains the persistence module `src/persistence/ChatGPTConversationPersistence.js` and state/lifecycle tokens including:
- `remoteId`
- `activeConversationId`
- `nextConversationId`
- `synchronizeConversationIdentifiers`
- `remoteConversationHistory`
- `pinnedRemoteConversationHistory`
- `loadedRemoteConversationIds`
- `externallyOpenedRemoteConversationIds`
- `persistState` / `restorePersistedState`

This is evidence that the first-party conversation layer explicitly distinguishes and synchronizes conversation identifiers. It is not yet an external read-side.

### 2. History rendering has a dedicated accessibility-ID namespace
The same exact conversation module contains the History UI lifecycle and the printable prefix:
- `renderHistoryDrawer`
- `renderHistoryItem`
- `renderHistoryConversation`
- `renderHistoryConversationActions`
- `openConversation`
- `loadConversationContent`
- `chatgpt.history.item.`
- `chatgpt.history.actions.`
- `Open `
- `Actions for `

The strongest unresolved question is therefore no longer merely "is the newest row clickable?". It is: **what value is appended to `chatgpt.history.item.` at runtime, and is it a stable/native conversation identifier or another deterministic locator?**

No claim is made here that the suffix equals `remoteId`; that requires data-flow proof or exact on-device correlation.

### 3. Rename is real but secondary
The exact conversation module also contains:
- `renderConversationRename`
- `beginConversationRename`
- `commitConversationRename`
- `renameRemoteConversationHistory`
- `invalidateConversationHistoryRequests`

Rename remains a possible fallback locator, but it should not be the next first choice until the existing History accessibility-ID boundary is tested. Rename also introduces an unnecessary mutation if a stable first-party row identifier is already exposed.

### 4. The official conversation-history service is ID-bearing first-party machinery
`chatgpt_services.valdimodule` contains `src/conversations/ChatGPTConversationHistoryClient.js` with:
- `loadConversations`
- `loadPinnedConversations`
- `loadConversation`
- `renameConversation`
- `deleteConversation`
- `setConversationPinned`
- `updateConversation`
- `/backend-api/conversations`
- `/backend-api/conversation`
- `/backend-api/pins`

Its decoder vocabulary includes History item timestamps/snippet fields (`create_time`, `update_time`, `snippet`, etc.). The companion must **not** call these private endpoints; their relevance is only to understand the first-party data model and UI boundary.

### 5. A native conversation ID is known to cross an Android Intent boundary in the bubble path
Exact JADX evidence shows `com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID` being written to and read from first-party Intents/PendingIntents for conversation-bubble / screen-share flows.

This proves ChatGPT has at least one Android-native ID transport boundary. It is **special-path evidence**, not proof that ordinary chats expose the same boundary. Do not restart blind notification/bubble polling from this fact.

### 6. Public `/c/<id>` reopen remains the strongest verifier
The exported `ChatGptDeeplinkActivity` accepts the official ChatGPT conversation route, and real-device work already proved that a known candidate can be reopened via `https://chatgpt.com/c/<candidate>`. Therefore any candidate extracted from a History row can be tested without trusting its format: neutral state -> explicit `/c/<candidate>` -> exact marker receipt.

## Android/Valdi boundary corroboration
The open-source Valdi Android implementation currently assigns a Valdi node's `accessibilityId` to Android `AccessibilityNodeInfo.viewIdResourceName`.

This is framework-level corroboration, not exact-version proof for ChatGPT's bundled Valdi runtime. It is nevertheless highly relevant because the Capability Lab already requests `flagReportViewIds`, calls `getViewIdResourceName()`, includes view IDs in semantic evidence, and feeds them to the candidate harvester.

Therefore the next device experiment should explicitly preserve and enumerate raw History view IDs rather than infer row identity from title/order alone.

## v0.17 instrumentation consequence
The current Lab was technically capable of seeing a `viewIdResourceName`, but the v0.17 run stopped at the duplicate `New chat` semantic before row-local metadata harvesting. Its `candidateCount=0` is therefore **not** evidence against a History view-ID read-side.

## New runtime priority
The next harness should be observation-first and batched:

1. **Known-row calibration:** open History on an already known/indexed marker conversation and enumerate all visible nodes with raw `viewIdResourceName`, action set, semantic label, parent/child structure, and especially prefixes `chatgpt.history.item.` / `chatgpt.history.actions.`.
2. If one row exposes a candidate suffix, open only the structurally unique corresponding row and verify the known marker. Then, if the suffix is a plausible native ID, separately reopen `/c/<suffix>` and require the same marker.
3. **Fresh-row observation:** create/send exactly one fresh marker, switch away with a unique actionable `New chat` target (deduplicated by actionable target, not duplicate semantic leaves), reopen History, and observe whether a new `chatgpt.history.item.*` row appears immediately.
4. If its suffix is stable and `/c/<suffix>` verifies, native-ID fresh bootstrap is solved. If the suffix is non-native but deterministic, evaluate it as a durable History binding.
5. Only if History accessibility IDs are absent/useless should the next priority become `HistoryTitleBinding`; only after that, warm indexed-conversation pool.

Priority is now:

`verified native ID from History accessibility ID` > `stable exact History row accessibility locator` > `HistoryTitleBinding` > `warm indexed pool`.

Indexed SearchBinding remains the eventual repair locator for conversations after Search indexing catches up.

## Fail-closed rules for the next harness
- No assumption that `chatgpt.history.item.<suffix>` suffix equals native conversation ID until marker-verified.
- No coordinate writes or geometry selection.
- No private backend/API or credential/session extraction.
- No blind walking through unrelated History rows.
- No short-delay Global Search ladder.
- Runtime mutation remains CLAIM-before-side-effect / no blind replay.

## Exact-APK re-download note
A new targeted workflow (`chatgpt-apk-fresh-binding-static-trace.yml`) was added to parse the exact `.valdimodule` archive more deeply. Its first run failed before analysis because the old SwissTransfer source URL used by earlier APK workflows now returns HTTP 404. The SHA-pinned APK was therefore **not** re-downloaded or re-analyzed in that run.

Do not retry that expired transfer link blindly. The conclusions above are based on the already persisted exact-APK artifacts. If bytecode/archive-level data-flow beyond those artifacts becomes necessary, first obtain a durable replacement source for the exact SHA-pinned APK.

## Decision
Do not build a v0.18 merely to fix the v0.17 `New chat` selector. The next executable version should be built only after its contract is centered on the statically justified History accessibility-ID boundary and should batch known-row calibration plus fresh-row observation in one run.
