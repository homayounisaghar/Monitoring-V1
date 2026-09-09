package com.homayounisaghar.chatgptwebviewprobe;

import java.util.ArrayList;
import java.util.List;

/**
 * Deterministic long-text chunking for speech-output providers with bounded
 * per-utterance input. This is formatting/transport logic only, not semantic
 * summarization. Exact source text remains separately stored in workflow data.
 */
final class SpeechTextChunkerV1 {
    private SpeechTextChunkerV1() {}

    static List<String> chunk(String text, int maxChars) {
        if (maxChars < 64) throw new IllegalArgumentException("maxChars too small");
        String src = ExactTextV1.canonical(text);
        List<String> out = new ArrayList<String>();
        if (src.isEmpty()) return out;

        int start = 0;
        while (start < src.length()) {
            int hardEnd = Math.min(src.length(), start + maxChars);
            if (hardEnd == src.length()) {
                add(out, src.substring(start));
                break;
            }

            int cut = bestBoundary(src, start, hardEnd);
            if (cut <= start) cut = hardEnd;
            add(out, src.substring(start, cut));
            start = cut;
            while (start < src.length() && src.charAt(start) == '\n') start++;
        }
        return out;
    }

    private static int bestBoundary(String s, int start, int hardEnd) {
        // Prefer paragraph / line boundaries, then Persian/Latin sentence ends,
        // then ordinary whitespace. Search only the latter half so chunks stay
        // reasonably large and deterministic.
        int floor = start + (hardEnd - start) / 2;
        int p = s.lastIndexOf("\n\n", hardEnd - 1);
        if (p >= floor) return p + 2;
        p = s.lastIndexOf('\n', hardEnd - 1);
        if (p >= floor) return p + 1;
        for (int i = hardEnd - 1; i >= floor; i--) {
            char c = s.charAt(i);
            if (c == '.' || c == '!' || c == '?' || c == '؟' || c == '؛') return i + 1;
        }
        for (int i = hardEnd - 1; i >= floor; i--) {
            if (Character.isWhitespace(s.charAt(i))) return i + 1;
        }
        return hardEnd;
    }

    private static void add(List<String> out, String s) {
        String x = s.trim();
        if (!x.isEmpty()) out.add(x);
    }
}
