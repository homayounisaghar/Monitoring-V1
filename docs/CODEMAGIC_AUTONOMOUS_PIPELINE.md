# Codemagic Autonomous Build/Delivery Runbook

This file is the canonical operational memory for handing the Pebble/Onshape Codemagic workflow between ChatGPT conversations. Do not rediscover this setup from scratch unless the repository state proves it changed.

## Target autonomous loop

1. Assistant edits source/config in GitHub.
2. Assistant pushes to the configured development branch.
3. GitHub webhook triggers Codemagic.
4. Codemagic reports the result through GitHub Checks.
5. Assistant reads the result and diagnostics.
6. On failure, assistant fixes source or `codemagic.yaml`, pushes again, and repeats without routine user checkpoints.
7. On success, Codemagic signs with the persistent Android signing identity.
8. Codemagic publishes the signed APK to GitHub as a prerelease asset and mirrors latest APK + metadata to a delivery branch.
9. Assistant retrieves the mirrored binary from GitHub, materializes it into `/mnt/data`, verifies it, and returns a `sandbox:/mnt/data/...apk` link in ChatGPT.

GitHub Actions is not the primary Android build system. Codemagic is.

## User intervention boundary

Only ask the user for action when one of these is genuinely required:

- a click in logged-in Codemagic UI;
- a secret/credential that only the user can enter;
- permission changes in GitHub/Codemagic;
- adding/replacing a signing identity;
- an external login/session that cannot be automated.

Do not use the user as a relay for GitHub commits, Codemagic status, artifact download, or file transfer when tools can handle it.

## Shared Codemagic variable group

Expected global group:

- `codemagic_api`

Known variables:

- `CM_API_TOKEN` — used to obtain temporary public Codemagic artifact URLs when needed.
- `GITHUB_TOKEN` — GitHub fine-grained PAT used for release/Contents API write operations.

Important UI detail: these may live under **Personal account settings → codemagic.yaml settings → Global variables and secrets**, even when an individual application's Environment variables page says `No existing variables`.

Never print, commit, or paste token values into chat/source control.

## GitHub token model

`GITHUB_TOKEN` is a GitHub fine-grained Personal Access Token stored only in Codemagic as a Secret.

Minimum permissions used by the known-good Onshape delivery pipeline:

- Repository access: only selected repositories
- `Contents`: Read and write
- `Metadata`: Read-only (required by GitHub)
- Account permissions: none

The token must include each repository that needs publishing access. For Pebble it must include:

- `homayounisaghar/Monitoring-V1`

The same token can also include:

- `homayounisaghar/capability-fabric`

Do not assume Codemagic repository authentication / checkout credentials are exported to the shell or have release-write permission. Codemagic's GitHub App can write Checks independently of the shell token.

## Pebble Chat Bridge — current setup

Repository:

- `homayounisaghar/Monitoring-V1`

Development branch:

- `build/pebble-chat-bridge-v019`

Codemagic workflow:

- `pebble-bridge-v019`
- build file: root `codemagic.yaml`

Permanent Android signing identity:

- `pebble_bridge`

Environment imports already expected:

- group `codemagic_api`
- signing identity `pebble_bridge`
- Java 17

Known existing working pieces:

- GitHub repository connection/authentication;
- webhook;
- GitHub push → Codemagic build → GitHub Check;
- Android release build;
- persistent signing;
- certificate verification;
- full build log / diagnostics;
- `CM_API_TOKEN` based temporary artifact URL generation.

## Desired Pebble delivery architecture

Once `GITHUB_TOKEN` has `Monitoring-V1` repository access, copy the known-good Onshape publishing pattern:

1. create/find a prerelease tag such as `pebble-v0.19-<short-commit>`;
2. upload the signed APK as a GitHub release asset;
3. update/create delivery branch `ci/pebble-apk-delivery`;
4. write `.ci/latest-pebble-build.json` with commit/build/release/SHA/signing metadata;
5. mirror the binary to `.ci/latest-pebble.apk` through GitHub Contents API.

The binary mirror is intentional: the assistant can fetch it as base64 through GitHub tools, decode it into `/mnt/data`, verify SHA/integrity, and hand the real APK back through a sandbox link.

The older experimental credential probes (`PEBBLE_GITHUB_TOKEN`, `GITHUB_TOKEN`, `GH_TOKEN`, `CM_GITHUB_TOKEN`) and commit-status relay are not the desired final architecture once the correctly scoped shared `GITHUB_TOKEN` is available.

## Known-good Onshape reference implementation

Reference repository:

- `homayounisaghar/capability-fabric`

Reference branch:

- `experiment/onshape-native-session-bridge`

Reference signing identity:

- `onshape_bridge_dev`

Reference delivery branch:

- `ci/onshape-apk-delivery`

Reference mirrored files:

- `.ci/latest-onshape-build.json`
- `.ci/latest-onshape.apk`

Reference Codemagic app ID:

- `6a94a8fef6653c0fa45989f9`

When uncertain about delivery design, inspect that repository's current `codemagic.yaml` before inventing a new mechanism.

## Assistant checklist when resuming in a new chat

Before asking the user anything:

1. Read this runbook.
2. Inspect current `codemagic.yaml` on `build/pebble-chat-bridge-v019`.
3. Verify current branch / Draft PR / check-runs.
4. Verify the latest Codemagic check and diagnostics.
5. Verify whether `ci/pebble-apk-delivery` exists and inspect metadata before claiming publishing is broken.
6. Use GitHub tools to edit/push/check/retrieve binaries.
7. Ask the user only for missing UI permissions, token repository access, secrets, or signing setup.

## Security rules

- Never commit signing private keys or PAT values.
- Never ask the user to paste secrets into chat.
- Keep tokens in Codemagic Secret variables only.
