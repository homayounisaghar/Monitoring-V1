import { defineTool } from "@lovable.dev/mcp-js";

export default defineTool({
  name: "get_current_session",
  title: "Get current session",
  description:
    "Return the currently selected ST2 session — kind, opponent/label, date, duration, halves, venue, weather, and result.",
  inputSchema: {},
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async () => {
    const { currentSession } = await import("@/lib/session-data");
    return {
      content: [{ type: "text", text: JSON.stringify(currentSession, null, 2) }],
      structuredContent: { session: currentSession },
    };
  },
});
