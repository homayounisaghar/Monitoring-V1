import { defineTool } from "@lovable.dev/mcp-js";

export default defineTool({
  name: "list_squad",
  title: "List squad",
  description:
    "List every athlete on the current session, including position, participation tag, minutes played, HR coverage, and sRPE submission status.",
  inputSchema: {},
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async () => {
    const { squad } = await import("@/lib/session-data");
    return {
      content: [{ type: "text", text: JSON.stringify(squad, null, 2) }],
      structuredContent: { squad },
    };
  },
});
