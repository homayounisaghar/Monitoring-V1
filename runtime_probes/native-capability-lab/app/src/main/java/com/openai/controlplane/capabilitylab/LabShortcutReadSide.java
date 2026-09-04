package com.openai.controlplane.capabilitylab;

import android.content.Context;
import android.content.Intent;
import android.content.pm.LauncherApps;
import android.content.pm.ShortcutInfo;
import android.os.Bundle;
import android.os.Process;

import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

final class LabShortcutReadSide {
    private static final Pattern UUID_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])");
    private static final Pattern HEX32_FIND = Pattern.compile("(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])");

    private LabShortcutReadSide() {}

    static void snapshot(Context context) {
        try {
            LauncherApps apps = (LauncherApps) context.getSystemService(Context.LAUNCHER_APPS_SERVICE);
            if (apps == null) {
                LabStore.append(context, "SHORTCUT_SNAPSHOT unavailable=no_launcher_apps_service");
                return;
            }
            boolean host = apps.hasShortcutHostPermission();
            LabStore.append(context, "SHORTCUT_HOST_PERMISSION=" + host);
            if (!host) {
                LabStore.append(context, "SHORTCUT_SNAPSHOT unavailable=no_shortcut_host_permission");
                return;
            }

            LauncherApps.ShortcutQuery query = new LauncherApps.ShortcutQuery()
                    .setPackage(ProfileGuard.CHATGPT_PACKAGE)
                    .setQueryFlags(LauncherApps.ShortcutQuery.FLAG_MATCH_DYNAMIC
                            | LauncherApps.ShortcutQuery.FLAG_MATCH_PINNED
                            | LauncherApps.ShortcutQuery.FLAG_MATCH_MANIFEST
                            | LauncherApps.ShortcutQuery.FLAG_MATCH_CACHED);
            List<ShortcutInfo> shortcuts = apps.getShortcuts(query, Process.myUserHandle());
            int count = shortcuts == null ? 0 : shortcuts.size();
            int candidateMatches = 0;
            LabStore.append(context, "SHORTCUT_SNAPSHOT_ALLOWED count=" + count);
            if (shortcuts != null) {
                for (ShortcutInfo shortcut : shortcuts) {
                    if (shortcut == null) continue;
                    candidateMatches += addCandidates(context, "shortcut.id", shortcut.getId());
                    try {
                        Intent[] intents = shortcut.getIntents();
                        if (intents == null) continue;
                        for (Intent intent : intents) {
                            if (intent == null) continue;
                            candidateMatches += addCandidates(context, "shortcut.intent.data", intent.getDataString());
                            candidateMatches += addCandidates(context, "shortcut.intent.action", intent.getAction());
                            Bundle extras = intent.getExtras();
                            if (extras != null) {
                                for (String key : extras.keySet()) {
                                    if (key == null) continue;
                                    candidateMatches += addCandidates(context, "shortcut.extraKey", key);
                                    Object value;
                                    try { value = extras.get(key); }
                                    catch (Throwable t) { value = null; }
                                    if (value != null) {
                                        candidateMatches += addCandidates(context, "shortcut.extra." + key, String.valueOf(value));
                                    }
                                }
                            }
                        }
                    } catch (Throwable t) {
                        LabStore.append(context, "SHORTCUT_INTENT_READ_ERROR idHash=" + Integer.toHexString(shortcut.getId().hashCode()).toLowerCase(Locale.US)
                                + " type=" + t.getClass().getSimpleName());
                    }
                }
            }
            LabStore.append(context, "SHORTCUT_SNAPSHOT candidateMatches=" + candidateMatches);
        } catch (SecurityException se) {
            LabStore.append(context, "SHORTCUT_SNAPSHOT_DENIED SecurityException=" + LabStore.abbrev(String.valueOf(se.getMessage()), 240));
        } catch (Throwable t) {
            LabStore.append(context, "SHORTCUT_SNAPSHOT_ERROR " + t.getClass().getSimpleName() + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 240));
        }
    }

    private static int addCandidates(Context context, String source, String raw) {
        if (raw == null || raw.isEmpty()) return 0;
        int count = 0;
        Matcher uuid = UUID_FIND.matcher(raw);
        while (uuid.find() && count < 16) {
            LabStore.addCandidate(context, source, uuid.group());
            count++;
        }
        Matcher hex = HEX32_FIND.matcher(raw);
        while (hex.find() && count < 16) {
            LabStore.addCandidate(context, source, hex.group());
            count++;
        }
        return count;
    }
}
