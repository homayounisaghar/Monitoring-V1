package com.openai.controlplane.notificationprobe;

import android.app.Notification;
import android.app.NotificationChannel;
import android.content.pm.PackageInfo;
import android.content.pm.ShortcutInfo;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

public class NotificationProbeService extends NotificationListenerService {
    private static final String CHATGPT_PACKAGE = "com.openai.chatgpt";
    private static final String EXPECTED_VERSION = "1.2026.237";

    @Override
    public void onListenerConnected() {
        super.onListenerConnected();
        ProbeStore.markConnected(this);
        snapshotActiveChatGptNotifications();
    }

    @Override
    public void onListenerDisconnected() {
        ProbeStore.markDisconnected(this);
        super.onListenerDisconnected();
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (!isExactChatGptNotification(sbn)) return;
        record("POSTED", sbn);
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        if (!isExactChatGptNotification(sbn)) return;
        record("REMOVED", sbn);
    }

    private void snapshotActiveChatGptNotifications() {
        try {
            StatusBarNotification[] active = getActiveNotifications();
            if (active == null) {
                ProbeStore.append(this, "ACTIVE_SNAPSHOT count=0 (null)");
                return;
            }
            int count = 0;
            for (StatusBarNotification sbn : active) {
                if (isExactChatGptNotification(sbn)) {
                    count++;
                    record("ACTIVE_SNAPSHOT", sbn);
                }
            }
            ProbeStore.append(this, "ACTIVE_SNAPSHOT ChatGPT_count=" + count + " system_count=" + active.length);
        } catch (Throwable t) {
            ProbeStore.append(this, "ACTIVE_SNAPSHOT_ERROR " + t.getClass().getSimpleName());
        }
    }

    private boolean isExactChatGptNotification(StatusBarNotification sbn) {
        if (sbn == null || !CHATGPT_PACKAGE.equals(sbn.getPackageName())) return false;
        try {
            PackageInfo info = getPackageManager().getPackageInfo(CHATGPT_PACKAGE, 0);
            return EXPECTED_VERSION.equals(info.versionName);
        } catch (Throwable t) {
            return false;
        }
    }

    private void record(String kind, StatusBarNotification sbn) {
        try {
            Notification n = sbn.getNotification();
            StringBuilder out = new StringBuilder();
            out.append(kind)
                    .append(" id=").append(sbn.getId())
                    .append(" tag=").append(q(sbn.getTag()))
                    .append(" key=").append(q(sbn.getKey()))
                    .append(" groupKey=").append(q(sbn.getGroupKey()))
                    .append(" postTime=").append(sbn.getPostTime())
                    .append(" ongoing=").append(sbn.isOngoing());

            if (n != null) {
                out.append(" channelId=").append(q(n.getChannelId()))
                        .append(" shortcutId=").append(q(n.getShortcutId()))
                        .append(" category=").append(q(n.category))
                        .append(" group=").append(q(n.getGroup()));

                if (n.getLocusId() != null) {
                    out.append(" locusId=").append(q(n.getLocusId().getId()));
                }

                Bundle e = n.extras;
                if (e != null) {
                    out.append(" title=").append(q(text(e.getCharSequence(Notification.EXTRA_TITLE))))
                            .append(" text=").append(q(text(e.getCharSequence(Notification.EXTRA_TEXT))))
                            .append(" bigText=").append(q(text(e.getCharSequence(Notification.EXTRA_BIG_TEXT))));
                    String interesting = interestingExtras(e);
                    if (!interesting.isEmpty()) out.append(" interestingExtras={").append(interesting).append("}");
                }
            }

            appendRankingMetadata(out, sbn);
            appendDerivedHints(out, sbn, n);
            ProbeStore.append(this, out.toString());
        } catch (Throwable t) {
            ProbeStore.append(this, kind + " RECORD_ERROR " + t.getClass().getSimpleName());
        }
    }

    private void appendRankingMetadata(StringBuilder out, StatusBarNotification sbn) {
        try {
            RankingMap map = getCurrentRanking();
            Ranking ranking = new Ranking();
            if (map == null || !map.getRanking(sbn.getKey(), ranking)) {
                out.append(" ranking=missing");
                return;
            }
            out.append(" rankingImportance=").append(ranking.getImportance())
                    .append(" rankingIsConversation=").append(ranking.isConversation());

            NotificationChannel channel = ranking.getChannel();
            if (channel != null) {
                out.append(" rankingChannelId=").append(q(channel.getId()))
                        .append(" rankingChannelConversationId=").append(q(channel.getConversationId()))
                        .append(" rankingParentChannelId=").append(q(channel.getParentChannelId()));
            }

            ShortcutInfo shortcut = ranking.getConversationShortcutInfo();
            if (shortcut != null) {
                out.append(" rankingShortcutId=").append(q(shortcut.getId()))
                        .append(" rankingShortcutShortLabel=").append(q(text(shortcut.getShortLabel())))
                        .append(" rankingShortcutLongLabel=").append(q(text(shortcut.getLongLabel())));
            }
        } catch (Throwable t) {
            out.append(" rankingError=").append(t.getClass().getSimpleName());
        }
    }

    private static void appendDerivedHints(StringBuilder out, StatusBarNotification sbn, Notification n) {
        List<String> hints = new ArrayList<>();
        String tag = clean(sbn == null ? null : sbn.getTag());
        if (!tag.isEmpty()) {
            hints.add("tag=" + tag);
            int dot = tag.indexOf('.');
            if (dot > 0) hints.add("tagPrefixBeforeDot=" + tag.substring(0, dot));
        }
        if (n != null) {
            String shortcut = clean(n.getShortcutId());
            if (!shortcut.isEmpty()) hints.add("notificationShortcutId=" + shortcut);
            if (n.getLocusId() != null) {
                String locus = clean(n.getLocusId().getId());
                if (!locus.isEmpty()) hints.add("locusId=" + locus);
            }
        }
        if (!hints.isEmpty()) out.append(" idLikeHints=").append(hints);
    }

    private static String interestingExtras(Bundle e) {
        List<String> keys = new ArrayList<>(e.keySet());
        Collections.sort(keys);
        StringBuilder out = new StringBuilder();
        for (String key : keys) {
            if (key == null) continue;
            String lower = key.toLowerCase(Locale.US);
            if (!(lower.contains("conversation") || lower.contains("thread") || lower.contains("shortcut") ||
                    lower.contains("chat") || lower.endsWith("id") || lower.contains("message_id"))) {
                continue;
            }
            Object value;
            try {
                value = e.get(key);
            } catch (Throwable t) {
                value = "<" + t.getClass().getSimpleName() + ">";
            }
            if (out.length() > 0) out.append(", ");
            out.append(key).append('=').append(abbrev(String.valueOf(value), 180));
        }
        return out.toString();
    }

    private static String text(CharSequence s) {
        return s == null ? "" : s.toString().replace('\n', ' ').replace('\r', ' ');
    }

    private static String clean(String s) {
        return s == null ? "" : s.trim();
    }

    private static String q(String s) {
        return '"' + abbrev(clean(s), 240) + '"';
    }

    private static String abbrev(String s, int max) {
        if (s == null) return "";
        String one = s.replace('\n', ' ').replace('\r', ' ');
        return one.length() <= max ? one : one.substring(0, max) + "...";
    }
}
