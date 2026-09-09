package com.homayounisaghar.chatgptwebviewprobe;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * Exact material-text identity for Dashboard/workflow payloads.
 *
 * Canonicalization intentionally preserves spaces, tabs, blank lines and all
 * visible line structure. Only platform line-ending representation is folded
 * to LF so Android/JSON/HTML sources share one stable byte representation.
 *
 * Do not replace this with whitespace normalization for material payload
 * equality or effect receipts. Normalized hashes may be diagnostics only.
 */
final class ExactTextV1 {
    private ExactTextV1() {}

    static String canonical(String value) {
        if (value == null) return "";
        return value.replace("\r\n", "\n").replace('\r', '\n');
    }

    static byte[] utf8(String value) {
        return canonical(value).getBytes(StandardCharsets.UTF_8);
    }

    static String sha256(String value) {
        try {
            MessageDigest d = MessageDigest.getInstance("SHA-256");
            byte[] out = d.digest(utf8(value));
            StringBuilder b = new StringBuilder(out.length * 2);
            for (byte x : out) b.append(String.format("%02x", x & 0xff));
            return b.toString();
        } catch (Exception e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }

    static boolean same(String a, String b) {
        return canonical(a).equals(canonical(b));
    }
}
