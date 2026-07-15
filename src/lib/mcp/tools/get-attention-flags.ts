import { defineTool } from "@lovable.dev/mcp-js";

export default defineTool({
  name: "get_attention_flags",
  title: "Get attention flags",
  description:
    "Return the current session's Tier-1 attention flags — athletes that need attention, their severity (escalate/notice), the reason, and the underlying read (value-on-track delta or gap between external and internal load).",
  inputSchema: {},
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async () => {
    const { TIER1_ROWS_DEFAULT, sortTier1 } = await import("@/lib/session-flags");
    const rows = sortTier1(TIER1_ROWS_DEFAULT);
    return {
      content: [{ type: "text", text: JSON.stringify(rows, null, 2) }],
      structuredContent: { flags: rows },
    };
  },
});
