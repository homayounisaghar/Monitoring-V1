package com.openai.controlplane.capabilitylab;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;

import java.security.MessageDigest;
import java.util.Locale;

final class ProfileGuard {
    static final String CHATGPT_PACKAGE = "com.openai.chatgpt";
    static final String EXPECTED_VERSION = "1.2026.237";
    static final String EXPECTED_SIGNER_SHA256 = "b24f4bfbb3cf293f938703b9d87027c1102cc36dc4fa206910e08927db40473c";
    static final String CHATGPT_MAIN = "com.openai.chatgpt.MainActivity";
    static final String CHATGPT_DEEPLINK = "com.openai.chatgpt.ChatGptDeeplinkActivity";
    static final String CHATGPT_ASSISTANT = "com.openai.voice.assistant.AssistantActivity";
    static final String CHATGPT_PROCESS_TEXT = "com.openai.chatgpt.TextProcessorActivity";

    private ProfileGuard() {}

    static PackageInfo packageInfo(Context c) throws Exception {
        PackageManager pm = c.getPackageManager();
        if (Build.VERSION.SDK_INT >= 33) {
            return pm.getPackageInfo(CHATGPT_PACKAGE,
                    PackageManager.PackageInfoFlags.of(PackageManager.GET_SIGNING_CERTIFICATES));
        }
        return pm.getPackageInfo(CHATGPT_PACKAGE, PackageManager.GET_SIGNING_CERTIFICATES);
    }

    static String version(Context c) {
        try {
            String v = packageInfo(c).versionName;
            return v == null ? "<null>" : v;
        } catch (Throwable t) {
            return "NOT_INSTALLED";
        }
    }

    static String signerSha256(Context c) {
        try {
            PackageInfo info = packageInfo(c);
            if (info.signingInfo == null) return "<no-signing-info>";
            Signature[] sigs = info.signingInfo.hasMultipleSigners()
                    ? info.signingInfo.getApkContentsSigners()
                    : info.signingInfo.getSigningCertificateHistory();
            if (sigs == null || sigs.length == 0) return "<no-signers>";
            return sha256(sigs[0].toByteArray());
        } catch (Throwable t) {
            return "<error:" + t.getClass().getSimpleName() + ">";
        }
    }

    static boolean isExact(Context c) {
        return EXPECTED_VERSION.equals(version(c))
                && EXPECTED_SIGNER_SHA256.equalsIgnoreCase(signerSha256(c));
    }

    static void assertExact(Context c) {
        String v = version(c);
        String s = signerSha256(c);
        if (!EXPECTED_VERSION.equals(v) || !EXPECTED_SIGNER_SHA256.equalsIgnoreCase(s)) {
            throw new IllegalStateException("Fail closed: expected ChatGPT " + EXPECTED_VERSION
                    + " signer " + EXPECTED_SIGNER_SHA256 + " but found version=" + v + " signer=" + s);
        }
    }

    static String shortSigner(Context c) {
        String s = signerSha256(c);
        return s.length() >= 16 ? s.substring(0, 16) : s;
    }

    static String sha256(byte[] bytes) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] digest = md.digest(bytes);
        StringBuilder b = new StringBuilder();
        for (byte x : digest) b.append(String.format(Locale.US, "%02x", x & 0xff));
        return b.toString();
    }
}
