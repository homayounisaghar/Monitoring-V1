import { auth, defineMcp } from "@lovable.dev/mcp-js";
import getCurrentSessionTool from "./tools/get-current-session";
import listSquadTool from "./tools/list-squad";
import getAttentionFlagsTool from "./tools/get-attention-flags";

// The OAuth issuer MUST be the direct Supabase host, not the .lovable.cloud
// proxy. Read the project ref from the Vite-inlined env literal.
const projectRef = import.meta.env.VITE_SUPABASE_PROJECT_ID ?? "project-ref-unset";

export default defineMcp({
  name: "st2-mcp",
  title: "ST2 — Post-session monitoring",
  version: "0.1.0",
  instructions:
    "Read-only access to the ST2 post-session monitoring app. Use `get_current_session` for the selected session's metadata, `list_squad` for every athlete on that session, and `get_attention_flags` for the current Tier-1 flags.",
  auth: auth.oauth.issuer({
    issuer: `https://${projectRef}.supabase.co/auth/v1`,
    acceptedAudiences: "authenticated",
  }),
  tools: [getCurrentSessionTool, listSquadTool, getAttentionFlagsTool],
});
