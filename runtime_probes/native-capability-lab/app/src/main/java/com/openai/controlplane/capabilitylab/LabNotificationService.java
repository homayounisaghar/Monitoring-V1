package com.openai.controlplane.capabilitylab;

import android.app.Notification;
import android.app.NotificationChannel;
import android.content.pm.PackageInfo;
import android.content.pm.ShortcutInfo;
import android.os.Bundle;
import android.os.UserHandle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

public class LabNotificationService extends NotificationListenerService {
    private static volatile LabNotificationService INSTANCE;

    @Override
    public void onListenerConnected() {
        super.onListenerConnected();
        INSTANCE = this;
        LabStore.markNotificationConnected(this, true);
        LabStore.append(this, "NOTIFICATION_LISTENER_CONNECTED");
        snapshotNow("listener_connected");
    }

    @Override
    public void onListenerDisconnected() {
        LabStore.markNotificationConnected(this, false);
        LabStore.append(this, "NOTIFICATION_LISTENER_DISCONNECTED");
        INSTANCE = null;
        super.onListenerDisconnected();
    }

    @Override
    public void onDestroy() {
        if (INSTANCE == this) INSTANCE = null;
        super.onDestroy();
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (isExactChatGpt(sbn)) recordNotification("POSTED", sbn, null);
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn, RankingMap rankingMap) {
        if (isExactChatGpt(sbn)) recordNotification("POSTED", sbn, rankingMap);
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        if (isExactChatGpt(sbn)) recordNotification("REMOVED", sbn, null);
    }

    @Override
    public void onNotificationChannelModified(String pkg, UserHandle user, NotificationChannel channel, int modificationType) {
        if (!ProfileGuard.CHATGPT_PACKAGE.equals(pkg) || channel == null) return;
        String line = "CHANNEL_MODIFIED type=" + modificationType
                + " id=" + q(channel.getId())
                + " conversationId=" + q(channel.getConversationId())
                + " parentChannelId=" + q(channel.getParentChannelId())
                + " name=" + q(String.valueOf(channel.getName()));
        LabStore.append(this, line);
        LabStore.addCandidate(this, "channelModified.conversationId", channel.getConversationId());
    }

    static boolean isLive() { return INSTANCE != null; }

    static void snapshotFromRunner(String label) {
        LabNotificationService s = INSTANCE;
        if (s == null) return;
        s.snapshotNow(label);
    }

    static void tryChannelSnapshotFromRunner() {
        LabNotificationService s = INSTANCE;
        if (s == null) return;
        s.tryChannelSnapshot();
        LabShortcutReadSide.snapshot(s);

        // Stable v0.4 LAB-ONLY discovery fan-out. The plan DSL intentionally reuses the
        // already-allowlisted channel_snapshot op; production claims remain based only on
        // the public Android observations above. Raw shell output is never persisted.
        if (LabShizukuObserver.permissionGranted()) {
            try {
                LabShizukuObserver.capture(s, "channel_step_" + LabStore.step(s));
            } catch (Throwable t) {
                LabStore.append(s, "SHELL_OBSERVER_ERROR " + t.getClass().getSimpleName()
                        + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 260));
            }
        } else {
            LabStore.append(s, "SHELL_OBSERVER_SKIPPED shizuku=" + LabShizukuObserver.compactStatus());
        }
    }

    private void snapshotNow(String label) {
        try {
            StatusBarNotification[] active = getActiveNotifications();
            int chatCount = 0;
            int systemCount = active == null ? 0 : active.length;
            if (active != null) {
                for (StatusBarNotification sbn : active) {
                    if (isExactChatGpt(sbn)) {
                        chatCount++;
                        recordNotification("ACTIVE_SNAPSHOT", sbn, getCurrentRanking());
                    }
                }
            }
            LabStore.append(this, "NOTIFICATION_SNAPSHOT label=" + label + " ChatGPT_count=" + chatCount + " system_count=" + systemCount);
        } catch (Throwable t) {
            LabStore.append(this, "NOTIFICATION_SNAPSHOT_ERROR " + t.getClass().getSimpleName() + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 200));
        }

        try {
            StatusBarNotification[] snoozed = getSnoozedNotifications();
            int chat = 0;
            if (snoozed != null) {
                for (StatusBarNotification sbn : snoozed) {
                    if (isExactChatGpt(sbn)) {
                        chat++;
                        recordNotification("SNOOZED_SNAPSHOT", sbn, getCurrentRanking());
                    }
                }
            }
            LabStore.append(this, "SNOOZED_SNAPSHOT ChatGPT_count=" + chat);
        } catch (Throwable t) {
            LabStore.append(this, "SNOOZED_SNAPSHOT_ERROR " + t.getClass().getSimpleName());
        }
    }

    private void tryChannelSnapshot() {
        try {
            PackageInfo info = ProfileGuard.packageInfo(this);
            UserHandle user = UserHandle.getUserHandleForUid(info.applicationInfo.uid);
            List<NotificationChannel> channels = getNotificationChannels(ProfileGuard.CHATGPT_PACKAGE, user);
            int count = channels == null ? 0 : channels.size();
            LabStore.append(this, "CHANNEL_SNAPSHOT_ALLOWED count=" + count);
            if (channels != null) {
                for (NotificationChannel channel : channels) {
                    if (channel == null) continue;
                    LabStore.append(this, "CHANNEL id=" + q(channel.getId())
                            + " conversationId=" + q(channel.getConversationId())
                            + " parentChannelId=" + q(channel.getParentChannelId())
                            + " importance=" + channel.getImportance()
                            + " name=" + q(String.valueOf(channel.getName())));
                    LabStore.addCandidate(this, "channel.conversationId", channel.getConversationId());
                }
            }
        } catch (SecurityException se) {
            LabStore.append(this, "CHANNEL_SNAPSHOT_DENIED SecurityException=" + LabStore.abbrev(String.valueOf(se.getMessage()), 240));
        } catch (Throwable t) {
            LabStore.append(this, "CHANNEL_SNAPSHOT_ERROR " + t.getClass().getSimpleName() + ":" + LabStore.abbrev(String.valueOf(t.getMessage()), 240));
        }
    }

    private boolean isExactChatGpt(StatusBarNotification sbn) {
        if (sbn == null || !ProfileGuard.CHATGPT_PACKAGE.equals(sbn.getPackageName())) return false;
        try {
            return ProfileGuard.isExact(this);
        } catch (Throwable t) {
            return false;
        }
    }

    private void recordNotification(String kind, StatusBarNotification sbn, RankingMap suppliedMap) {
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

            addCandidateWithTagVariants("sbn.tag", sbn.getTag());

            if (n != null) {
                out.append(" channelId=").append(q(n.getChannelId()))
                        .append(" shortcutId=").append(q(n.getShortcutId()))
                        .append(" category=").append(q(n.category))
                        .append(" group=").append(q(n.getGroup()));
                LabStore.addCandidate(this, "notification.shortcutId", n.getShortcutId());

                if (n.getLocusId() != null) {
                    String locus = n.getLocusId().getId();
                    out.append(" locusId=").append(q(locus));
                    LabStore.addCandidate(this, "notification.locusId", locus);
                }

                Bundle e = n.extras;
                if (e != null) {
                    out.append(" title=").append(q(text(e.getCharSequence(Notification.EXTRA_TITLE))))
                            .append(" text=").append(q(text(e.getCharSequence(Notification.EXTRA_TEXT))))
                            .append(" bigText=").append(q(text(e.getCharSequence(Notification.EXTRA_BIG_TEXT))));
                    appendInterestingExtras(out, e);
                }
            }

            appendRanking(out, sbn, suppliedMap == null ? getCurrentRanking() : suppliedMap);
            LabStore.append(this, out.toString());
        } catch (Throwable t) {
            LabStore.append(this, kind + " RECORD_ERROR " + t.getClass().getSimpleName());
        }
    }

    private void appendRanking(StringBuilder out, StatusBarNotification sbn, RankingMap map) {
        try {
            Ranking r = new Ranking();
            if (map == null || !map.getRanking(sbn.getKey(), r)) {
                out.append(" ranking=missing");
                return;
            }
            out.append(" rankingImportance=").append(r.getImportance())
                    .append(" rankingIsConversation=").append(r.isConversation());
            NotificationChannel c = r.getChannel();
            if (c != null) {
                out.append(" rankingChannelId=").append(q(c.getId()))
                        .append(" rankingConversationId=").append(q(c.getConversationId()))
                        .append(" rankingParentChannelId=").append(q(c.getParentChannelId()));
                LabStore.addCandidate(this, "ranking.channel.conversationId", c.getConversationId());
            }
            ShortcutInfo shortcut = r.getConversationShortcutInfo();
            if (shortcut != null) {
                out.append(" rankingShortcutId=").append(q(shortcut.getId()))
                        .append(" rankingShortcutShortLabel=").append(q(text(shortcut.getShortLabel())))
                        .append(" rankingShortcutLongLabel=").append(q(text(shortcut.getLongLabel())));
                LabStore.addCandidate(this, "ranking.shortcutId", shortcut.getId());
            }
        } catch (Throwable t) {
            out.append(" rankingError=").append(t.getClass().getSimpleName());
        }
    }

    private void appendInterestingExtras(StringBuilder out, Bundle e) {
        List<String> keys = new ArrayList<>(e.keySet());
        Collections.sort(keys);
        StringBuilder interesting = new StringBuilder();
        for (String key : keys) {
            if (key == null) continue;
            String lower = key.toLowerCase(Locale.US);
            if (!(lower.contains("conversation") || lower.contains("thread") || lower.contains("shortcut")
                    || lower.contains("chat") || lower.endsWith("id") || lower.contains("message_id"))) continue;
            Object value;
            try { value = e.get(key); } catch (Throwable t) { value = "<" + t.getClass().getSimpleName() + ">"; }
            String s = value == null ? "" : String.valueOf(value);
            if (interesting.length() > 0) interesting.append(", ");
            interesting.append(key).append('=').append(LabStore.abbrev(s, 180));
            LabStore.addCandidate(this, "notification.extra." + key, s);
        }
        if (interesting.length() > 0) out.append(" interestingExtras={").append(interesting).append('}');
    }

    private void addCandidateWithTagVariants(String source, String tag) {
        if (tag == null) return;
        LabStore.addCandidate(this, source, tag);
        int dot = tag.indexOf('.');
        if (dot > 0) LabStore.addCandidate(this, source + ".prefixBeforeDot", tag.substring(0, dot));
    }

    private static String text(CharSequence s) {
        return s == null ? "" : s.toString().replace('\n', ' ').replace('\r', ' ');
    }

    private static String q(String s) {
        String x = s == null ? "" : s.trim();
        return '"' + LabStore.abbrev(x, 240) + '"';
    }
}
