# Monitoring-V1

Status: public supporting/build/test repository — **not canonical continuity state**.

This repository is used as an implementation, build, test, or evidence workspace by some projects whose authoritative current state lives in the private continuity root:

`homayounisaghar/capability-fabric`

A replacement AI must not infer the user's current project frontier from this repository's `main` branch or miscellaneous historical files. Resolve active work through `capability-fabric/WORK_REGISTRY.md` and follow the exact branch/commit/run referenced by the relevant `PROJECT_STATE.md`.

Known current supporting uses include Pebble/ChatGPT native capability probes and the public test-build path for Onshape MouseBridge.

## Security boundary
This repository is public.

- Never commit passwords, private keys, API tokens, session cookies, recovery codes, private user state, or other live secrets.
- Local `.env` files are ignored; use an `.env.example` containing names/placeholders only when configuration documentation is needed.
- Public/publishable client configuration is not continuity authority and should still be kept out of committed local environment files when not needed.

## Continuity rule
If a project becomes dependent on an artifact here, its canonical project state must record the exact repository, ref/commit/run/artifact and the operational consequence. Do not rely on conversational memory to rediscover it.
