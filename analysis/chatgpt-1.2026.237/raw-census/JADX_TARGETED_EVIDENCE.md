# JADX_TARGETED_EVIDENCE.md

## ATTACHMENT_SHARE

### `sources/android/net/http/UploadDataProvider.java:5`
```text
3: import java.io.Closeable;
4: 
5: public class UploadDataProvider implements Closeable {
6:     static {
7:         throw new NoClassDefFoundError();
```

### `sources/androidx/activity/result/contract/ActivityResultContracts$OpenDocument.java:13`
```text
11:     @Override
12:     public final Intent createIntent(Context context, Object obj) {
13:         return new Intent("android.intent.action.OPEN_DOCUMENT").putExtra("android.intent.extra.MIME_TYPES", (String[]) obj).setType("*/*");
14:     }
15: 
```

### `sources/androidx/core/content/FileProvider.java:14`
```text
12: import android.os.Environment;
13: import android.os.ParcelFileDescriptor;
14: import android.webkit.MimeTypeMap;
15: import defpackage.gmo;
16: import defpackage.hmo;
```

### `sources/androidx/core/content/FileProvider.java:204`
```text
202:             return "application/octet-stream";
203:         }
204:         String mimeTypeFromExtension = MimeTypeMap.getSingleton().getMimeTypeFromExtension(fileB.getName().substring(iLastIndexOf + 1));
205:         return mimeTypeFromExtension != null ? mimeTypeFromExtension : "application/octet-stream";
206:     }
```

### `sources/androidx/core/content/FileProvider.java:205`
```text
203:         }
204:         String mimeTypeFromExtension = MimeTypeMap.getSingleton().getMimeTypeFromExtension(fileB.getName().substring(iLastIndexOf + 1));
205:         return mimeTypeFromExtension != null ? mimeTypeFromExtension : "application/octet-stream";
206:     }
207: 
```

### `sources/com/google/android/gms/fido/fido2/api/common/Attachment$UnsupportedAttachmentException.java:3`
```text
1: package com.google.android.gms.fido.fido2.api.common;
2: 
3: public class Attachment$UnsupportedAttachmentException extends Exception {
4: }
```

### `sources/com/openai/chatgpt/R.java:2071`
```text
2069:         public static final int pi2_hint_background_color = 0x7f0604f5;
2070:         public static final int pi2_overlay_stroke_color = 0x7f0604f6;
2071:         public static final int pi2_review_upload_background = 0x7f0604f7;
2072:         public static final int places_autocomplete_list_background = 0x7f0604fe;
2073:         public static final int places_color_disabled_surface = 0x7f060506;
```

### `sources/com/openai/chatgpt/R.java:3895`
```text
3893:         public static final int undo = 0x7f08054e;
3894:         public static final int unpin = 0x7f08054f;
3895:         public static final int upload = 0x7f080550;
3896:         public static final int usage = 0x7f080552;
3897:         public static final int user = 0x7f080553;
```

### `sources/com/openai/chatgpt/R.java:5282`
```text
5280:         public static final int tag_on_apply_window_listener = 0x7f0b0523;
5281:         public static final int tag_on_receive_content_listener = 0x7f0b0524;
5282:         public static final int tag_on_receive_content_mime_types = 0x7f0b0525;
5283:         public static final int tag_screen_reader_focusable = 0x7f0b0526;
5284:         public static final int tag_state_description = 0x7f0b0527;
```

### `sources/com/openai/chatgpt/R.java:5380`
```text
5378:         public static final int unlabeled = 0x7f0b0585;
5379:         public static final int up = 0x7f0b0586;
5380:         public static final int upload_button = 0x7f0b0587;
5381:         public static final int useLogo = 0x7f0b0588;
5382:         public static final int use_photo_button = 0x7f0b0589;
```

### `sources/com/openai/chatgpt/R.java:6249`
```text
6247:         public static final int pi2_ui_input_checkbox = 0x7f0e0318;
6248:         public static final int pi2_ui_input_checkbox_group = 0x7f0e0319;
6249:         public static final int pi2_ui_input_file_upload = 0x7f0e031a;
6250:         public static final int pi2_ui_input_number = 0x7f0e031b;
6251:         public static final int pi2_ui_input_phone_number = 0x7f0e031c;
```

### `sources/com/openai/chatgpt/R.java:6900`
```text
6898:         public static final int calpico_new_room_banner_title = 0x7f120017;
6899:         public static final int calpico_profile_edit_fun_facts_count = 0x7f120018;
6900:         public static final int calpico_room_snippet_attachments = 0x7f120019;
6901:         public static final int calpico_room_snippet_conversations = 0x7f12001a;
6902:         public static final int calpico_room_snippet_images = 0x7f12001b;
```

### `sources/com/openai/chatgpt/R.java:6932`
```text
6930:         public static final int codex_tool_call_searched_web_queries = 0x7f120037;
6931:         public static final int connectors_email_verification_dialog_time_remaining_content_description = 0x7f120038;
6932:         public static final int conversation_file_upload_message_attachment_limit_description = 0x7f120039;
6933:         public static final int conversation_file_upload_message_attachment_limit_reached = 0x7f12003a;
6934:         public static final int conversation_join_shared_project_member_count = 0x7f12003b;
```

### `sources/com/openai/chatgpt/R.java:6933`
```text
6931:         public static final int connectors_email_verification_dialog_time_remaining_content_description = 0x7f120038;
6932:         public static final int conversation_file_upload_message_attachment_limit_description = 0x7f120039;
6933:         public static final int conversation_file_upload_message_attachment_limit_reached = 0x7f12003a;
6934:         public static final int conversation_join_shared_project_member_count = 0x7f12003b;
6935:         public static final int conversation_shared_project_pill_multiple = 0x7f12003c;
```

### `sources/com/openai/chatgpt/R.java:6937`
```text
6935:         public static final int conversation_shared_project_pill_multiple = 0x7f12003c;
6936:         public static final int conversation_work_onboarding_installed_plugins = 0x7f12003d;
6937:         public static final int conversations_image_share_intent_plural = 0x7f12003e;
6938:         public static final int exo_controls_fastforward_by_amount_description = 0x7f12003f;
6939:         public static final int exo_controls_rewind_by_amount_description = 0x7f120040;
```

### `sources/com/openai/chatgpt/R.java:7045`
```text
7043:         public static final int pi2_selfie_processing = 0x7f13004b;
7044:         public static final int pi2_selfie_right_pose = 0x7f13004c;
7045:         public static final int pi2_upload_gov_id_back_lottie = 0x7f13004d;
7046:         public static final int pi2_upload_gov_id_front_lottie = 0x7f13004e;
7047:         public static final int pi2_upload_gov_id_passport_lottie = 0x7f13004f;
```

### `sources/com/openai/chatgpt/R.java:7046`
```text
7044:         public static final int pi2_selfie_right_pose = 0x7f13004c;
7045:         public static final int pi2_upload_gov_id_back_lottie = 0x7f13004d;
7046:         public static final int pi2_upload_gov_id_front_lottie = 0x7f13004e;
7047:         public static final int pi2_upload_gov_id_passport_lottie = 0x7f13004f;
7048:         public static final int pi2_wallet_removal = 0x7f130050;
```

### `sources/com/openai/chatgpt/R.java:7047`
```text
7045:         public static final int pi2_upload_gov_id_back_lottie = 0x7f13004d;
7046:         public static final int pi2_upload_gov_id_front_lottie = 0x7f13004e;
7047:         public static final int pi2_upload_gov_id_passport_lottie = 0x7f13004f;
7048:         public static final int pi2_wallet_removal = 0x7f130050;
7049:         public static final int supported_phone_country_codes = 0x7f13005d;
```

### `sources/com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\f\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException", "Ljava/lang/Exception;", "Lkotlin/Exception;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException extends Exception {
7: }
```

### `sources/com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\f\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"com/openai/feature/conversations/impl/coordinator/PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException", "Ljava/lang/Exception;", "Lkotlin/Exception;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class PendingAttachmentPreparationHandler$PendingAttachmentRateLimitedException extends Exception {
7: }
```

### `sources/com/openai/feature/conversations/upload/FileUploadRateLimitException.java:1`
```text
1: package com.openai.feature.conversations.upload;
2: 
3: import defpackage.u6h;
```

### `sources/com/openai/feature/conversations/upload/FileUploadRateLimitException.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversations/upload/FileUploadRateLimitException;", "Ljava/lang/IllegalStateException;", "Lkotlin/IllegalStateException;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
7: public final class FileUploadRateLimitException extends IllegalStateException {
8:     public final u6h a;
```

### `sources/com/openai/feature/conversations/upload/FileUploadRateLimitException.java:7`
```text
5: 
6: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversations/upload/FileUploadRateLimitException;", "Ljava/lang/IllegalStateException;", "Lkotlin/IllegalStateException;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
7: public final class FileUploadRateLimitException extends IllegalStateException {
8:     public final u6h a;
9: 
```

### `sources/com/openai/feature/conversations/upload/FileUploadRateLimitException.java:10`
```text
8:     public final u6h a;
9: 
10:     public FileUploadRateLimitException(u6h u6hVar) {
11:         super("File upload rate limited");
12:         this.a = u6hVar;
```

### `sources/com/openai/feature/conversations/upload/FileUploadRateLimitException.java:11`
```text
9: 
10:     public FileUploadRateLimitException(u6h u6hVar) {
11:         super("File upload rate limited");
12:         this.a = u6hVar;
13:     }
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'basicModels':s,'coreModel':s,'moreMessages':s,'moreUploads':s,'goImageCreation':s,'longerMemory':s,'noAds':s,'smarterModels':s,'moreMessagesAndUploads':s,'plusImageCreation':s,'moreMemory':s,'agentsAndDeepResearch':s,'earlyAccess':s,'proFrontierModel':s,'proCodex':s,'proDeepResearch':s,'proUnlimitedModel':s,'proMaximumMemory':s,'advancedChatIntelligence':s,'expandedCodexTokenUsage':s,'advancedCodingModels':s,'expandedDataAnalysisTools':s,'moreParallelT
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\bB\b\u0007\u0018\u00002\u00020\u0001B\u0081\u0002\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002\u0012\u0006\u0010\b\u001a\u00020\u0002\u0012\u0006\u0010\t\u001a\u00020\u0002\u0012\u0006\u0010\n\u001a\u00020\u0002\u0012\u0006\
9: public final class SubscriptionPricingNativeFeatureCopy extends b {
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'basicModels':s,'coreModel':s,'moreMessages':s,'moreUploads':s,'goImageCreation':s,'longerMemory':s,'noAds':s,'smarterModels':s,'moreMessagesAndUploads':s,'plusImageCreation':s,'moreMemory':s,'agentsAndDeepResearch':s,'earlyAccess':s,'proFrontierModel':s,'proCodex':s,'proDeepResearch':s,'proUnlimitedModel':s,'proMaximumMemory':s,'advancedChatIntelligence':s,'expandedCodexTokenUsage':s,'advancedCodingModels':s,'expandedDataAnalysisTools':s,'moreParallelT
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\bB\b\u0007\u0018\u00002\u00020\u0001B\u0081\u0002\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002\u0012\u0006\u0010\b\u001a\u00020\u0002\u0012\u0006\u0010\t\u001a\u00020\u0002\u0012\u0006\u0010\n\u001a\u00020\u0002\u0012\u0006\
9: public final class SubscriptionPricingNativeFeatureCopy extends b {
10:     private String _advancedChatIntelligence;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:26`
```text
24:     private String _moreMemory;
25:     private String _moreMessages;
26:     private String _moreMessagesAndUploads;
27:     private String _moreParallelTasks;
28:     private String _moreUploads;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:28`
```text
26:     private String _moreMessagesAndUploads;
27:     private String _moreParallelTasks;
28:     private String _moreUploads;
29:     private String _multiImageOutput;
30:     private String _noAds;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:46`
```text
44:         this._coreModel = str2;
45:         this._moreMessages = str3;
46:         this._moreUploads = str4;
47:         this._goImageCreation = str5;
48:         this._longerMemory = str6;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:51`
```text
49:         this._noAds = str7;
50:         this._smarterModels = str8;
51:         this._moreMessagesAndUploads = str9;
52:         this._plusImageCreation = str10;
53:         this._moreMemory = str11;
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:8`
```text
6: import kotlin.jvm.functions.Function0;
7: 
8: @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0000\n\u0002\b\u0007\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\b\b\u0001\u0018\u00002\u00020\u0001B\u000f\u0012\u0006\u0010\u0003\u001a\u00020\u0002¢\u0006\u0004\b\u0004\u0010\u0005R$\u0010\r\u001a\u0004\u0018\u00010\u00068\u0006@\u0006X\u0086\u000e¢\u0006\u0012\n\u0004\b\u0007\u0010\b\u001a\u0004\b\t\u0010\n\"\u0004\b\u000b\u0010\fR*\u0010\u0016\u001a\n\u0012\u0004\u0012\u
9: public final class ComposeValdiRootView extends ValdiRootView {
10:     public static final int $stable = 8;
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:12`
```text
10:     public static final int $stable = 8;
11: 
12:     public Object attachmentToken;
13: 
14:     public Function0 onRemeasureRequested;
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:20`
```text
18:     }
19: 
20:     public final Object getAttachmentToken() {
21:         return this.attachmentToken;
22:     }
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:21`
```text
19: 
20:     public final Object getAttachmentToken() {
21:         return this.attachmentToken;
22:     }
23: 
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:28`
```text
26:     }
27: 
28:     public final void setAttachmentToken(Object obj) {
29:         this.attachmentToken = obj;
30:     }
```

### `sources/com/openai/valdi/compose/ComposeValdiRootView.java:29`
```text
27: 
28:     public final void setAttachmentToken(Object obj) {
29:         this.attachmentToken = obj;
30:     }
31: 
```

### `sources/com/openai/valdi/filepicker/FilePickerCapabilities.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import com.snap.valdi.utils.b;
```

### `sources/com/openai/valdi/filepicker/FilePickerCapabilities.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'camera':b,'files':b,'photos':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\n\b\u0007\u0018\u00002\u00020\u0001B!\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002¢\u0006\u0004\b\u0006\u0010\u0007R\u0016\u0010\b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\tR\u00
9: public final class FilePickerCapabilities extends b {
10:     private boolean _camera;
```

### `sources/com/openai/valdi/filepicker/FilePickerCapabilities.java:9`
```text
7: @o2d0(propertyReplacements = "", schema = "'camera':b,'files':b,'photos':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\n\b\u0007\u0018\u00002\u00020\u0001B!\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002¢\u0006\u0004\b\u0006\u0010\u0007R\u0016\u0010\b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\tR\u00
9: public final class FilePickerCapabilities extends b {
10:     private boolean _camera;
11:     private boolean _files;
```

### `sources/com/openai/valdi/filepicker/FilePickerCapabilities.java:14`
```text
12:     private boolean _photos;
13: 
14:     public FilePickerCapabilities(boolean z, boolean z2, boolean z3) {
15:         this._camera = z;
16:         this._files = z2;
```

### `sources/com/openai/valdi/filepicker/FilePickerCompletion.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import com.snap.valdi.utils.ValdiMarshallable;
```

### `sources/com/openai/valdi/filepicker/FilePickerCompletion.java:11`
```text
9: import kotlin.Metadata;
10: 
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u001d\u0010\n\u001a\u00020\u00042\f\u0010\t\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u
12: @t5d0(propertyReplacements = "", proxyClass = yko.class, schema = "'onFailure':f|m|(r:'[0]'),'onFiles':f|m|(a<r:'[1]'>)", typeReferences = {FilePickerFailure.class, wk10.class})
13: public interface FilePickerCompletion extends ValdiMarshallable {
```

### `sources/com/openai/valdi/filepicker/FilePickerCompletion.java:12`
```text
10: 
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u001d\u0010\n\u001a\u00020\u00042\f\u0010\t\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u
12: @t5d0(propertyReplacements = "", proxyClass = yko.class, schema = "'onFailure':f|m|(r:'[0]'),'onFiles':f|m|(a<r:'[1]'>)", typeReferences = {FilePickerFailure.class, wk10.class})
13: public interface FilePickerCompletion extends ValdiMarshallable {
14:     void onFailure(FilePickerFailure failure);
```

### `sources/com/openai/valdi/filepicker/FilePickerCompletion.java:13`
```text
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u001d\u0010\n\u001a\u00020\u00042\f\u0010\t\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u
12: @t5d0(propertyReplacements = "", proxyClass = yko.class, schema = "'onFailure':f|m|(r:'[0]'),'onFiles':f|m|(a<r:'[1]'>)", typeReferences = {FilePickerFailure.class, wk10.class})
13: public interface FilePickerCompletion extends ValdiMarshallable {
14:     void onFailure(FilePickerFailure failure);
15: 
```

### `sources/com/openai/valdi/filepicker/FilePickerCompletion.java:14`
```text
12: @t5d0(propertyReplacements = "", proxyClass = yko.class, schema = "'onFailure':f|m|(r:'[0]'),'onFiles':f|m|(a<r:'[1]'>)", typeReferences = {FilePickerFailure.class, wk10.class})
13: public interface FilePickerCompletion extends ValdiMarshallable {
14:     void onFailure(FilePickerFailure failure);
15: 
16:     void onFiles(List<wk10> files);
```

### `sources/com/openai/valdi/filepicker/FilePickerFailure.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import com.snap.valdi.utils.b;
```

### `sources/com/openai/valdi/filepicker/FilePickerFailure.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'message':s", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001B\u0011\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002¢\u0006\u0004\b\u0004\u0010\u0005R\u0016\u0010\u0006\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0006\u0010\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerFailure;", "Lcom/snap/valdi/utils/b;", "", "message", "<init>", "(Ljava/lang/String;)V", "_message", "Lja
9: public final class FilePickerFailure extends b {
10:     private String _message;
```

### `sources/com/openai/valdi/filepicker/FilePickerFailure.java:9`
```text
7: @o2d0(propertyReplacements = "", schema = "'message':s", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001B\u0011\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002¢\u0006\u0004\b\u0004\u0010\u0005R\u0016\u0010\u0006\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0006\u0010\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerFailure;", "Lcom/snap/valdi/utils/b;", "", "message", "<init>", "(Ljava/lang/String;)V", "_message", "Lja
9: public final class FilePickerFailure extends b {
10:     private String _message;
11: 
```

### `sources/com/openai/valdi/filepicker/FilePickerFailure.java:12`
```text
10:     private String _message;
11: 
12:     public FilePickerFailure(String str) {
13:         this._message = str;
14:     }
```

### `sources/com/openai/valdi/filepicker/FilePickerNativeModuleFactoryImpl.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import defpackage.i5y;
```

### `sources/com/openai/valdi/filepicker/FilePickerNativeModuleFactoryImpl.java:8`
```text
6: import kotlin.Metadata;
7: 
8: @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\u0007¢\u0006\u0004\b\u0002\u0010\u0003J\u000f\u0010\u0005\u001a\u00020\u0004H\u0016¢\u0006\u0004\b\u0005\u0010\u0006¨\u0006\u0007"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerNativeModuleFactoryImpl;", "Lj5y;", "<init>", "()V", "Li5y;", "onLoadModule", "()Li5y;", "modules_oai_file_picker-oai_file_picker_android_impl_kt"}, k = 1, mv = {1,
9: public final class FilePickerNativeModuleFactoryImpl extends j5y {
10:     @Override
```

### `sources/com/openai/valdi/filepicker/FilePickerNativeModuleFactoryImpl.java:9`
```text
7: 
8: @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\u0007¢\u0006\u0004\b\u0002\u0010\u0003J\u000f\u0010\u0005\u001a\u00020\u0004H\u0016¢\u0006\u0004\b\u0005\u0010\u0006¨\u0006\u0007"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerNativeModuleFactoryImpl;", "Lj5y;", "<init>", "()V", "Li5y;", "onLoadModule", "()Li5y;", "modules_oai_file_picker-oai_file_picker_android_impl_kt"}, k = 1, mv = {1,
9: public final class FilePickerNativeModuleFactoryImpl extends j5y {
10:     @Override
11:     public i5y onLoadModule() {
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import com.snap.valdi.utils.b;
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:8`
```text
6: import kotlin.Metadata;
7: 
8: @o2d0(propertyReplacements = "", schema = "'acceptedTypes':a<s>,'maximumFileBytes':d,'maximumFiles':d,'maximumTotalBytes':d,'source':r<e>:'[0]'", typeReferences = {FilePickerSource.class})
9: @Metadata(d1 = {"\u0000\"\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0005\u0012\u0006\u0010\b\u001a\u00020\u0005\u0012\u0006\u0010\n\u001a\u00020\t¢\u0006\u0004\b\u000b\u0010\fR\u001c\u0010\r\u001a\b\u
10: public final class FilePickerOptions extends b {
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:9`
```text
7: 
8: @o2d0(propertyReplacements = "", schema = "'acceptedTypes':a<s>,'maximumFileBytes':d,'maximumFiles':d,'maximumTotalBytes':d,'source':r<e>:'[0]'", typeReferences = {FilePickerSource.class})
9: @Metadata(d1 = {"\u0000\"\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0005\u0012\u0006\u0010\b\u001a\u00020\u0005\u0012\u0006\u0010\n\u001a\u00020\t¢\u0006\u0004\b\u000b\u0010\fR\u001c\u0010\r\u001a\b\u
10: public final class FilePickerOptions extends b {
11:     private List<String> _acceptedTypes;
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:10`
```text
8: @o2d0(propertyReplacements = "", schema = "'acceptedTypes':a<s>,'maximumFileBytes':d,'maximumFiles':d,'maximumTotalBytes':d,'source':r<e>:'[0]'", typeReferences = {FilePickerSource.class})
9: @Metadata(d1 = {"\u0000\"\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0005\u0012\u0006\u0010\b\u001a\u00020\u0005\u0012\u0006\u0010\n\u001a\u00020\t¢\u0006\u0004\b\u000b\u0010\fR\u001c\u0010\r\u001a\b\u
10: public final class FilePickerOptions extends b {
11:     private List<String> _acceptedTypes;
12:     private double _maximumFileBytes;
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:15`
```text
13:     private double _maximumFiles;
14:     private double _maximumTotalBytes;
15:     private FilePickerSource _source;
16: 
17:     public FilePickerOptions(List<String> list, double d, double d2, double d3, FilePickerSource filePickerSource) {
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:17`
```text
15:     private FilePickerSource _source;
16: 
17:     public FilePickerOptions(List<String> list, double d, double d2, double d3, FilePickerSource filePickerSource) {
18:         this._acceptedTypes = list;
19:         this._maximumFileBytes = d;
```

### `sources/com/openai/valdi/filepicker/FilePickerOptions.java:22`
```text
20:         this._maximumFiles = d2;
21:         this._maximumTotalBytes = d3;
22:         this._source = filePickerSource;
23:     }
24: }
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import com.snap.valdi.utils.ValdiMarshallable;
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:9`
```text
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u00002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u001f\u0010\n\u001a\u00020\t2\u0006\u0010\u0006\u001a\u00020\u00052\u0006\u0010\b\u001a\u00020\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u0017\u0010
10: @t5d0(propertyReplacements = "", proxyClass = alo.class, schema = "'getCapabilities':f|m|(): r:'[0]','pickFiles':f|m|(r:'[1]', r:'[2]')", typeReferences = {FilePickerCapabilities.class, FilePickerOptions.class, FilePickerCompletion.class})
11: public interface FilePickerService extends ValdiMarshallable {
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:10`
```text
8: 
9: @Metadata(d1 = {"\u00002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u001f\u0010\n\u001a\u00020\t2\u0006\u0010\u0006\u001a\u00020\u00052\u0006\u0010\b\u001a\u00020\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u0017\u0010
10: @t5d0(propertyReplacements = "", proxyClass = alo.class, schema = "'getCapabilities':f|m|(): r:'[0]','pickFiles':f|m|(r:'[1]', r:'[2]')", typeReferences = {FilePickerCapabilities.class, FilePickerOptions.class, FilePickerCompletion.class})
11: public interface FilePickerService extends ValdiMarshallable {
12:     FilePickerCapabilities getCapabilities();
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:11`
```text
9: @Metadata(d1 = {"\u00002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u001f\u0010\n\u001a\u00020\t2\u0006\u0010\u0006\u001a\u00020\u00052\u0006\u0010\b\u001a\u00020\u0007H&¢\u0006\u0004\b\n\u0010\u000bJ\u0017\u0010
10: @t5d0(propertyReplacements = "", proxyClass = alo.class, schema = "'getCapabilities':f|m|(): r:'[0]','pickFiles':f|m|(r:'[1]', r:'[2]')", typeReferences = {FilePickerCapabilities.class, FilePickerOptions.class, FilePickerCompletion.class})
11: public interface FilePickerService extends ValdiMarshallable {
12:     FilePickerCapabilities getCapabilities();
13: 
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:12`
```text
10: @t5d0(propertyReplacements = "", proxyClass = alo.class, schema = "'getCapabilities':f|m|(): r:'[0]','pickFiles':f|m|(r:'[1]', r:'[2]')", typeReferences = {FilePickerCapabilities.class, FilePickerOptions.class, FilePickerCompletion.class})
11: public interface FilePickerService extends ValdiMarshallable {
12:     FilePickerCapabilities getCapabilities();
13: 
14:     void pickFiles(FilePickerOptions options, FilePickerCompletion completion);
```

### `sources/com/openai/valdi/filepicker/FilePickerService.java:14`
```text
12:     FilePickerCapabilities getCapabilities();
13: 
14:     void pickFiles(FilePickerOptions options, FilePickerCompletion completion);
15: 
16:     @Override
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:1`
```text
1: package com.openai.valdi.filepicker;
2: 
3: import defpackage.q4d0;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Files':0,'Photos':1,'Camera':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerSource;", "", "Files", "Photos", "Camera", "modules_oai_file_picker-oai_file_picker_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FilePickerSource {
10:     public static final FilePickerSource Camera;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:9`
```text
7: @q4d0(propertyReplacements = "", schema = "'Files':0,'Photos':1,'Camera':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerSource;", "", "Files", "Photos", "Camera", "modules_oai_file_picker-oai_file_picker_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FilePickerSource {
10:     public static final FilePickerSource Camera;
11:     public static final FilePickerSource Files;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/filepicker/FilePickerSource;", "", "Files", "Photos", "Camera", "modules_oai_file_picker-oai_file_picker_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FilePickerSource {
10:     public static final FilePickerSource Camera;
11:     public static final FilePickerSource Files;
12:     public static final FilePickerSource Photos;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:11`
```text
9: public final class FilePickerSource {
10:     public static final FilePickerSource Camera;
11:     public static final FilePickerSource Files;
12:     public static final FilePickerSource Photos;
13:     public static final FilePickerSource[] a;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:12`
```text
10:     public static final FilePickerSource Camera;
11:     public static final FilePickerSource Files;
12:     public static final FilePickerSource Photos;
13:     public static final FilePickerSource[] a;
14: 
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:13`
```text
11:     public static final FilePickerSource Files;
12:     public static final FilePickerSource Photos;
13:     public static final FilePickerSource[] a;
14: 
15:     static {
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:16`
```text
14: 
15:     static {
16:         FilePickerSource filePickerSource = new FilePickerSource("Files", 0);
17:         Files = filePickerSource;
18:         FilePickerSource filePickerSource2 = new FilePickerSource("Photos", 1);
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:17`
```text
15:     static {
16:         FilePickerSource filePickerSource = new FilePickerSource("Files", 0);
17:         Files = filePickerSource;
18:         FilePickerSource filePickerSource2 = new FilePickerSource("Photos", 1);
19:         Photos = filePickerSource2;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:18`
```text
16:         FilePickerSource filePickerSource = new FilePickerSource("Files", 0);
17:         Files = filePickerSource;
18:         FilePickerSource filePickerSource2 = new FilePickerSource("Photos", 1);
19:         Photos = filePickerSource2;
20:         FilePickerSource filePickerSource3 = new FilePickerSource("Camera", 2);
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:19`
```text
17:         Files = filePickerSource;
18:         FilePickerSource filePickerSource2 = new FilePickerSource("Photos", 1);
19:         Photos = filePickerSource2;
20:         FilePickerSource filePickerSource3 = new FilePickerSource("Camera", 2);
21:         Camera = filePickerSource3;
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:20`
```text
18:         FilePickerSource filePickerSource2 = new FilePickerSource("Photos", 1);
19:         Photos = filePickerSource2;
20:         FilePickerSource filePickerSource3 = new FilePickerSource("Camera", 2);
21:         Camera = filePickerSource3;
22:         a = new FilePickerSource[]{filePickerSource, filePickerSource2, filePickerSource3};
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:21`
```text
19:         Photos = filePickerSource2;
20:         FilePickerSource filePickerSource3 = new FilePickerSource("Camera", 2);
21:         Camera = filePickerSource3;
22:         a = new FilePickerSource[]{filePickerSource, filePickerSource2, filePickerSource3};
23:     }
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:22`
```text
20:         FilePickerSource filePickerSource3 = new FilePickerSource("Camera", 2);
21:         Camera = filePickerSource3;
22:         a = new FilePickerSource[]{filePickerSource, filePickerSource2, filePickerSource3};
23:     }
24: 
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:25`
```text
23:     }
24: 
25:     public static FilePickerSource valueOf(String str) {
26:         return (FilePickerSource) Enum.valueOf(FilePickerSource.class, str);
27:     }
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:26`
```text
24: 
25:     public static FilePickerSource valueOf(String str) {
26:         return (FilePickerSource) Enum.valueOf(FilePickerSource.class, str);
27:     }
28: 
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:29`
```text
27:     }
28: 
29:     public static FilePickerSource[] values() {
30:         return (FilePickerSource[]) a.clone();
31:     }
```

### `sources/com/openai/valdi/filepicker/FilePickerSource.java:30`
```text
28: 
29:     public static FilePickerSource[] values() {
30:         return (FilePickerSource[]) a.clone();
31:     }
32: }
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'filename':s,'mimeType':s,'bytes':t", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0012\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B!\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\
9: public final class MobileFileSaveRequest extends b {
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'filename':s,'mimeType':s,'bytes':t", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0012\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B!\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\
9: public final class MobileFileSaveRequest extends b {
10:     private byte[] _bytes;
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:12`
```text
10:     private byte[] _bytes;
11:     private String _filename;
12:     private String _mimeType;
13: 
14:     public MobileFileSaveRequest(String str, String str2, byte[] bArr) {
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:16`
```text
14:     public MobileFileSaveRequest(String str, String str2, byte[] bArr) {
15:         this._filename = str;
16:         this._mimeType = str2;
17:         this._bytes = bArr;
18:     }
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:28`
```text
26:     }
27: 
28:     public final String get_mimeType() {
29:         return this._mimeType;
30:     }
```

### `sources/com/openai/valdi/filesaver/MobileFileSaveRequest.java:29`
```text
27: 
28:     public final String get_mimeType() {
29:         return this._mimeType;
30:     }
31: }
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:3`
```text
1: package com.openai.valdi.filesaver;
2: 
3: import android.content.ClipData;
4: import android.content.ContentResolver;
5: import android.content.ContentValues;
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:48`
```text
46:                 ContentValues contentValues = new ContentValues();
47:                 contentValues.put("_display_name", request.get_filename());
48:                 contentValues.put("mime_type", request.get_mimeType());
49:                 contentValues.put("relative_path", Environment.DIRECTORY_DOWNLOADS);
50:                 Uri uriInsert = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues);
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:75`
```text
73:                 }
74:                 Intent intent = new Intent("android.intent.action.SEND");
75:                 intent.setType(request.get_mimeType());
76:                 intent.setClipData(ClipData.newUri(contentResolver, request.get_filename(), uriInsert));
77:                 intent.putExtra("android.intent.extra.STREAM", uriInsert);
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:76`
```text
74:                 Intent intent = new Intent("android.intent.action.SEND");
75:                 intent.setType(request.get_mimeType());
76:                 intent.setClipData(ClipData.newUri(contentResolver, request.get_filename(), uriInsert));
77:                 intent.putExtra("android.intent.extra.STREAM", uriInsert);
78:                 intent.putExtra("android.intent.extra.TITLE", request.get_filename());
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:77`
```text
75:                 intent.setType(request.get_mimeType());
76:                 intent.setClipData(ClipData.newUri(contentResolver, request.get_filename(), uriInsert));
77:                 intent.putExtra("android.intent.extra.STREAM", uriInsert);
78:                 intent.putExtra("android.intent.extra.TITLE", request.get_filename());
79:                 intent.putExtra("android.intent.extra.SUBJECT", request.get_filename());
```

### `sources/com/openai/valdi/filesaver/MobileFileSaverNativeModuleFactoryImpl.java:96`
```text
94:                     fileOutputStreamK.write(request.get_bytes());
95:                     fileOutputStreamK.close();
96:                     MediaScannerConnection.scanFile(context, new String[]{fileUniqueDestinationFile.getAbsolutePath()}, new String[]{request.get_mimeType()}, null);
97:                 } catch (Throwable th3) {
98:                     try {
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:3`
```text
1: package com.openai.valdi.oai.platform;
2: 
3: import com.openai.valdi.filepicker.FilePickerService;
4: import com.openai.valdi.integrity.DeviceIntegrityService;
5: import com.openai.valdi.location.LocationService;
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:11`
```text
9: import kotlin.Metadata;
10: 
11: @o2d0(propertyReplacements = "", schema = "'experimentService':r?:'[0]','apiService':r?:'[1]','loggingService':r?:'[2]','accountScope':r?:'[3]','analyticsService':r?:'[4]','authenticationService':r?:'[5]','accountFeatureService':r?:'[6]','accountSettingsService':r?:'[7]','accountCustomizationsService':r?:'[8]','petCatalogDataSource':r?:'[9]','voiceService':r?:'[10]','filePickerService':r?:'[11]','locationService':r?:'[12]','deviceIntegrityService':r?:'[13]'", typeReferences = {OAIExperimentServi
12: @Metadata(d1 = {"\u0000^\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b \b\u0007\u0018\u00002\u00020\u0001B±\u000
13: public final class OAIPlatformServices extends b {
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:12`
```text
10: 
11: @o2d0(propertyReplacements = "", schema = "'experimentService':r?:'[0]','apiService':r?:'[1]','loggingService':r?:'[2]','accountScope':r?:'[3]','analyticsService':r?:'[4]','authenticationService':r?:'[5]','accountFeatureService':r?:'[6]','accountSettingsService':r?:'[7]','accountCustomizationsService':r?:'[8]','petCatalogDataSource':r?:'[9]','voiceService':r?:'[10]','filePickerService':r?:'[11]','locationService':r?:'[12]','deviceIntegrityService':r?:'[13]'", typeReferences = {OAIExperimentServi
12: @Metadata(d1 = {"\u0000^\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b \b\u0007\u0018\u00002\u00020\u0001B±\u000
13: public final class OAIPlatformServices extends b {
14:     private OAIAccountCustomizationsService _accountCustomizationsService;
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:23`
```text
21:     private DeviceIntegrityService _deviceIntegrityService;
22:     private OAIExperimentService _experimentService;
23:     private FilePickerService _filePickerService;
24:     private LocationService _locationService;
25:     private OAILoggingService _loggingService;
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:29`
```text
27:     private VoiceService _voiceService;
28: 
29:     public OAIPlatformServices(OAIExperimentService oAIExperimentService, OAIAPIService oAIAPIService, OAILoggingService oAILoggingService, OAIAccountScope oAIAccountScope, OAIAnalyticsService oAIAnalyticsService, OAIAuthenticationService oAIAuthenticationService, OAIAccountFeatureService oAIAccountFeatureService, OAIAccountSettingsService oAIAccountSettingsService, OAIAccountCustomizationsService oAIAccountCustomizationsService, OAIPetCatalogDataSource oAIPetCatalogDataSource, VoiceService voic
30:         this._experimentService = oAIExperimentService;
31:         this._apiService = oAIAPIService;
```

### `sources/com/openai/valdi/oai/platform/OAIPlatformServices.java:41`
```text
39:         this._petCatalogDataSource = oAIPetCatalogDataSource;
40:         this._voiceService = voiceService;
41:         this._filePickerService = filePickerService;
42:         this._locationService = locationService;
43:         this._deviceIntegrityService = deviceIntegrityService;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:55`
```text
53: import kotlin.Metadata;
54: 
55: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/voice/recording/VoiceAudioRecordingUploadWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerParameters;", "p
56: public final class VoiceAudioRecordingUploadWorker extends CoroutineWorker {
57:     public static final long f;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:56`
```text
54: 
55: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/voice/recording/VoiceAudioRecordingUploadWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerParameters;", "p
56: public final class VoiceAudioRecordingUploadWorker extends CoroutineWorker {
57:     public static final long f;
58:     public static final int g = 0;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:70`
```text
68:     }
69: 
70:     public VoiceAudioRecordingUploadWorker(Context context, WorkerParameters workerParameters) {
71:         super(context, workerParameters);
72:         this.e = h940.m("VoiceAudioRecordingUploadWorker");
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:72`
```text
70:     public VoiceAudioRecordingUploadWorker(Context context, WorkerParameters workerParameters) {
71:         super(context, workerParameters);
72:         this.e = h940.m("VoiceAudioRecordingUploadWorker");
73:     }
74: 
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:77`
```text
75:     public static ikj b(dzd0 dzd0Var) {
76:         if (wnm.k(dzd0Var, bzd0.a)) {
77:             g100[] g100VarArr = {new g100("upload_outcome", "skipped"), new g100("upload_skipped", Boolean.TRUE)};
78:             gcg0 gcg0Var = new gcg0((byte) 15);
79:             for (int i = 0; i < 2; i++) {
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:86`
```text
84:         }
85:         if (wnm.k(dzd0Var, czd0.a)) {
86:             g100[] g100VarArr2 = {new g100("upload_outcome", "complete")};
87:             gcg0 gcg0Var2 = new gcg0((byte) 15);
88:             g100 g100Var2 = g100VarArr2[0];
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:96`
```text
94:             return null;
95:         }
96:         g100[] g100VarArr3 = {new g100("upload_outcome", "failed")};
97:         gcg0 gcg0Var3 = new gcg0((byte) 15);
98:         g100 g100Var3 = g100VarArr3[0];
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:217`
```text
215:             this.d = (w9e0) qg3VarB.m2.invoke();
216:             if (!strA4.equals(qg3VarB.b.e)) {
217:                 gev.f(uee0Var, "Voice audio recording upload account does not match the current account", null, null, 14);
218:                 return new yyu();
219:             }
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:16`
```text
14: import kotlin.Metadata;
15: 
16: @Metadata(d1 = {"\u0000T\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0010\u000e\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010\u0007\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\b\b\u0007\u0018\u0000 +:\u0001,B\u000f\u0012\u0006\u0010\u0002\u001a\u00020\u0001¢\u0006\u0004\b\u0003\u0
17: public final class AttributedTextCpp {
18:     public static final tj4 Companion = new tj4();
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:53`
```text
51:     public static final native String nativeGetFont(long j, int i);
52: 
53:     public static final native byte[] nativeGetImageAttachmentData(long j, int i);
54: 
55:     public static final native float nativeGetImageAttachmentHeight(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:55`
```text
53:     public static final native byte[] nativeGetImageAttachmentData(long j, int i);
54: 
55:     public static final native float nativeGetImageAttachmentHeight(long j, int i);
56: 
57:     public static final native float nativeGetImageAttachmentWidth(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:57`
```text
55:     public static final native float nativeGetImageAttachmentHeight(long j, int i);
56: 
57:     public static final native float nativeGetImageAttachmentWidth(long j, int i);
58: 
59:     public static final native int nativeGetInlineViewAttachmentChildIndex(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:59`
```text
57:     public static final native float nativeGetImageAttachmentWidth(long j, int i);
58: 
59:     public static final native int nativeGetInlineViewAttachmentChildIndex(long j, int i);
60: 
61:     public static final native float nativeGetInlineViewAttachmentHeight(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:61`
```text
59:     public static final native int nativeGetInlineViewAttachmentChildIndex(long j, int i);
60: 
61:     public static final native float nativeGetInlineViewAttachmentHeight(long j, int i);
62: 
63:     public static final native int nativeGetInlineViewAttachmentVerticalAlignment(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:63`
```text
61:     public static final native float nativeGetInlineViewAttachmentHeight(long j, int i);
62: 
63:     public static final native int nativeGetInlineViewAttachmentVerticalAlignment(long j, int i);
64: 
65:     public static final native float nativeGetInlineViewAttachmentWidth(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:65`
```text
63:     public static final native int nativeGetInlineViewAttachmentVerticalAlignment(long j, int i);
64: 
65:     public static final native float nativeGetInlineViewAttachmentWidth(long j, int i);
66: 
67:     public static final native Object nativeGetOnLayout(long j, int i);
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:136`
```text
134:     }
135: 
136:     public cor getImageAttachmentAtIndex(int index) {
137:         tj4 tj4Var = Companion;
138:         long nativeHandle = this.native.getNativeHandle();
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:140`
```text
138:         long nativeHandle = this.native.getNativeHandle();
139:         tj4Var.getClass();
140:         float fNativeGetImageAttachmentWidth = nativeGetImageAttachmentWidth(nativeHandle, index);
141:         if (fNativeGetImageAttachmentWidth <= 0.0f) {
142:             return null;
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:141`
```text
139:         tj4Var.getClass();
140:         float fNativeGetImageAttachmentWidth = nativeGetImageAttachmentWidth(nativeHandle, index);
141:         if (fNativeGetImageAttachmentWidth <= 0.0f) {
142:             return null;
143:         }
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:144`
```text
142:             return null;
143:         }
144:         return new cor(fNativeGetImageAttachmentWidth, nativeGetImageAttachmentHeight(this.native.getNativeHandle(), index), nativeGetImageAttachmentData(this.native.getNativeHandle(), index));
145:     }
146: 
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:147`
```text
145:     }
146: 
147:     public fls getInlineViewAttachmentAtIndex(int index) {
148:         tj4 tj4Var = Companion;
149:         long nativeHandle = this.native.getNativeHandle();
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:151`
```text
149:         long nativeHandle = this.native.getNativeHandle();
150:         tj4Var.getClass();
151:         int iNativeGetInlineViewAttachmentChildIndex = nativeGetInlineViewAttachmentChildIndex(nativeHandle, index);
152:         if (iNativeGetInlineViewAttachmentChildIndex < 0) {
153:             return null;
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:152`
```text
150:         tj4Var.getClass();
151:         int iNativeGetInlineViewAttachmentChildIndex = nativeGetInlineViewAttachmentChildIndex(nativeHandle, index);
152:         if (iNativeGetInlineViewAttachmentChildIndex < 0) {
153:             return null;
154:         }
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:155`
```text
153:             return null;
154:         }
155:         int iNativeGetInlineViewAttachmentVerticalAlignment = nativeGetInlineViewAttachmentVerticalAlignment(this.native.getNativeHandle(), index);
156:         int i = 1;
157:         int i2 = 2;
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:158`
```text
156:         int i = 1;
157:         int i2 = 2;
158:         if (iNativeGetInlineViewAttachmentVerticalAlignment == 1) {
159:             i = i2;
160:         } else if (iNativeGetInlineViewAttachmentVerticalAlignment == 2) {
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:160`
```text
158:         if (iNativeGetInlineViewAttachmentVerticalAlignment == 1) {
159:             i = i2;
160:         } else if (iNativeGetInlineViewAttachmentVerticalAlignment == 2) {
161:             i = 3;
162:         } else {
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:164`
```text
162:         } else {
163:             i2 = 4;
164:             if (iNativeGetInlineViewAttachmentVerticalAlignment == 3) {
165:                 i = i2;
166:             } else if (iNativeGetInlineViewAttachmentVerticalAlignment == 4) {
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:166`
```text
164:             if (iNativeGetInlineViewAttachmentVerticalAlignment == 3) {
165:                 i = i2;
166:             } else if (iNativeGetInlineViewAttachmentVerticalAlignment == 4) {
167:                 i = 5;
168:             }
```

### `sources/com/snap/valdi/attributes/impl/richtext/AttributedTextCpp.java:170`
```text
168:             }
169:         }
170:         return new fls(iNativeGetInlineViewAttachmentChildIndex, nativeGetInlineViewAttachmentWidth(this.native.getNativeHandle(), index), nativeGetInlineViewAttachmentHeight(this.native.getNativeHandle(), index), i);
171:     }
172: 
```

### `sources/com/snap/valdi/views/ValdiTextSelectionGroup.java:4`
```text
2: 
3: import android.R;
4: import android.content.ClipData;
5: import android.content.ClipboardManager;
6: import android.content.Context;
```

### `sources/com/snap/valdi/views/ValdiTextSelectionGroup.java:213`
```text
211:             return;
212:         }
213:         clipboardManager.setPrimaryClip(ClipData.newPlainText("", strZ));
214:         ValdiFunction valdiFunction = valdiTextSelectionGroup.t;
215:         if (valdiFunction != null) {
```

### `sources/com/snap/valdi/views/ValdiTextViewBase.java:514`
```text
512:                 for (n8d0 n8d0Var : list3) {
513:                     int i4 = i3 + 1;
514:                     fls inlineViewAttachmentAtIndex = o8d0Var2.a.getInlineViewAttachmentAtIndex(((Number) list2.get(i3)).intValue());
515:                     if (inlineViewAttachmentAtIndex != null) {
516:                         hls hlsVar = (hls) n8d0Var.c;
```

### `sources/com/snap/valdi/views/ValdiTextViewBase.java:515`
```text
513:                     int i4 = i3 + 1;
514:                     fls inlineViewAttachmentAtIndex = o8d0Var2.a.getInlineViewAttachmentAtIndex(((Number) list2.get(i3)).intValue());
515:                     if (inlineViewAttachmentAtIndex != null) {
516:                         hls hlsVar = (hls) n8d0Var.c;
517:                         hlsVar.c = inlineViewAttachmentAtIndex;
```

### `sources/com/snap/valdi/views/ValdiTextViewBase.java:517`
```text
515:                     if (inlineViewAttachmentAtIndex != null) {
516:                         hls hlsVar = (hls) n8d0Var.c;
517:                         hlsVar.c = inlineViewAttachmentAtIndex;
518:                         float f = inlineViewAttachmentAtIndex.c;
519:                         float f2 = hlsVar.a;
```

### `sources/com/snap/valdi/views/ValdiTextViewBase.java:518`
```text
516:                         hls hlsVar = (hls) n8d0Var.c;
517:                         hlsVar.c = inlineViewAttachmentAtIndex;
518:                         float f = inlineViewAttachmentAtIndex.c;
519:                         float f2 = hlsVar.a;
520:                         int iD0 = a4w.d0(f * f2);
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:62`
```text
60: import kotlin.jvm.internal.DefaultConstructorMarker;
61: 
62: @Metadata(d1 = {"\u0000î\u0001\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\t\n\u0002\u0010\u000e\n\u0002\b\u0011\n
63: public final class LoggingCoordinator {
64:     private static final long INITIAL_DISK_FULL_RETRY_DELAY_MS = 30000;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:90`
```text
88:     private final long startedAtMs;
89:     private final EventQueueStorage storage;
90:     private final cg9 uploadSignals;
91:     private static final Companion Companion = new Companion(null);
92:     private static final long LEASE_DURATION_MS = 120000;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:193`
```text
191:                 LoggingCoordinator loggingCoordinator = LoggingCoordinator.this;
192:                 this.label = 1;
193:                 Object objProcessUploads = loggingCoordinator.processUploads(this);
194:                 wqi wqiVar = wqi.a;
195:                 if (objProcessUploads == wqiVar) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:195`
```text
193:                 Object objProcessUploads = loggingCoordinator.processUploads(this);
194:                 wqi wqiVar = wqi.a;
195:                 if (objProcessUploads == wqiVar) {
196:                     return wqiVar;
197:                 }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:918`
```text
916:     }
917: 
918:     @uuj(c = "com.statsig.androidsdk.LoggingCoordinator", f = "LoggingCoordinator.kt", l = {481, 489, 492, 515, 519}, m = "processUploads", v = 2)
919:     @Metadata(k = 3, mv = {2, 3, 0}, xi = 48)
920:     public static final class C00121 extends rsg {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:940`
```text
938:             this.result = obj;
939:             this.label |= Integer.MIN_VALUE;
940:             return LoggingCoordinator.this.processUploads(this);
941:         }
942:     }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1042`
```text
1040:             this.this$0.retryJob = null;
1041:             this.this$0.retryDeadlineMs = null;
1042:             cg9 cg9Var = this.this$0.uploadSignals;
1043:             UploadSignal uploadSignal = new UploadSignal(yqeVar, i2, objArr == true ? 1 : 0);
1044:             this.label = 2;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1043`
```text
1041:             this.this$0.retryDeadlineMs = null;
1042:             cg9 cg9Var = this.this$0.uploadSignals;
1043:             UploadSignal uploadSignal = new UploadSignal(yqeVar, i2, objArr == true ? 1 : 0);
1044:             this.label = 2;
1045:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1079`
```text
1077:         this.legacyReplayClaimed = new AtomicBoolean(false);
1078:         this.commands = q2v.S(Integer.MAX_VALUE, 0, 6, null);
1079:         this.uploadSignals = q2v.S(Integer.MAX_VALUE, 0, 6, null);
1080:         this.admissionLock = new Object();
1081:         this.startedAtMs = ((Number) function0.invoke()).longValue();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1794`
```text
1792:             if (size >= 50) {
1793:                 this.eventsSinceAutomaticFlush = size % 50;
1794:                 this.uploadSignals.p(new UploadSignal(yqeVar, i3, objArr == true ? 1 : 0));
1795:             }
1796:             return wec0Var;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1830`
```text
1828:     }
1829: 
1830:     public final java.lang.Object processUploads(defpackage.psg<? super defpackage.wec0> r25) {
1831:         throw new UnsupportedOperationException("Method not decompiled: com.statsig.androidsdk.LoggingCoordinator.processUploads(psg):java.lang.Object");
1832:     }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1831`
```text
1829: 
1830:     public final java.lang.Object processUploads(defpackage.psg<? super defpackage.wec0> r25) {
1831:         throw new UnsupportedOperationException("Method not decompiled: com.statsig.androidsdk.LoggingCoordinator.processUploads(psg):java.lang.Object");
1832:     }
1833: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2009`
```text
2007:         }
2008:         this.commands.x(null);
2009:         this.uploadSignals.x(null);
2010:         oet oetVar3 = (oet) this.scope.getCoroutineContext().get(buy.n);
2011:         if (oetVar3 != null) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2102`
```text
2100:     }
2101: 
2102:     @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0007\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0005\b\u0082\b\u0018\u00002\u00020\u0001B\u0019\u0012\u0010\b\u0002\u0010\u0004\u001a\n\u0012\u0004\u0012\u00020\u0003\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006J\u0018\u0010\u0007\u001a\n\u0012\u0004\u0012\u00020\u0003\u0018\u00010\u0002HÆ\u0003¢\u0006\u0004\b\u0007
2103:     public static final class UploadSignal {
2104:         private final yqe completion;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2103`
```text
2101: 
2102:     @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0007\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0005\b\u0082\b\u0018\u00002\u00020\u0001B\u0019\u0012\u0010\b\u0002\u0010\u0004\u001a\n\u0012\u0004\u0012\u00020\u0003\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006J\u0018\u0010\u0007\u001a\n\u0012\u0004\u0012\u00020\u0003\u0018\u00010\u0002HÆ\u0003¢\u0006\u0004\b\u0007
2103:     public static final class UploadSignal {
2104:         private final yqe completion;
2105: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2106`
```text
2104:         private final yqe completion;
2105: 
2106:         public UploadSignal(yqe yqeVar, int i, DefaultConstructorMarker defaultConstructorMarker) {
2107:             this((i & 1) != 0 ? null : yqeVar);
2108:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2110`
```text
2108:         }
2109: 
2110:         public static UploadSignal copy$default(UploadSignal uploadSignal, yqe yqeVar, int i, Object obj) {
2111:             if ((i & 1) != 0) {
2112:                 yqeVar = uploadSignal.completion;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2112`
```text
2110:         public static UploadSignal copy$default(UploadSignal uploadSignal, yqe yqeVar, int i, Object obj) {
2111:             if ((i & 1) != 0) {
2112:                 yqeVar = uploadSignal.completion;
2113:             }
2114:             return uploadSignal.copy(yqeVar);
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2114`
```text
2112:                 yqeVar = uploadSignal.completion;
2113:             }
2114:             return uploadSignal.copy(yqeVar);
2115:         }
2116: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2121`
```text
2119:         }
2120: 
2121:         public final UploadSignal copy(yqe completion) {
2122:             return new UploadSignal(completion);
2123:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2122`
```text
2120: 
2121:         public final UploadSignal copy(yqe completion) {
2122:             return new UploadSignal(completion);
2123:         }
2124: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2129`
```text
2127:                 return true;
2128:             }
2129:             return (other instanceof UploadSignal) && wnm.k(this.completion, ((UploadSignal) other).completion);
2130:         }
2131: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2145`
```text
2143: 
2144:         public String toString() {
2145:             return "UploadSignal(completion=" + this.completion + ")";
2146:         }
2147: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2148`
```text
2146:         }
2147: 
2148:         public UploadSignal(yqe yqeVar) {
2149:             this.completion = yqeVar;
2150:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:2152`
```text
2150:         }
2151: 
2152:         public UploadSignal() {
2153:             this(null, 1, 0 == true ? 1 : 0);
2154:         }
```

### `sources/com/withpersona/sdk2/inquiry/document/network/DocumentFileUploadResponse.java:8`
```text
6: 
7: @ugt(generateAdapter = StatsigRuntimeMutableOptionsKt.DEFAULT_LOGGING_ENABLED)
8: @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\b\u0007\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/withpersona/sdk2/inquiry/document/network/DocumentFileUploadResponse;", "", "document_release"}, k = 1, mv = {2, 2, 0}, xi = 48)
9: public final class DocumentFileUploadResponse {
10:     public final DocumentFileData a;
```

### `sources/com/withpersona/sdk2/inquiry/document/network/DocumentFileUploadResponse.java:9`
```text
7: @ugt(generateAdapter = StatsigRuntimeMutableOptionsKt.DEFAULT_LOGGING_ENABLED)
8: @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\b\u0007\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/withpersona/sdk2/inquiry/document/network/DocumentFileUploadResponse;", "", "document_release"}, k = 1, mv = {2, 2, 0}, xi = 48)
9: public final class DocumentFileUploadResponse {
10:     public final DocumentFileData a;
11: 
```

### `sources/com/withpersona/sdk2/inquiry/document/network/DocumentFileUploadResponse.java:12`
```text
10:     public final DocumentFileData a;
11: 
12:     public DocumentFileUploadResponse(DocumentFileData documentFileData) {
13:         this.a = documentFileData;
14:     }
```

### `sources/com/withpersona/sdk2/inquiry/internal/fallbackmode/g.java:248`
```text
246:             return obj;
247:         }
248:         FallbackModeService.UploadUrlResponse uploadUrlResponse = (FallbackModeService.UploadUrlResponse) ((NetworkCallResult.Success) networkCallResult2).getResponse();
249:         String str2 = uploadUrlResponse != null ? uploadUrlResponse.a : null;
250:         if (str2 == null) {
```

### `sources/com/withpersona/sdk2/inquiry/internal/fallbackmode/g.java:249`
```text
247:         }
248:         FallbackModeService.UploadUrlResponse uploadUrlResponse = (FallbackModeService.UploadUrlResponse) ((NetworkCallResult.Success) networkCallResult2).getResponse();
249:         String str2 = uploadUrlResponse != null ? uploadUrlResponse.a : null;
250:         if (str2 == null) {
251:             or40 or40Var3 = qr40.a;
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:20`
```text
18: 
19: @ugt(generateAdapter = StatsigRuntimeMutableOptionsKt.DEFAULT_LOGGING_ENABLED)
20: public final class GenericFileUploadErrorResponse {
21:     public static final Companion Companion = new Companion(null);
22:     private final List<DocumentErrorResponse> errors;
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:63`
```text
61:     }
62: 
63:     public GenericFileUploadErrorResponse(List<? extends DocumentErrorResponse> list) {
64:         this.errors = list;
65:     }
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:67`
```text
65:     }
66: 
67:     public static GenericFileUploadErrorResponse copy$default(GenericFileUploadErrorResponse genericFileUploadErrorResponse, List list, int i, Object obj) {
68:         if ((i & 1) != 0) {
69:             list = genericFileUploadErrorResponse.errors;
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:69`
```text
67:     public static GenericFileUploadErrorResponse copy$default(GenericFileUploadErrorResponse genericFileUploadErrorResponse, List list, int i, Object obj) {
68:         if ((i & 1) != 0) {
69:             list = genericFileUploadErrorResponse.errors;
70:         }
71:         return genericFileUploadErrorResponse.copy(list);
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:71`
```text
69:             list = genericFileUploadErrorResponse.errors;
70:         }
71:         return genericFileUploadErrorResponse.copy(list);
72:     }
73: 
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:78`
```text
76:     }
77: 
78:     public final GenericFileUploadErrorResponse copy(List<? extends DocumentErrorResponse> list) {
79:         return new GenericFileUploadErrorResponse(list);
80:     }
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:79`
```text
77: 
78:     public final GenericFileUploadErrorResponse copy(List<? extends DocumentErrorResponse> list) {
79:         return new GenericFileUploadErrorResponse(list);
80:     }
81: 
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:86`
```text
84:             return true;
85:         }
86:         return (obj instanceof GenericFileUploadErrorResponse) && wnm.k(this.errors, ((GenericFileUploadErrorResponse) obj).errors);
87:     }
88: 
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:98`
```text
96: 
97:     public String toString() {
98:         return y8k.m("GenericFileUploadErrorResponse(errors=", ")", this.errors);
99:     }
100: 
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:152`
```text
150:                 public static final Parcelable.Creator<Details> CREATOR = new Creator();
151:                 private final List<String> enabledFileTypes;
152:                 private final String uploadedFileType;
153: 
154:                 public Details(@egt(name = "uploaded_file_type") String str, @egt(name = "enabled_file_types") List<String> list) {
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:154`
```text
152:                 private final String uploadedFileType;
153: 
154:                 public Details(@egt(name = "uploaded_file_type") String str, @egt(name = "enabled_file_types") List<String> list) {
155:                     this.uploadedFileType = str;
156:                     this.enabledFileTypes = list;
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:155`
```text
153: 
154:                 public Details(@egt(name = "uploaded_file_type") String str, @egt(name = "enabled_file_types") List<String> list) {
155:                     this.uploadedFileType = str;
156:                     this.enabledFileTypes = list;
157:                 }
```

### `sources/com/withpersona/sdk2/inquiry/network/core/GenericFileUploadErrorResponse.java:168`
```text
166:                 }
167: 
168:                 public final String getUploadedFileType() {
169:                     return this.uploadedFileType;
170:                 }
```

_Hits captured: 180 (cap 180)_

## VOICE_AUDIO

### `sources/com/google/android/gms/internal/mlkit_common/zzst.java:44`
```text
42:                 long modelFirstUseTimeMs = sharedPrefManager.getModelFirstUseTimeMs(remoteModel);
43:                 if (modelFirstUseTimeMs == 0) {
44:                     modelFirstUseTimeMs = SystemClock.elapsedRealtime();
45:                     sharedPrefManager.setModelFirstUseTimeMs(remoteModel, modelFirstUseTimeMs);
46:                 }
```

### `sources/com/google/android/gms/internal/mlkit_common/zzst.java:55`
```text
53:                 zza.e("RemoteModelUtils", "Model downloaded without its beginning time recorded.");
54:             } else {
55:                 zzmzVar.zze(Long.valueOf(SystemClock.elapsedRealtime() - modelDownloadBeginTimeMs2));
56:             }
57:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzap.java:8`
```text
6:     @Override
7:     public final long zza() {
8:         return SystemClock.elapsedRealtimeNanos();
9:     }
10: }
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzaq.java:8`
```text
6:     @Override
7:     public final long zza() {
8:         return SystemClock.elapsedRealtime() * 1000000;
9:     }
10: }
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzar.java:11`
```text
9:         zzbb zzaqVar;
10:         try {
11:             SystemClock.elapsedRealtimeNanos();
12:             zzaqVar = new zzap();
13:         } catch (Throwable unused) {
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzar.java:14`
```text
12:             zzaqVar = new zzap();
13:         } catch (Throwable unused) {
14:             SystemClock.elapsedRealtime();
15:             zzaqVar = new zzaq();
16:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:132`
```text
130: 
131:     public final void zzf(zzwo zzwoVar, zzrc zzrcVar) {
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:133`
```text
131:     public final void zzf(zzwo zzwoVar, zzrc zzrcVar) {
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
135:             zze(zzwoVar.zza(), zzrcVar, zzj());
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:134`
```text
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
135:             zze(zzwoVar.zza(), zzrcVar, zzj());
136:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:168`
```text
166:         }
167:         ((zzcy) this.zzl.get(zzrcVar)).zzt(obj, Long.valueOf(j));
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:169`
```text
167:         ((zzcy) this.zzl.get(zzrcVar)).zzt(obj, Long.valueOf(j));
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
171:             MLTaskExecutor.workerThreadExecutor().execute(new Runnable() {
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzwp.java:170`
```text
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzrcVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzrcVar, Long.valueOf(jElapsedRealtime));
171:             MLTaskExecutor.workerThreadExecutor().execute(new Runnable() {
172:                 @Override
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzlx.java:57`
```text
55: 
56:     public zzlx zzb() {
57:         this.zze = SystemClock.elapsedRealtimeNanos() / 1000;
58:         return this;
59:     }
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzlx.java:62`
```text
60: 
61:     public void zzc(long j) {
62:         long jElapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos() / 1000;
63:         long j2 = this.zzf;
64:         if (j2 != 0 && jElapsedRealtimeNanos - j2 >= 1000000) {
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzlx.java:64`
```text
62:         long jElapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos() / 1000;
63:         long j2 = this.zzf;
64:         if (j2 != 0 && jElapsedRealtimeNanos - j2 >= 1000000) {
65:             zza();
66:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzlx.java:67`
```text
65:             zza();
66:         }
67:         this.zzf = jElapsedRealtimeNanos;
68:         this.zzc++;
69:         this.zzd += j;
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzlx.java:82`
```text
80: 
81:     public void zzd(long j) {
82:         zzc((SystemClock.elapsedRealtimeNanos() / 1000) - j);
83:     }
84: }
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzmj.java:101`
```text
99:         zzii zziiVar;
100:         zzio zzioVar;
101:         long jElapsedRealtime = SystemClock.elapsedRealtime();
102:         if (this.zzk.get(zzivVar) != null && jElapsedRealtime - ((Long) this.zzk.get(zzivVar)).longValue() <= 30000) {
103:             return;
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzmj.java:102`
```text
100:         zzio zzioVar;
101:         long jElapsedRealtime = SystemClock.elapsedRealtime();
102:         if (this.zzk.get(zzivVar) != null && jElapsedRealtime - ((Long) this.zzk.get(zzivVar)).longValue() <= 30000) {
103:             return;
104:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzmj.java:105`
```text
103:             return;
104:         }
105:         this.zzk.put(zzivVar, Long.valueOf(jElapsedRealtime));
106:         int i = zzmtVar.zza;
107:         int i2 = zzmtVar.zzb;
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzmu.java:15`
```text
13: 
14:     private static zzmt zzc(int i, int i2, long j, int i3, int i4, int i5, int i6) {
15:         return new zzmt(i, i2, i5, i3, i4, SystemClock.elapsedRealtime() - j, i6);
16:     }
17: }
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:128`
```text
126: 
127:     public final void zzf(zzoa zzoaVar, zzkt zzktVar) {
128:         long jElapsedRealtime = SystemClock.elapsedRealtime();
129:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
130:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:129`
```text
127:     public final void zzf(zzoa zzoaVar, zzkt zzktVar) {
128:         long jElapsedRealtime = SystemClock.elapsedRealtime();
129:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
130:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
131:             zze(zzoaVar.zza(), zzktVar, zzj());
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:130`
```text
128:         long jElapsedRealtime = SystemClock.elapsedRealtime();
129:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
130:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
131:             zze(zzoaVar.zza(), zzktVar, zzj());
132:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:164`
```text
162:         }
163:         ((zzbs) this.zzl.get(zzktVar)).zzo(obj, Long.valueOf(j));
164:         long jElapsedRealtime = SystemClock.elapsedRealtime();
165:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
166:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:165`
```text
163:         ((zzbs) this.zzl.get(zzktVar)).zzo(obj, Long.valueOf(j));
164:         long jElapsedRealtime = SystemClock.elapsedRealtime();
165:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
166:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
167:             final byte[] bArr = null;
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzoc.java:166`
```text
164:         long jElapsedRealtime = SystemClock.elapsedRealtime();
165:         if (zzk(zzktVar, jElapsedRealtime, 30L)) {
166:             this.zzk.put(zzktVar, Long.valueOf(jElapsedRealtime));
167:             final byte[] bArr = null;
168:             MLTaskExecutor.workerThreadExecutor().execute(new Runnable(zzktVar, zzgVar, bArr) {
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:132`
```text
130: 
131:     public final void zzf(zzub zzubVar, zzov zzovVar) {
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:133`
```text
131:     public final void zzf(zzub zzubVar, zzov zzovVar) {
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
135:             zze(zzubVar.zza(), zzovVar, zzj());
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:134`
```text
132:         long jElapsedRealtime = SystemClock.elapsedRealtime();
133:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
134:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
135:             zze(zzubVar.zza(), zzovVar, zzj());
136:         }
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:168`
```text
166:         }
167:         ((zzbp) this.zzl.get(zzovVar)).zzm(obj, Long.valueOf(j));
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:169`
```text
167:         ((zzbp) this.zzl.get(zzovVar)).zzm(obj, Long.valueOf(j));
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
171:             MLTaskExecutor.workerThreadExecutor().execute(new Runnable() {
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzuc.java:170`
```text
168:         long jElapsedRealtime = SystemClock.elapsedRealtime();
169:         if (zzk(zzovVar, jElapsedRealtime, 30L)) {
170:             this.zzk.put(zzovVar, Long.valueOf(jElapsedRealtime));
171:             MLTaskExecutor.workerThreadExecutor().execute(new Runnable() {
172:                 @Override
```

### `sources/com/google/android/gms/location/LocationResult.java:52`
```text
50:         for (Location location : list2) {
51:             Location location2 = (Location) it.next();
52:             if (Double.compare(location.getLatitude(), location2.getLatitude()) != 0 || Double.compare(location.getLongitude(), location2.getLongitude()) != 0 || location.getTime() != location2.getTime() || location.getElapsedRealtimeNanos() != location2.getElapsedRealtimeNanos() || !fas.G(location.getProvider(), location2.getProvider())) {
53:                 return false;
54:             }
```

### `sources/com/google/android/gms/location/LocationResult.java:179`
```text
177:                     sb.append(string3);
178:                 }
179:                 long jCurrentTimeMillis = System.currentTimeMillis() - SystemClock.elapsedRealtime();
180:                 sb.append(", ert=");
181:                 long elapsedRealtimeNanos = (location.getElapsedRealtimeNanos() / 1000000) + jCurrentTimeMillis;
```

### `sources/com/google/android/gms/location/LocationResult.java:181`
```text
179:                 long jCurrentTimeMillis = System.currentTimeMillis() - SystemClock.elapsedRealtime();
180:                 sb.append(", ert=");
181:                 long elapsedRealtimeNanos = (location.getElapsedRealtimeNanos() / 1000000) + jCurrentTimeMillis;
182:                 if (elapsedRealtimeNanos >= 0) {
183:                     string = w4i0.a.format(new Date(elapsedRealtimeNanos));
```

### `sources/com/google/android/gms/location/LocationResult.java:182`
```text
180:                 sb.append(", ert=");
181:                 long elapsedRealtimeNanos = (location.getElapsedRealtimeNanos() / 1000000) + jCurrentTimeMillis;
182:                 if (elapsedRealtimeNanos >= 0) {
183:                     string = w4i0.a.format(new Date(elapsedRealtimeNanos));
184:                 } else {
```

### `sources/com/google/android/gms/location/LocationResult.java:183`
```text
181:                 long elapsedRealtimeNanos = (location.getElapsedRealtimeNanos() / 1000000) + jCurrentTimeMillis;
182:                 if (elapsedRealtimeNanos >= 0) {
183:                     string = w4i0.a.format(new Date(elapsedRealtimeNanos));
184:                 } else {
185:                     SimpleDateFormat simpleDateFormat = w4i0.a;
```

### `sources/com/google/android/gms/location/LocationResult.java:186`
```text
184:                 } else {
185:                     SimpleDateFormat simpleDateFormat = w4i0.a;
186:                     string = Long.toString(elapsedRealtimeNanos);
187:                 }
188:                 sb.append(string);
```

### `sources/com/google/mlkit/common/sdkinternal/SharedPrefManager.java:99`
```text
97:         String modelNameForPersist = modelInfo.getModelNameForPersist();
98:         String modelHash = modelInfo.getModelHash();
99:         zza().edit().putString("downloading_model_hash_" + modelNameForPersist, modelHash).putLong("downloading_model_id_" + modelNameForPersist, j).putLong("downloading_begin_time_" + modelNameForPersist, SystemClock.elapsedRealtime()).apply();
100:     }
101: 
```

### `sources/com/google/mlkit/vision/common/InputImage.java:62`
```text
60: 
61:     public static InputImage fromBitmap(Bitmap bitmap, int i) {
62:         long jElapsedRealtime = SystemClock.elapsedRealtime();
63:         InputImage inputImage = new InputImage(bitmap, i);
64:         zzc(-1, 1, jElapsedRealtime, bitmap.getHeight(), bitmap.getWidth(), bitmap.getAllocationByteCount(), i);
```

### `sources/com/google/mlkit/vision/common/InputImage.java:64`
```text
62:         long jElapsedRealtime = SystemClock.elapsedRealtime();
63:         InputImage inputImage = new InputImage(bitmap, i);
64:         zzc(-1, 1, jElapsedRealtime, bitmap.getHeight(), bitmap.getWidth(), bitmap.getAllocationByteCount(), i);
65:         return inputImage;
66:     }
```

### `sources/com/google/mlkit/vision/common/InputImage.java:69`
```text
67: 
68:     public static InputImage fromByteArray(byte[] bArr, int i, int i2, int i3, int i4) {
69:         long jElapsedRealtime = SystemClock.elapsedRealtime();
70:         p0d0.u(bArr);
71:         InputImage inputImage = new InputImage(ByteBuffer.wrap(bArr), i, i2, i3, i4);
```

### `sources/com/google/mlkit/vision/common/InputImage.java:72`
```text
70:         p0d0.u(bArr);
71:         InputImage inputImage = new InputImage(ByteBuffer.wrap(bArr), i, i2, i3, i4);
72:         zzc(i4, 2, jElapsedRealtime, i2, i, bArr.length, i3);
73:         return inputImage;
74:     }
```

### `sources/com/google/mlkit/vision/common/InputImage.java:77`
```text
75: 
76:     public static InputImage fromByteBuffer(ByteBuffer byteBuffer, int i, int i2, int i3, int i4) {
77:         long jElapsedRealtime = SystemClock.elapsedRealtime();
78:         InputImage inputImage = new InputImage(byteBuffer, i, i2, i3, i4);
79:         zzc(i4, 3, jElapsedRealtime, i2, i, byteBuffer.limit(), i3);
```

### `sources/com/google/mlkit/vision/common/InputImage.java:79`
```text
77:         long jElapsedRealtime = SystemClock.elapsedRealtime();
78:         InputImage inputImage = new InputImage(byteBuffer, i, i2, i3, i4);
79:         zzc(i4, 3, jElapsedRealtime, i2, i, byteBuffer.limit(), i3);
80:         return inputImage;
81:     }
```

### `sources/com/google/mlkit/vision/common/InputImage.java:86`
```text
84:         p0d0.v(context, "Please provide a valid Context");
85:         p0d0.v(uri, "Please provide a valid imageUri");
86:         long jElapsedRealtime = SystemClock.elapsedRealtime();
87:         Bitmap bitmapZza = ImageUtils.getInstance().zza(context.getContentResolver(), uri);
88:         InputImage inputImage = new InputImage(bitmapZza, 0);
```

### `sources/com/google/mlkit/vision/common/InputImage.java:89`
```text
87:         Bitmap bitmapZza = ImageUtils.getInstance().zza(context.getContentResolver(), uri);
88:         InputImage inputImage = new InputImage(bitmapZza, 0);
89:         zzc(-1, 4, jElapsedRealtime, bitmapZza.getHeight(), bitmapZza.getWidth(), bitmapZza.getAllocationByteCount(), 0);
90:         return inputImage;
91:     }
```

### `sources/com/google/mlkit/vision/common/InputImage.java:116`
```text
114:         int iLimit;
115:         InputImage inputImage;
116:         long jElapsedRealtime = SystemClock.elapsedRealtime();
117:         p0d0.v(image, "Please provide a valid image");
118:         zza(i);
```

### `sources/com/google/mlkit/vision/common/InputImage.java:142`
```text
140:             inputImage = inputImage2;
141:         }
142:         zzc(image2.getFormat(), 5, jElapsedRealtime, image2.getHeight(), image2.getWidth(), iLimit, i2);
143:         return inputImage;
144:     }
```

### `sources/com/google/mlkit/vision/face/internal/zza.java:76`
```text
74:         }
75:         try {
76:             List listZzd = zzoyVar.zzd(ImageUtils.getInstance().getImageDataWrapper(inputImage), new zzoq(inputImage.getFormat(), inputImage.getWidth(), inputImage.getHeight(), CommonConvertUtils.convertToMVRotation(inputImage.getRotationDegrees()), SystemClock.elapsedRealtime()));
77:             ArrayList arrayList = new ArrayList();
78:             Iterator it = listZzd.iterator();
```

### `sources/com/openai/chatgpt/R.java:3367`
```text
3365:         public static final int mic_filled = 0x7f0802c5;
3366:         public static final int mic_filled_off = 0x7f0802c6;
3367:         public static final int microphone = 0x7f0802c7;
3368:         public static final int microphone_slash = 0x7f0802c8;
3369:         public static final int minus_circle = 0x7f0802c9;
```

### `sources/com/openai/chatgpt/R.java:3368`
```text
3366:         public static final int mic_filled_off = 0x7f0802c6;
3367:         public static final int microphone = 0x7f0802c7;
3368:         public static final int microphone_slash = 0x7f0802c8;
3369:         public static final int minus_circle = 0x7f0802c9;
3370:         public static final int minus_md = 0x7f0802ca;
```

### `sources/com/openai/chatgpt/R.java:3933`
```text
3931:         public static final int whisk = 0x7f080576;
3932:         public static final int widget_camera = 0x7f080577;
3933:         public static final int widget_microphone = 0x7f080578;
3934:         public static final int widget_photo = 0x7f080579;
3935:         public static final int widget_preview = 0x7f08057a;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure.java:1`
```text
1: package com.openai.feature.conversation.common.speech;
2: 
3: import kotlin.Metadata;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechAudioPlayerFailure extends Exception {
7: }
```

### `sources/com/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechAudioPlayerFailure extends Exception {
7: }
```

### `sources/com/openai/feature/conversation/common/speech/SpeechPlaybackFailure.java:1`
```text
1: package com.openai.feature.conversation.common.speech;
2: 
3: import kotlin.Metadata;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechPlaybackFailure.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechPlaybackFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechPlaybackFailure extends Exception {
7:     public final int a;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechPlaybackFailure.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechPlaybackFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechPlaybackFailure extends Exception {
7:     public final int a;
8:     public final Integer b;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechPlaybackFailure.java:11`
```text
9:     public final String c;
10: 
11:     public SpeechPlaybackFailure(int i, Integer num, String str, Throwable th) {
12:         super(th);
13:         this.a = i;
```

### `sources/com/openai/valdi/voice/VoiceCapabilities.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'advancedVoice':b,'dictation':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class VoiceCapabilities extends b {
```

### `sources/com/openai/valdi/voice/VoiceCapabilities.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'advancedVoice':b,'dictation':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class VoiceCapabilities extends b {
10:     private boolean _advancedVoice;
```

### `sources/com/openai/valdi/voice/VoiceCapabilities.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class VoiceCapabilities extends b {
10:     private boolean _advancedVoice;
11:     private boolean _dictation;
12: 
```

### `sources/com/openai/valdi/voice/VoiceCapabilities.java:14`
```text
12: 
13:     public VoiceCapabilities(boolean z, boolean z2) {
14:         this._advancedVoice = z;
15:         this._dictation = z2;
16:     }
```

### `sources/com/openai/valdi/voice/VoiceSession.java:9`
```text
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u000f\u0010\t\u001a\u00020\u0002H&¢\u0006\u0004\b\t\u0010\u0004J\u0017\u0010\r\u001a\u00020\f
10: @t5d0(propertyReplacements = "", proxyClass = ose0.class, schema = "'finish':f|m|(),'setMuted':f|m|(b),'stop':f|m|()", typeReferences = {})
11: public interface VoiceSession extends ValdiMarshallable {
```

### `sources/com/openai/valdi/voice/VoiceSession.java:10`
```text
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u000f\u0010\t\u001a\u00020\u0002H&¢\u0006\u0004\b\t\u0010\u0004J\u0017\u0010\r\u001a\u00020\f
10: @t5d0(propertyReplacements = "", proxyClass = ose0.class, schema = "'finish':f|m|(),'setMuted':f|m|(b),'stop':f|m|()", typeReferences = {})
11: public interface VoiceSession extends ValdiMarshallable {
12:     void finish();
```

### `sources/com/openai/valdi/voice/VoiceSession.java:17`
```text
15:     int pushToMarshaller(ValdiMarshaller marshaller);
16: 
17:     void setMuted(boolean muted);
18: 
19:     void stop();
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:223`
```text
221:             HashMap map = inputData.a;
222:             String strA5 = inputData.a("feedback_type");
223:             if (strA5 == null || (f9e0VarValueOf = f9e0.valueOf(strA5)) == null || (strA = inputData.a("feedback_voice_mode")) == null || (ife0VarValueOf = ife0.valueOf(strA)) == null) {
224:                 i = 14;
225:                 y8e0Var = null;
```

### `sources/com/statsig/androidsdk/Diagnostics.java:150`
```text
148:             return false;
149:         }
150:         Marker marker = new Marker(key, ActionType.END, Double.valueOf(SystemClock.elapsedRealtimeNanos() / 1000000.0d), step, null, Boolean.valueOf(success), null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 4194256, null);
151:         int i2 = WhenMappings.$EnumSwitchMapping$0[contextType.ordinal()];
152:         if (i2 != 1 && i2 != 2) {
```

### `sources/com/statsig/androidsdk/Diagnostics.java:176`
```text
174:             return false;
175:         }
176:         Marker marker = new Marker(key, ActionType.START, Double.valueOf(SystemClock.elapsedRealtimeNanos() / 1000000.0d), step, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 4194288, null);
177:         int i2 = WhenMappings.$EnumSwitchMapping$0[contextType.ordinal()];
178:         if (i2 != 1 && i2 != 2) {
```

### `sources/com/withpersona/sdk2/camera/camera2/recorder/AudioEncoder$RecordAudioException.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\f\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"com/withpersona/sdk2/camera/camera2/recorder/AudioEncoder$RecordAudioException", "Ljava/lang/RuntimeException;", "Lkotlin/RuntimeException;", "camera_release"}, k = 1, mv = {2, 2, 0}, xi = 48)
6: public final class AudioEncoder$RecordAudioException extends RuntimeException {
7: }
```

### `sources/com/withpersona/sdk2/camera/camera2/recorder/AudioEncoder$RecordAudioException.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\f\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"com/withpersona/sdk2/camera/camera2/recorder/AudioEncoder$RecordAudioException", "Ljava/lang/RuntimeException;", "Lkotlin/RuntimeException;", "camera_release"}, k = 1, mv = {2, 2, 0}, xi = 48)
6: public final class AudioEncoder$RecordAudioException extends RuntimeException {
7: }
```

### `sources/com/withpersona/sdk2/inquiry/governmentid/video_capture/VideoCaptureConfig.java:16`
```text
14: import kotlin.Metadata;
15: 
16: @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0006\b\u0087\b\u0018\u00002\u00020\u0001BA\u0012\b\b\u0002\u0010\u0003\u001a\u00020\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\u0004\u0012\n\b\u0001\u0010\n\u001a\u0004\u0018\u00010\t\u0012\u0006\
17: public final class VideoCaptureConfig implements Parcelable {
18:     public static final Parcelable.Creator<VideoCaptureConfig> CREATOR = new pjd0();
```

### `sources/com/withpersona/sdk2/inquiry/governmentid/video_capture/VideoCaptureConfig.java:33`
```text
31:     }
32: 
33:     public final VideoCaptureConfig copy(long maxRecordingLengthMs, List<? extends NextStep.GovernmentId.CaptureFileType> enabledCaptureFileTypes, List<? extends rjd0> videoCaptureMethods, @egt(name = "webRTCJwt") String webRtcJwt, boolean recordAudio) {
34:         return new VideoCaptureConfig(maxRecordingLengthMs, enabledCaptureFileTypes, videoCaptureMethods, webRtcJwt, recordAudio);
35:     }
```

### `sources/com/withpersona/sdk2/inquiry/governmentid/video_capture/VideoCaptureConfig.java:34`
```text
32: 
33:     public final VideoCaptureConfig copy(long maxRecordingLengthMs, List<? extends NextStep.GovernmentId.CaptureFileType> enabledCaptureFileTypes, List<? extends rjd0> videoCaptureMethods, @egt(name = "webRTCJwt") String webRtcJwt, boolean recordAudio) {
34:         return new VideoCaptureConfig(maxRecordingLengthMs, enabledCaptureFileTypes, videoCaptureMethods, webRtcJwt, recordAudio);
35:     }
36: 
```

### `sources/com/withpersona/sdk2/inquiry/governmentid/video_capture/VideoCaptureConfig.java:60`
```text
58: 
59:     public final String toString() {
60:         return "VideoCaptureConfig(maxRecordingLengthMs=" + this.a + ", enabledCaptureFileTypes=" + this.b + ", videoCaptureMethods=" + this.c + ", webRtcJwt=" + this.d + ", recordAudio=" + this.e + ")";
61:     }
62: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3829`
```text
3827: 
3828:         @ugt(generateAdapter = StatsigRuntimeMutableOptionsKt.DEFAULT_LOGGING_ENABLED)
3829:         @Metadata(d1 = {"\u0000(\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u000b\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u000e\b\u0007\u0018\u00002\u00020\u0001Bg\u0012\b\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\b\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0001\u0010\u0005\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0001\u0010\u0006\u001a\u0004\u0018\u00010\u0002\u0012\b\u0010\u0007\u001a\u0004
3830:         public static final class PromptPage implements Parcelable {
3831:             public static final Parcelable.Creator<PromptPage> CREATOR = new Creator();
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3836`
```text
3834:             private final String cameraPermissionsPrompt;
3835:             private final String cameraPermissionsTitle;
3836:             private final String microphonePermissionsBtnCancel;
3837:             private final String microphonePermissionsBtnContinueMobile;
3838:             private final String microphonePermissionsPrompt;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3837`
```text
3835:             private final String cameraPermissionsTitle;
3836:             private final String microphonePermissionsBtnCancel;
3837:             private final String microphonePermissionsBtnContinueMobile;
3838:             private final String microphonePermissionsPrompt;
3839:             private final String microphonePermissionsTitle;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3838`
```text
3836:             private final String microphonePermissionsBtnCancel;
3837:             private final String microphonePermissionsBtnContinueMobile;
3838:             private final String microphonePermissionsPrompt;
3839:             private final String microphonePermissionsTitle;
3840:             private final String navBarTitle;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3839`
```text
3837:             private final String microphonePermissionsBtnContinueMobile;
3838:             private final String microphonePermissionsPrompt;
3839:             private final String microphonePermissionsTitle;
3840:             private final String navBarTitle;
3841: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3867`
```text
3865:             }
3866: 
3867:             public final String getMicrophonePermissionsBtnCancel() {
3868:                 return this.microphonePermissionsBtnCancel;
3869:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3868`
```text
3866: 
3867:             public final String getMicrophonePermissionsBtnCancel() {
3868:                 return this.microphonePermissionsBtnCancel;
3869:             }
3870: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3871`
```text
3869:             }
3870: 
3871:             public final String getMicrophonePermissionsBtnContinueMobile() {
3872:                 return this.microphonePermissionsBtnContinueMobile;
3873:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3872`
```text
3870: 
3871:             public final String getMicrophonePermissionsBtnContinueMobile() {
3872:                 return this.microphonePermissionsBtnContinueMobile;
3873:             }
3874: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3875`
```text
3873:             }
3874: 
3875:             public final String getMicrophonePermissionsPrompt() {
3876:                 return this.microphonePermissionsPrompt;
3877:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3876`
```text
3874: 
3875:             public final String getMicrophonePermissionsPrompt() {
3876:                 return this.microphonePermissionsPrompt;
3877:             }
3878: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3879`
```text
3877:             }
3878: 
3879:             public final String getMicrophonePermissionsTitle() {
3880:                 return this.microphonePermissionsTitle;
3881:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3880`
```text
3878: 
3879:             public final String getMicrophonePermissionsTitle() {
3880:                 return this.microphonePermissionsTitle;
3881:             }
3882: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3893`
```text
3891:                 dest.writeString(this.cameraPermissionsAllowButtonText);
3892:                 dest.writeString(this.cameraPermissionsCancelButtonText);
3893:                 dest.writeString(this.microphonePermissionsBtnCancel);
3894:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
3895:                 dest.writeString(this.microphonePermissionsPrompt);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3894`
```text
3892:                 dest.writeString(this.cameraPermissionsCancelButtonText);
3893:                 dest.writeString(this.microphonePermissionsBtnCancel);
3894:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
3895:                 dest.writeString(this.microphonePermissionsPrompt);
3896:                 dest.writeString(this.microphonePermissionsTitle);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3895`
```text
3893:                 dest.writeString(this.microphonePermissionsBtnCancel);
3894:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
3895:                 dest.writeString(this.microphonePermissionsPrompt);
3896:                 dest.writeString(this.microphonePermissionsTitle);
3897:                 dest.writeString(this.navBarTitle);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3896`
```text
3894:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
3895:                 dest.writeString(this.microphonePermissionsPrompt);
3896:                 dest.writeString(this.microphonePermissionsTitle);
3897:                 dest.writeString(this.navBarTitle);
3898:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3918`
```text
3916:                 this.cameraPermissionsAllowButtonText = str3;
3917:                 this.cameraPermissionsCancelButtonText = str4;
3918:                 this.microphonePermissionsBtnCancel = str5;
3919:                 this.microphonePermissionsBtnContinueMobile = str6;
3920:                 this.microphonePermissionsPrompt = str7;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3919`
```text
3917:                 this.cameraPermissionsCancelButtonText = str4;
3918:                 this.microphonePermissionsBtnCancel = str5;
3919:                 this.microphonePermissionsBtnContinueMobile = str6;
3920:                 this.microphonePermissionsPrompt = str7;
3921:                 this.microphonePermissionsTitle = str8;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3920`
```text
3918:                 this.microphonePermissionsBtnCancel = str5;
3919:                 this.microphonePermissionsBtnContinueMobile = str6;
3920:                 this.microphonePermissionsPrompt = str7;
3921:                 this.microphonePermissionsTitle = str8;
3922:                 this.navBarTitle = str9;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:3921`
```text
3919:                 this.microphonePermissionsBtnContinueMobile = str6;
3920:                 this.microphonePermissionsPrompt = str7;
3921:                 this.microphonePermissionsTitle = str8;
3922:                 this.navBarTitle = str9;
3923:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5408`
```text
5406: 
5407:         @ugt(generateAdapter = StatsigRuntimeMutableOptionsKt.DEFAULT_LOGGING_ENABLED)
5408:         @Metadata(d1 = {"\u0000(\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0010\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0013\b\u0007\u0018\u00002\u00020\u0001B\u0099\u0001\u0012\b\b\u0001\u0010\u0003\u001a\u00020\u0002\u0012\b\b\u0001\u0010\u0004\u001a\u00020\u0002\u0012\b\b\u0001\u0010\u0005\u001a\u00020\u0002\u0012\b\b\u0001\u0010\u0006\u001a\u00020\u0002\u0012\b\b\u0001\u0010\u0007\u001a\u00020\u0002\u0012
5409:         public static final class PromptPage implements Parcelable {
5410:             public static final Parcelable.Creator<PromptPage> CREATOR = new Creator();
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5417`
```text
5415:             private final String cameraPermissionsTitle;
5416:             private final String disclosure;
5417:             private final String microphonePermissionsBtnCancel;
5418:             private final String microphonePermissionsBtnContinueMobile;
5419:             private final String microphonePermissionsPrompt;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5418`
```text
5416:             private final String disclosure;
5417:             private final String microphonePermissionsBtnCancel;
5418:             private final String microphonePermissionsBtnContinueMobile;
5419:             private final String microphonePermissionsPrompt;
5420:             private final String microphonePermissionsTitle;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5419`
```text
5417:             private final String microphonePermissionsBtnCancel;
5418:             private final String microphonePermissionsBtnContinueMobile;
5419:             private final String microphonePermissionsPrompt;
5420:             private final String microphonePermissionsTitle;
5421:             private final String navBarTitle;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5420`
```text
5418:             private final String microphonePermissionsBtnContinueMobile;
5419:             private final String microphonePermissionsPrompt;
5420:             private final String microphonePermissionsTitle;
5421:             private final String navBarTitle;
5422:             private final String prompt;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5459`
```text
5457:             }
5458: 
5459:             public final String getMicrophonePermissionsBtnCancel() {
5460:                 return this.microphonePermissionsBtnCancel;
5461:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5460`
```text
5458: 
5459:             public final String getMicrophonePermissionsBtnCancel() {
5460:                 return this.microphonePermissionsBtnCancel;
5461:             }
5462: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5463`
```text
5461:             }
5462: 
5463:             public final String getMicrophonePermissionsBtnContinueMobile() {
5464:                 return this.microphonePermissionsBtnContinueMobile;
5465:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5464`
```text
5462: 
5463:             public final String getMicrophonePermissionsBtnContinueMobile() {
5464:                 return this.microphonePermissionsBtnContinueMobile;
5465:             }
5466: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5467`
```text
5465:             }
5466: 
5467:             public final String getMicrophonePermissionsPrompt() {
5468:                 return this.microphonePermissionsPrompt;
5469:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5468`
```text
5466: 
5467:             public final String getMicrophonePermissionsPrompt() {
5468:                 return this.microphonePermissionsPrompt;
5469:             }
5470: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5471`
```text
5469:             }
5470: 
5471:             public final String getMicrophonePermissionsTitle() {
5472:                 return this.microphonePermissionsTitle;
5473:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5472`
```text
5470: 
5471:             public final String getMicrophonePermissionsTitle() {
5472:                 return this.microphonePermissionsTitle;
5473:             }
5474: 
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5502`
```text
5500:                 dest.writeString(this.cameraPermissionsAllowButtonText);
5501:                 dest.writeString(this.cameraPermissionsCancelButtonText);
5502:                 dest.writeString(this.microphonePermissionsBtnCancel);
5503:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
5504:                 dest.writeString(this.microphonePermissionsPrompt);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5503`
```text
5501:                 dest.writeString(this.cameraPermissionsCancelButtonText);
5502:                 dest.writeString(this.microphonePermissionsBtnCancel);
5503:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
5504:                 dest.writeString(this.microphonePermissionsPrompt);
5505:                 dest.writeString(this.microphonePermissionsTitle);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5504`
```text
5502:                 dest.writeString(this.microphonePermissionsBtnCancel);
5503:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
5504:                 dest.writeString(this.microphonePermissionsPrompt);
5505:                 dest.writeString(this.microphonePermissionsTitle);
5506:                 dest.writeString(this.navBarTitle);
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5505`
```text
5503:                 dest.writeString(this.microphonePermissionsBtnContinueMobile);
5504:                 dest.writeString(this.microphonePermissionsPrompt);
5505:                 dest.writeString(this.microphonePermissionsTitle);
5506:                 dest.writeString(this.navBarTitle);
5507:             }
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5532`
```text
5530:                 this.cameraPermissionsAllowButtonText = str8;
5531:                 this.cameraPermissionsCancelButtonText = str9;
5532:                 this.microphonePermissionsBtnCancel = str10;
5533:                 this.microphonePermissionsBtnContinueMobile = str11;
5534:                 this.microphonePermissionsPrompt = str12;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5533`
```text
5531:                 this.cameraPermissionsCancelButtonText = str9;
5532:                 this.microphonePermissionsBtnCancel = str10;
5533:                 this.microphonePermissionsBtnContinueMobile = str11;
5534:                 this.microphonePermissionsPrompt = str12;
5535:                 this.microphonePermissionsTitle = str13;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5534`
```text
5532:                 this.microphonePermissionsBtnCancel = str10;
5533:                 this.microphonePermissionsBtnContinueMobile = str11;
5534:                 this.microphonePermissionsPrompt = str12;
5535:                 this.microphonePermissionsTitle = str13;
5536:                 this.navBarTitle = str14;
```

### `sources/com/withpersona/sdk2/inquiry/network/dto/NextStep.java:5535`
```text
5533:                 this.microphonePermissionsBtnContinueMobile = str11;
5534:                 this.microphonePermissionsPrompt = str12;
5535:                 this.microphonePermissionsTitle = str13;
5536:                 this.navBarTitle = str14;
5537:             }
```

### `sources/com/withpersona/sdk2/inquiry/selfie/video_capture/VideoCaptureConfig.java:23`
```text
21: import kotlin.Metadata;
22: 
23: @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0006\b\u0087\b\u0018\u00002\u00020\u0001BA\u0012\b\b\u0002\u0010\u0003\u001a\u00020\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\u0004\u0012\n\b\u0001\u0010\n\u001a\u0004\u0018\u00010\t\u0012\u0006\
24: public final class VideoCaptureConfig implements Parcelable {
25:     public static final Parcelable.Creator<VideoCaptureConfig> CREATOR = new ojd0();
```

### `sources/com/withpersona/sdk2/inquiry/selfie/video_capture/VideoCaptureConfig.java:90`
```text
88:     }
89: 
90:     public final VideoCaptureConfig copy(long maxRecordingLengthMs, List<? extends NextStep.Selfie.CaptureFileType> enabledCaptureFileTypes, List<? extends rjd0> videoCaptureMethods, @egt(name = "webRTCJwt") String webRtcJwt, boolean recordAudio) {
91:         return new VideoCaptureConfig(maxRecordingLengthMs, enabledCaptureFileTypes, videoCaptureMethods, webRtcJwt, recordAudio);
92:     }
```

### `sources/com/withpersona/sdk2/inquiry/selfie/video_capture/VideoCaptureConfig.java:91`
```text
89: 
90:     public final VideoCaptureConfig copy(long maxRecordingLengthMs, List<? extends NextStep.Selfie.CaptureFileType> enabledCaptureFileTypes, List<? extends rjd0> videoCaptureMethods, @egt(name = "webRTCJwt") String webRtcJwt, boolean recordAudio) {
91:         return new VideoCaptureConfig(maxRecordingLengthMs, enabledCaptureFileTypes, videoCaptureMethods, webRtcJwt, recordAudio);
92:     }
93: 
```

### `sources/com/withpersona/sdk2/inquiry/selfie/video_capture/VideoCaptureConfig.java:117`
```text
115: 
116:     public final String toString() {
117:         return "VideoCaptureConfig(maxRecordingLengthMs=" + this.a + ", enabledCaptureFileTypes=" + this.b + ", videoCaptureMethods=" + this.c + ", webRtcJwt=" + this.d + ", recordAudio=" + this.e + ")";
118:     }
119: 
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:26`
```text
24: import kotlin.jvm.internal.DefaultConstructorMarker;
25: 
26: @Metadata(d1 = {"\u0000T\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010!\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010#\n\u0002\b\u0005\b\u0001\u0018\u0000 \u001f2\u00020\u0001:\u0002 \u001fB\t\b\u0007¢\u0006\u0004\b\u0002\u0010\u0003J \u0010\t\u
27: public final class TrackingEventsCache {
28: 
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:31`
```text
29:     public static final Companion INSTANCE = new Companion(null);
30:     private static volatile TrackingEventsCache INSTANCE;
31:     private final d2y mutex = new f2y();
32:     private final List<TrackingEventData> events = new ArrayList();
33:     private final Set<String> sessionTokensBeingFlushed = new LinkedHashSet();
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:144`
```text
142:         if (i2 == 0) {
143:             ct40.j(obj);
144:             d2y d2yVar2 = this.mutex;
145:             anonymousClass1.L$0 = str;
146:             anonymousClass1.L$1 = trackingEvent;
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:194`
```text
192:         if (i2 == 0) {
193:             ct40.j(obj);
194:             d2yVar = this.mutex;
195:             c00801.L$0 = str;
196:             c00801.L$1 = d2yVar;
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:250`
```text
248:         if (i2 == 0) {
249:             ct40.j(obj);
250:             d2y d2yVar2 = this.mutex;
251:             c00811.L$0 = d2yVar2;
252:             c00811.I$0 = 0;
```

### `sources/com/withpersona/sdk2/inquiry/tracking/TrackingEventsCache.java:293`
```text
291:         if (i2 == 0) {
292:             ct40.j(obj);
293:             d2yVar = this.mutex;
294:             c00821.L$0 = str;
295:             c00821.L$1 = d2yVar;
```

### `sources/defpackage/a31.java:90`
```text
88:                                 c31 c31Var = (c31) aVar.d.poll();
89:                                 if (c31Var != null) {
90:                                     numValueOf = Integer.valueOf((int) (SystemClock.elapsedRealtime() - c31Var.a));
91:                                     i2 = c31Var.b;
92:                                 } else {
```

### `sources/defpackage/a5e0.java:60`
```text
58:             return null;
59:         }
60:         long jElapsedRealtime = SystemClock.elapsedRealtime();
61:         ArrayBlockingQueue arrayBlockingQueue = new ArrayBlockingQueue(1);
62:         CancellationSignal cancellationSignal = new CancellationSignal();
```

### `sources/defpackage/a5e0.java:65`
```text
63:         try {
64:             DnsResolver.getInstance().query(null, str, 4 | (z ? 0 : 2), a, cancellationSignal, new z4e0(arrayBlockingQueue));
65:             long jElapsedRealtime2 = j - (SystemClock.elapsedRealtime() - jElapsedRealtime);
66:             if (jElapsedRealtime2 < 0) {
67:                 jElapsedRealtime2 = 0;
```

### `sources/defpackage/a5e0.java:66`
```text
64:             DnsResolver.getInstance().query(null, str, 4 | (z ? 0 : 2), a, cancellationSignal, new z4e0(arrayBlockingQueue));
65:             long jElapsedRealtime2 = j - (SystemClock.elapsedRealtime() - jElapsedRealtime);
66:             if (jElapsedRealtime2 < 0) {
67:                 jElapsedRealtime2 = 0;
68:             }
```

### `sources/defpackage/a5e0.java:67`
```text
65:             long jElapsedRealtime2 = j - (SystemClock.elapsedRealtime() - jElapsedRealtime);
66:             if (jElapsedRealtime2 < 0) {
67:                 jElapsedRealtime2 = 0;
68:             }
69:             try {
```

### `sources/defpackage/a5e0.java:70`
```text
68:             }
69:             try {
70:                 return new zu0((cv0) arrayBlockingQueue.poll(jElapsedRealtime2, TimeUnit.MILLISECONDS), SystemClock.elapsedRealtime() - jElapsedRealtime);
71:             } catch (InterruptedException unused) {
72:                 Thread.currentThread().interrupt();
```

### `sources/defpackage/a5e0.java:77`
```text
75:             }
76:         } catch (Exception e) {
77:             return new zu0(new bv0(null, a(e), e), SystemClock.elapsedRealtime() - jElapsedRealtime);
78:         }
79:     }
```

### `sources/defpackage/abc.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("failureReason", true);
21:         pluginGeneratedSerialDescriptor.k("unsupportedCodexVersion", true);
22:         pluginGeneratedSerialDescriptor.k("supportsRealtimeConversation", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
24:     }
```

### `sources/defpackage/afl.java:35`
```text
33:         pluginGeneratedSerialDescriptor.k("showAssistantAudioDuckingFeedback", true);
34:         pluginGeneratedSerialDescriptor.k("showWingmanDebugOverlay", true);
35:         pluginGeneratedSerialDescriptor.k("showWingmanMuteButton", true);
36:         pluginGeneratedSerialDescriptor.k("showLocalVadInUi", true);
37:         pluginGeneratedSerialDescriptor.k("forceVoiceDisclosureOnVoiceStartup", true);
```

### `sources/defpackage/aqi.java:178`
```text
176:     public static long m(long j) {
177:         Trace.endSection();
178:         return SystemClock.elapsedRealtimeNanos() - j;
179:     }
180: 
```

### `sources/defpackage/asa.java:5`
```text
3: import kotlinx.serialization.descriptors.SerialDescriptor;
4: import kotlinx.serialization.encoding.Encoder;
5: import protobuf_analytics_events.v1.ChatgptVoiceMicrophoneState;
6: 
7: public final class asa implements ki60 {
```

### `sources/defpackage/asa.java:19`
```text
17:     public final void serialize(Encoder encoder, Object obj) {
18:         String str;
19:         int i = zra.a[((ChatgptVoiceMicrophoneState) obj).ordinal()];
20:         if (i == 1) {
21:             str = "CHATGPT_VOICE_MICROPHONE_STATE_UNSPECIFIED";
```

### `sources/defpackage/asa.java:21`
```text
19:         int i = zra.a[((ChatgptVoiceMicrophoneState) obj).ordinal()];
20:         if (i == 1) {
21:             str = "CHATGPT_VOICE_MICROPHONE_STATE_UNSPECIFIED";
22:         } else if (i == 2) {
23:             str = "CHATGPT_VOICE_MICROPHONE_STATE_MUTED";
```

### `sources/defpackage/asa.java:23`
```text
21:             str = "CHATGPT_VOICE_MICROPHONE_STATE_UNSPECIFIED";
22:         } else if (i == 2) {
23:             str = "CHATGPT_VOICE_MICROPHONE_STATE_MUTED";
24:         } else {
25:             if (i != 3) {
```

### `sources/defpackage/asa.java:29`
```text
27:                 return;
28:             }
29:             str = "CHATGPT_VOICE_MICROPHONE_STATE_UNMUTED";
30:         }
31:         encoder.G(str);
```

### `sources/defpackage/au10.java:64`
```text
62: 
63:     public final au10 a() {
64:         return new au10(this.a, this.b, this.c, this.d, this.e, this.f, this.g, this.h, this.i, this.j, this.k, this.l, this.m, this.n, this.o, this.q, this.r, l(), SystemClock.elapsedRealtime(), this.p);
65:     }
66: 
```

### `sources/defpackage/au10.java:76`
```text
74: 
75:     public final au10 d(n8w n8wVar, long j, long j2, long j3, long j4, vdb0 vdb0Var, deb0 deb0Var, List list) {
76:         return new au10(this.a, n8wVar, j2, j3, this.e, this.f, this.g, vdb0Var, deb0Var, list, this.k, this.l, this.m, this.n, this.o, this.q, j4, j, SystemClock.elapsedRealtime(), this.p);
77:     }
78: 
```

### `sources/defpackage/au10.java:113`
```text
111:             j2 = this.s;
112:         } while (j != this.t);
113:         return q0d0.H(q0d0.R(j2) + ((long) ((SystemClock.elapsedRealtime() - j) * this.o.a)));
114:     }
115: 
```

### `sources/defpackage/aw.java:7`
```text
5: 
6: public final class aw extends wsp implements Function0 {
7:     public static final aw b = new aw(0, SystemClock.class, "elapsedRealtime", "elapsedRealtime()J", 0);
8: 
9:     @Override
```

### `sources/defpackage/aw.java:11`
```text
9:     @Override
10:     public final Object invoke() {
11:         return Long.valueOf(SystemClock.elapsedRealtime());
12:     }
13: }
```

### `sources/defpackage/b53.java:44`
```text
42:         pluginGeneratedSerialDescriptor.k("voiceMainLanguage", true);
43:         pluginGeneratedSerialDescriptor.k("voiceBackgroundEnabled", true);
44:         pluginGeneratedSerialDescriptor.k("voice_mode", true);
45:         pluginGeneratedSerialDescriptor.k("voice_mode_rollout_version", true);
46:         pluginGeneratedSerialDescriptor.k("wingman_thinking_effort", true);
```

### `sources/defpackage/b53.java:45`
```text
43:         pluginGeneratedSerialDescriptor.k("voiceBackgroundEnabled", true);
44:         pluginGeneratedSerialDescriptor.k("voice_mode", true);
45:         pluginGeneratedSerialDescriptor.k("voice_mode_rollout_version", true);
46:         pluginGeneratedSerialDescriptor.k("wingman_thinking_effort", true);
47:         pluginGeneratedSerialDescriptor.k("preferredWeatherUnit", false);
```

### `sources/defpackage/bai0.java:12`
```text
10: 
11:     public bai0() {
12:         SystemClock.elapsedRealtime();
13:         Duration.ofMillis(SystemClock.uptimeMillis()).toMillis();
14:     }
```

### `sources/defpackage/bhe0.java:73`
```text
71:         }
72:         try {
73:             iArr5[i8b0.Mute.ordinal()] = 2;
74:         } catch (NoSuchFieldError unused16) {
75:         }
```

### `sources/defpackage/bq80.java:3`
```text
1: package defpackage;
2: 
3: import com.openai.feature.conversation.common.speech.SpeechPlaybackFailure;
4: import java.util.LinkedHashMap;
5: import java.util.LinkedHashSet;
```

### `sources/defpackage/bq80.java:29`
```text
27:     }
28: 
29:     public final Object a(Object obj, Object obj2, SpeechPlaybackFailure speechPlaybackFailure, dq80 dq80Var, cq80 cq80Var, rsg rsgVar) {
30:         this.g.remove(obj2);
31:         this.j = null;
```

### `sources/defpackage/bq80.java:39`
```text
37:         }
38:         this.e.invoke(obj, eq80.a);
39:         cq80Var.d.invoke(speechPlaybackFailure, dq80Var);
40:         return this.c.b(rsgVar);
41:     }
```

### `sources/defpackage/bq80.java:176`
```text
174:             rxb0 rxb0Var = (rxb0) yxb0Var;
175:             if (bq80Var.b(obj5, dq80Var2)) {
176:                 SpeechPlaybackFailure speechPlaybackFailureV = i780.v(4, rxb0Var);
177:                 yp80Var2.n = null;
178:                 yp80Var2.o = null;
```

### `sources/defpackage/bq80.java:182`
```text
180:                 yp80Var2.q = null;
181:                 yp80Var2.t = 2;
182:                 if (bq80Var.a(obj5, obj3, speechPlaybackFailureV, dq80Var2, cq80Var2, yp80Var2) == wqiVar) {
183:                     return wqiVar;
184:                 }
```

### `sources/defpackage/bsa.java:3`
```text
1: package defpackage;
2: 
3: import protobuf_analytics_events.v1.ChatgptVoiceMode;
4: 
5: public abstract class bsa {
```

### `sources/defpackage/bsa.java:9`
```text
7: 
8:     static {
9:         int[] iArr = new int[ChatgptVoiceMode.values().length];
10:         try {
11:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_UNSPECIFIED.ordinal()] = 1;
```

### `sources/defpackage/bsa.java:11`
```text
9:         int[] iArr = new int[ChatgptVoiceMode.values().length];
10:         try {
11:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_UNSPECIFIED.ordinal()] = 1;
12:         } catch (NoSuchFieldError unused) {
13:         }
```

### `sources/defpackage/bsa.java:15`
```text
13:         }
14:         try {
15:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_UNKNOWN.ordinal()] = 2;
16:         } catch (NoSuchFieldError unused2) {
17:         }
```

### `sources/defpackage/bsa.java:19`
```text
17:         }
18:         try {
19:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_ADVANCED.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
```

### `sources/defpackage/bsa.java:23`
```text
21:         }
22:         try {
23:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_STANDARD.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
```

### `sources/defpackage/bsa.java:27`
```text
25:         }
26:         try {
27:             iArr[ChatgptVoiceMode.CHATGPT_VOICE_MODE_WINGMAN.ordinal()] = 5;
28:         } catch (NoSuchFieldError unused5) {
29:         }
```

### `sources/defpackage/bzj.java:427`
```text
425:         }
426:         azj azjVar = this.l;
427:         if (((Exception) azjVar.c) != null && (c0.get() > 0 || SystemClock.elapsedRealtime() < azjVar.b)) {
428:             return;
429:         }
```

### `sources/defpackage/bzj.java:434`
```text
432:         try {
433:             boolean zG = this.t.g(this.J, j, this.K);
434:             this.W = SystemClock.elapsedRealtime();
435:             azjVar.c = null;
436:             azjVar.a = -9223372036854775807L;
```

### `sources/defpackage/bzj.java:646`
```text
644:         ynv ynvVar;
645:         azj azjVar = this.k;
646:         if (((Exception) azjVar.c) != null && (c0.get() > 0 || SystemClock.elapsedRealtime() < azjVar.b)) {
647:             return false;
648:         }
```

### `sources/defpackage/bzj.java:708`
```text
706:         }
707:         this.F = true;
708:         int audioSessionId = this.t.a.getAudioSessionId();
709:         boolean z = audioSessionId != this.Q;
710:         this.Q = audioSessionId;
```

### `sources/defpackage/bzj.java:709`
```text
707:         this.F = true;
708:         int audioSessionId = this.t.a.getAudioSessionId();
709:         boolean z = audioSessionId != this.Q;
710:         this.Q = audioSessionId;
711:         zxt zxtVar = this.n;
```

### `sources/defpackage/bzj.java:710`
```text
708:         int audioSessionId = this.t.a.getAudioSessionId();
709:         boolean z = audioSessionId != this.Q;
710:         this.Q = audioSessionId;
711:         zxt zxtVar = this.n;
712:         if (zxtVar != null) {
```

### `sources/defpackage/bzj.java:759`
```text
757:             if (oo4Var.u != -9223372036854775807L) {
758:                 oo4Var.b.getClass();
759:                 oo4Var.u = q0d0.H(SystemClock.elapsedRealtime());
760:             }
761:             oo4Var.j = q0d0.L(oo4Var.e, oo4Var.a());
```

### `sources/defpackage/bzj.java:786`
```text
784:         oo4Var.w = oo4Var.a();
785:         oo4Var.b.getClass();
786:         oo4Var.u = q0d0.H(SystemClock.elapsedRealtime());
787:         oo4Var.x = jB;
788:         mo4Var.a.stop();
```

### `sources/defpackage/c2i.java:17`
```text
15:         int i = ConversationScreenAccessibilityService.d;
16:         try {
17:             return conversationScreenAccessibilityService.c(SystemClock.elapsedRealtime(), h2iVar);
18:         } catch (RuntimeException e) {
19:             gev.f(conversationScreenAccessibilityService.b, "Unable to capture accessibility screen context", e, null, 12);
```

### `sources/defpackage/c6w.java:22`
```text
20:             Handler handler = (Handler) wj00Var.b;
21:             if (handler != null) {
22:                 handler.post(new sy4((Object) wj00Var, (Object) surface, SystemClock.elapsedRealtime(), (byte) 4));
23:             }
24:             g6wVar.k2 = true;
```

### `sources/defpackage/ckf.java:34`
```text
32:             }
33:             this.a.getClass();
34:             long jElapsedRealtime = SystemClock.elapsedRealtime();
35:             long j2 = j + jElapsedRealtime;
36:             if (j2 < jElapsedRealtime) {
```

### `sources/defpackage/ckf.java:35`
```text
33:             this.a.getClass();
34:             long jElapsedRealtime = SystemClock.elapsedRealtime();
35:             long j2 = j + jElapsedRealtime;
36:             if (j2 < jElapsedRealtime) {
37:                 a();
```

### `sources/defpackage/ckf.java:36`
```text
34:             long jElapsedRealtime = SystemClock.elapsedRealtime();
35:             long j2 = j + jElapsedRealtime;
36:             if (j2 < jElapsedRealtime) {
37:                 a();
38:             } else {
```

### `sources/defpackage/ckf.java:40`
```text
38:             } else {
39:                 boolean z = false;
40:                 while (!this.b && jElapsedRealtime < j2) {
41:                     try {
42:                         this.a.getClass();
```

### `sources/defpackage/ckf.java:43`
```text
41:                     try {
42:                         this.a.getClass();
43:                         wait(j2 - jElapsedRealtime);
44:                     } catch (InterruptedException unused) {
45:                         z = true;
```

_Hits captured: 180 (cap 180)_

## CONVERSATION_ACTIONS

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'messageId':s,'conversationId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'messageId':s,'conversationId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
10:     private String _conversationId;
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
10:     private String _conversationId;
11:     private String _messageId;
12: 
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:15`
```text
13:     public FinanceTransactionsRequestContext(String str) {
14:         this._messageId = str;
15:         this._conversationId = null;
16:     }
17: 
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:20`
```text
18:     public FinanceTransactionsRequestContext(String str, String str2) {
19:         this._messageId = str;
20:         this._conversationId = str2;
21:     }
22: }
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?,'turnOrdinal':d@?,'contentReferenceStartIndex':d@?,'isModelWrittenDil':b,'isReadOnly':b@?,'widgetType':s?,'widgetName':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0014\b\u0007\u0018\u00002\u00020\u0001Bq\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\b\u001a\u0004\u0018\u0001
9: public final class DILMessageMetadata extends b {
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?,'turnOrdinal':d@?,'contentReferenceStartIndex':d@?,'isModelWrittenDil':b,'isReadOnly':b@?,'widgetType':s?,'widgetName':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0014\b\u0007\u0018\u00002\u00020\u0001Bq\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\b\u001a\u0004\u0018\u0001
9: public final class DILMessageMetadata extends b {
10:     private Double _contentReferenceIndex;
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:12`
```text
10:     private Double _contentReferenceIndex;
11:     private Double _contentReferenceStartIndex;
12:     private String _conversationId;
13:     private boolean _isModelWrittenDil;
14:     private Boolean _isReadOnly;
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:21`
```text
19: 
20:     public DILMessageMetadata(String str, String str2, Double d, Double d2, Double d3, boolean z, Boolean bool, String str3, String str4) {
21:         this._conversationId = str;
22:         this._messageId = str2;
23:         this._contentReferenceIndex = d;
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @o2d0(propertyReplacements = "", schema = "'accountId':s,'accessToken':s,'baseUrl':s,'conversationId':s?,'parentMessageId':s", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u000e\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002¢\u0006\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\u0
8: public final class DeviceIntegrityRequest extends com.snap.valdi.utils.b {
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:7`
```text
5: 
6: @o2d0(propertyReplacements = "", schema = "'accountId':s,'accessToken':s,'baseUrl':s,'conversationId':s?,'parentMessageId':s", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u000e\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002¢\u0006\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\u0
8: public final class DeviceIntegrityRequest extends com.snap.valdi.utils.b {
9:     private String _accessToken;
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:12`
```text
10:     private String _accountId;
11:     private String _baseUrl;
12:     private String _conversationId;
13:     private String _parentMessageId;
14: 
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:19`
```text
17:         this._accessToken = str2;
18:         this._baseUrl = str3;
19:         this._conversationId = str4;
20:         this._parentMessageId = str5;
21:     }
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:35`
```text
33:     }
34: 
35:     public final String get_conversationId() {
36:         return this._conversationId;
37:     }
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:36`
```text
34: 
35:     public final String get_conversationId() {
36:         return this._conversationId;
37:     }
38: 
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:190`
```text
188:         if (i3 == 0) {
189:             ct40.j(objB);
190:             String strA2 = getInputData().a("conversation_id");
191:             if (strA2 == null) {
192:                 return new yyu();
```

### `sources/defpackage/a300.java:20`
```text
18:         a = a300Var;
19:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("X0_gf-W53LWIM8rFdjb1wYY4iDmjygcA6GolQZQJt1o=", a300Var, 10);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("userPromptMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("displayedMessageIds", false);
```

### `sources/defpackage/ap80.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("spawnId", false);
20:         pluginGeneratedSerialDescriptor.k("text", true);
21:         pluginGeneratedSerialDescriptor.k("delegateConversationId", true);
22:         pluginGeneratedSerialDescriptor.k("metadata", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ar2.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("saveId", true);
18:         pluginGeneratedSerialDescriptor.k("projectId", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationTitle", true);
21:         pluginGeneratedSerialDescriptor.k("title", true);
```

### `sources/defpackage/av1.java:23`
```text
21:         pluginGeneratedSerialDescriptor.k("instruction", false);
22:         pluginGeneratedSerialDescriptor.k("numVariations", true);
23:         pluginGeneratedSerialDescriptor.k("conversationId", false);
24:         pluginGeneratedSerialDescriptor.k("mode", true);
25:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ayy.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("OmZev71Y156-8Lp3Bp-DY_oGdf_tcScWr8A2H_Fl1gY=", ayyVar, 4);
18:         pluginGeneratedSerialDescriptor.k("type", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("imageFileId", true);
21:         pluginGeneratedSerialDescriptor.k("actions", false);
```

### `sources/defpackage/b1i.java:18`
```text
16:         a = b1iVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("ml0VAl8FtX41xNs-nAcNn3TXL4a_fasVVnef-ip6xdA=", b1iVar, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("token", false);
20:         pluginGeneratedSerialDescriptor.k("parentMessageId", false);
```

### `sources/defpackage/ba70.java:5`
```text
3: public enum ba70 {
4:     Post("post"),
5:     SharedConversation("shared_conversation");
6: 
7:     public final String a;
```

### `sources/defpackage/bc80.java:33`
```text
31:         pluginGeneratedSerialDescriptor.k("userId", true);
32:         pluginGeneratedSerialDescriptor.k("accountId", true);
33:         pluginGeneratedSerialDescriptor.k("conversationId", true);
34:         pluginGeneratedSerialDescriptor.k("isSharedConversation", true);
35:         pluginGeneratedSerialDescriptor.k("original_message_id", true);
```

### `sources/defpackage/bc80.java:34`
```text
32:         pluginGeneratedSerialDescriptor.k("accountId", true);
33:         pluginGeneratedSerialDescriptor.k("conversationId", true);
34:         pluginGeneratedSerialDescriptor.k("isSharedConversation", true);
35:         pluginGeneratedSerialDescriptor.k("original_message_id", true);
36:         pluginGeneratedSerialDescriptor.k("appPackageName", true);
```

### `sources/defpackage/bh50.java:17`
```text
15:         a = bh50Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("3BJgFpD7vT27iKkDRs2EDx9O7VKUihnwurcEJcOWB2g=", bh50Var, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/bqk.java:71`
```text
69:             case 11:
70:                 super(mwjVar2);
71:                 this.e = Collections.singletonList("s/c_{conversationId}");
72:                 this.f = Collections.singletonList("s/c_sample-shared-conversation-id");
73:                 break;
```

### `sources/defpackage/bs20.java:19`
```text
17:         a = bs20Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("VY8aRV82L6lNZ5jDkd37OyLd-QtBGRs2daJ8lyhMqYY=", bs20Var, 6);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("supportedEncodings", true);
```

### `sources/defpackage/bs6.java:18`
```text
16:         a = bs6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("GHhDRE8Va8_Y_YothYADtLEluA_tAVnF2_AQcn-bX7o=", bs6Var, 4);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("challengeId", false);
20:         pluginGeneratedSerialDescriptor.k("selectedOption", true);
```

### `sources/defpackage/btg.java:28`
```text
26:         pluginGeneratedSerialDescriptor.k("moderationResults", true);
27:         pluginGeneratedSerialDescriptor.k("safeUrlMap", true);
28:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
29:         pluginGeneratedSerialDescriptor.k("defaultModelSlug", true);
30:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
```

### `sources/defpackage/bx2.java:17`
```text
15:         a = bx2Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("HhZ9kaHD6KMeWrvaLww8EzXdD722nnSVXfMzAHzWF7c=", bx2Var, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/cdi.java:18`
```text
16:         a = cdiVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("od7nq0-KubJImC08uRSeG8iE3oCQxyYXCMP92pxAjXo=", cdiVar, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("turnExchangeId", false);
20:         pluginGeneratedSerialDescriptor.k("options", true);
```

### `sources/defpackage/cjx.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("X0FymQwhYMehsMeKDIwRmnj4-5AZS3M2iCZe-StpYhM=", cjxVar, 5);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("feedback", false);
21:         pluginGeneratedSerialDescriptor.k("checkedReasons", true);
```

### `sources/defpackage/ck6.java:18`
```text
16:         a = ck6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("yh6ic6Q5rfOe5DDIRCoeg9IHs3MLxUXv6Ft6aT8clts=", ck6Var, 9);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("rating", true);
```

### `sources/defpackage/crk.java:17`
```text
15:         a = crkVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("JpL5cmQFiuYOA3ypncFb-UwfEP7qWa9cNeM8LQw62W4=", crkVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("remainingAttachmentSlots", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/czk.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("allowLibraryDelete", true);
20:         pluginGeneratedSerialDescriptor.k("allowFileExport", true);
21:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
23:     }
```

### `sources/defpackage/d63.java:17`
```text
15:         a = d63Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("reY0PReImFGQSIO-JHYtc7XophsR2t1KTrasmbiw__M=", d63Var, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/dh40.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("contentId", false);
18:         pluginGeneratedSerialDescriptor.k("productArea", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("userMessageId", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dk2.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("xZGh3OKrPqPJdbkDaGZYwXghYFDA3Fv6WRZXnPyoaAg=", dk2Var, 3);
18:         pluginGeneratedSerialDescriptor.k("kind", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageIds", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dm9.java:10`
```text
8: import kotlin.jvm.functions.Function2;
9: 
10: @o2d0(propertyReplacements = "", schema = "'navigator':r:'[0]','openConversation':f?(s),'platformServices':r:'[1]','trackEvent':f?(s, s)", typeReferences = {INavigator.class, OAIPlatformServices.class})
11: @Metadata(d1 = {"\u0000*\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001BO\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0016\b\u0002\u0010\u0007\u001a\u0010\u0012\u0004\u0012\u00020\u0005\u0012\u0004\u0012\u00020\u0006\u0018\u00010\u0004\u0012\u0006\u0010\t\u001a\u00020\b\u0012\u001c\b\u0002\u0010\u000b\
12: public final class dm9 extends b {
```

### `sources/defpackage/dm9.java:11`
```text
9: 
10: @o2d0(propertyReplacements = "", schema = "'navigator':r:'[0]','openConversation':f?(s),'platformServices':r:'[1]','trackEvent':f?(s, s)", typeReferences = {INavigator.class, OAIPlatformServices.class})
11: @Metadata(d1 = {"\u0000*\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001BO\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0016\b\u0002\u0010\u0007\u001a\u0010\u0012\u0004\u0012\u00020\u0005\u0012\u0004\u0012\u00020\u0006\u0018\u00010\u0004\u0012\u0006\u0010\t\u001a\u00020\b\u0012\u001c\b\u0002\u0010\u000b\
12: public final class dm9 extends b {
13:     private INavigator _navigator;
```

### `sources/defpackage/dm9.java:14`
```text
12: public final class dm9 extends b {
13:     private INavigator _navigator;
14:     private Function1 _openConversation;
15:     private OAIPlatformServices _platformServices;
16:     private Function2 _trackEvent;
```

### `sources/defpackage/dm9.java:20`
```text
18:     public dm9(INavigator iNavigator, Function1 function1, OAIPlatformServices oAIPlatformServices, Function2 function2) {
19:         this._navigator = iNavigator;
20:         this._openConversation = function1;
21:         this._platformServices = oAIPlatformServices;
22:         this._trackEvent = function2;
```

### `sources/defpackage/dn5.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("correction", false);
20:         pluginGeneratedSerialDescriptor.k("targetAction", false);
21:         pluginGeneratedSerialDescriptor.k("conversationId", false);
22:         pluginGeneratedSerialDescriptor.k("contextualHintSource", false);
23:         pluginGeneratedSerialDescriptor.k("cachedGeneratedAtIso", false);
```

### `sources/defpackage/duw.java:18`
```text
16:         a = duwVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("d1vqAOst3f2MX_Xf2thiN5-vVcznFFXA_eY9bn8yOPQ=", duwVar, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("rating", false);
```

### `sources/defpackage/dv2.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("aZ_EqRTZPhz0lVm463cdfqK1463K5OwyKxo_n3Znh4g=", dv2Var, 3);
18:         pluginGeneratedSerialDescriptor.k("kind", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageIds", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dvt.java:160`
```text
158:                                     if (((Boolean) dzn.p(dznVar, fmi.Z0, false, null, 14)).booleanValue()) {
159:                                         int iB = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
160:                                         gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB))), 10);
161:                                         this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB), null, 4, null));
162:                                         ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:167`
```text
165:                                 } else {
166:                                     int iB2 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
167:                                     gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB2))), 10);
168:                                     this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB2), null, 4, null));
169:                                     ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:251`
```text
249:                                         if (((Boolean) dzn.p(dznVar, fmi.Z0, false, null, 14)).booleanValue()) {
250:                                             int iB3 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
251:                                             gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB3))), 10);
252:                                             this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB3), null, 4, null));
253:                                             ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:258`
```text
256:                                     } else {
257:                                         int iB4 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
258:                                         gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB4))), 10);
259:                                         this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB4), null, 4, null));
260:                                         ((mk3) this.g).f(str, false);
```

### `sources/defpackage/e1i.java:17`
```text
15:         a = e1iVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("5kN3qJBQ0HzIX-wny6ClEEuY_3rPFeTgtsdZgA8rtbk=", e1iVar, 3);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("model", false);
19:         pluginGeneratedSerialDescriptor.k("offset", true);
```

### `sources/defpackage/e7t.java:9`
```text
7: 
8:     static {
9:         e7t e7tVar = new e7t("ShareConversation", 0);
10:         a = e7tVar;
11:         e7t e7tVar2 = new e7t("DoNotShareConversation", 1);
```

### `sources/defpackage/e7t.java:11`
```text
9:         e7t e7tVar = new e7t("ShareConversation", 0);
10:         a = e7tVar;
11:         e7t e7tVar2 = new e7t("DoNotShareConversation", 1);
12:         b = e7tVar2;
13:         c = new e7t[]{e7tVar, e7tVar2};
```

### `sources/defpackage/e8u.java:31`
```text
29:         pluginGeneratedSerialDescriptor.k("userId", true);
30:         pluginGeneratedSerialDescriptor.k("accountId", true);
31:         pluginGeneratedSerialDescriptor.k("conversationId", true);
32:         pluginGeneratedSerialDescriptor.k("originalMessageId", false);
33:         pluginGeneratedSerialDescriptor.k("messages", true);
```

### `sources/defpackage/e9.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("status", false);
19:         pluginGeneratedSerialDescriptor.k("handoffId", false);
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
```

### `sources/defpackage/e9.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
23:         pluginGeneratedSerialDescriptor.k("destinationUserMessageId", false);
24:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/edc0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("xmZhMBoKPT6JLy3kQ-8oAvquiD_1oQYl5MI5iliJ-Ac=", edc0Var, 2);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
20:     }
```

### `sources/defpackage/edq.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("title", false);
21:         pluginGeneratedSerialDescriptor.k("snippet", false);
22:         pluginGeneratedSerialDescriptor.k("conversationId", false);
23:         pluginGeneratedSerialDescriptor.k("messageId", false);
24:         pluginGeneratedSerialDescriptor.k("isArchived", false);
```

### `sources/defpackage/em9.java:8`
```text
6: import kotlin.Metadata;
7: 
8: @o2d0(propertyReplacements = "", schema = "'navigator':r:'[0]','openConversation':f?(s),'platformServices':r:'[1]','trackEvent':f?(s, s)", typeReferences = {INavigator.class, OAIPlatformServices.class})
9: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\t\b\u0017¢\u0006\u0004\b\u0002\u0010\u0003¨\u0006\u0004"}, d2 = {"Lem9;", "Lcom/snap/valdi/utils/b;", "<init>", "()V", "modules_chatgpt_library-chatgpt_library_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
10: public final class em9 extends b {
```

### `sources/defpackage/ep6.java:18`
```text
16:         a = ep6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("dC1TGvyVE4mVOhxGv-Ay9aFewKUBI3Six72HPXOc1RY=", ep6Var, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("products", false);
```

### `sources/defpackage/eq20.java:18`
```text
16:         a = eq20Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("R0kus8NLdn-rQ5FWLO4hMPKsJefJMgjBoDjKRiwh4gs=", eq20Var, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("productQuery", false);
```

### `sources/defpackage/es20.java:19`
```text
17:         a = es20Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("TJGWkVNMjpkJRxoHV3JAxZ3g6osbD1s7LXEOAAsx4Ew=", es20Var, 6);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("supportedEncodings", true);
```

### `sources/defpackage/etg.java:18`
```text
16:         a = etgVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("orqmOZs-C-1F1zdO-PvZUCzK7iq4swHz7fFIBRvUjDI=", etgVar, 4);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("parentSnapshot", true);
```

### `sources/defpackage/evt.java:17`
```text
15:         a = evtVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("btBiFrvPkO1DFG9HWim_O9VYkuTw1RoEuKjLbx4lm3U=", evtVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("type", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ez60.java:24`
```text
22:         this.W0 = d470Var;
23:         this.X0 = q8iVar;
24:         this.Y0 = wnm.F(6, "SharedConversationViewModel");
25:         psg psgVar = null;
26:         w(d470Var, new el60((Object) this, (byte) 2), null);
```

### `sources/defpackage/ez60.java:163`
```text
161:             }
162:             rxb0 rxb0Var = (rxb0) yxb0Var;
163:             gev.f(this.Y0, "Failed to delete conversation", rxb0Var.b, null, 12);
164:             m(new ww80(rxb0Var, null, null, null, 126));
165:         }
```

### `sources/defpackage/f53.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("7CbcfmK_DHcbhJX6su6kQZfUhLwnoJpfZFP2Pwzl8ZE=", f53Var, 4);
17:         pluginGeneratedSerialDescriptor.k("kind", true);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("contentReferenceIndex", false);
```

### `sources/defpackage/fda.java:132`
```text
130:                 s3b s3bVar7 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesNextAssistantTurnButtonClicked");
131:                 sj20 sj20Var4 = da90.b;
132:                 s3bVar7.a("conversationId", sj20Var4, (12 & 8) == 0);
133:                 s3bVar7.a("fullscreenSessionId", sj20Var4, (12 & 8) == 0);
134:                 s3bVar7.a("messageId", sj20Var4, (12 & 8) == 0);
```

### `sources/defpackage/fda.java:144`
```text
142:                 s3b s3bVar8 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesPreviousAssistantTurnButtonClicked");
143:                 sj20 sj20Var5 = da90.b;
144:                 s3bVar8.a("conversationId", sj20Var5, (12 & 8) == 0);
145:                 s3bVar8.a("fullscreenSessionId", sj20Var5, (12 & 8) == 0);
146:                 s3bVar8.a("messageId", sj20Var5, (12 & 8) == 0);
```

### `sources/defpackage/fda.java:156`
```text
154:                 s3b s3bVar9 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesSearchHereButtonClicked");
155:                 sj20 sj20Var6 = da90.b;
156:                 s3bVar9.a("conversationId", sj20Var6, (12 & 8) == 0);
157:                 s3bVar9.a("fullscreenSessionId", sj20Var6, (12 & 8) == 0);
158:                 s3bVar9.a("messageId", sj20Var6, (12 & 8) == 0);
```

### `sources/defpackage/fei.java:18`
```text
16:         a = feiVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("BXFWgCbyfBzMa7ZfbGE5SPaWKIHlyKYIcGLFJ0bBnJw=", feiVar, 2);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("metadata", false);
20:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/fga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesNextAssistantTurnButtonClicked chatgptPlacesNextAssistantTurnButtonClicked = (ChatgptPlacesNextAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/fga.java:15`
```text
13:         ChatgptPlacesNextAssistantTurnButtonClicked chatgptPlacesNextAssistantTurnButtonClicked = (ChatgptPlacesNextAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesNextAssistantTurnButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/fha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductGroupClickedEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductGroupClickedEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupClickedEvent.getConversation_id());
22:         }
```

### `sources/defpackage/fha.java:21`
```text
19:         }
20:         if (chatgptProductGroupClickedEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupClickedEvent.getConversation_id());
22:         }
23:         if (chatgptProductGroupClickedEvent.getMessage_id() != null) {
```

### `sources/defpackage/fi40.java:20`
```text
18:         fi40 fi40Var = new fi40("Conversation", 0);
19:         a = fi40Var;
20:         fi40 fi40Var2 = new fi40("SharedConversation", 1);
21:         b = fi40Var2;
22:         fi40 fi40Var3 = new fi40("CalpicoRoom", 2);
```

### `sources/defpackage/fqk.java:23`
```text
21:         pluginGeneratedSerialDescriptor.l(new k3l());
22:         pluginGeneratedSerialDescriptor.k("allowLibraryDelete", true);
23:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
24:         descriptor = pluginGeneratedSerialDescriptor;
25:     }
```

### `sources/defpackage/frt.java:20`
```text
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("OiPgJ0kykXun48pr7VgqwTYZU73cU4_My6qlPFGjpxQ=", frtVar, 10);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("intent", false);
22:         pluginGeneratedSerialDescriptor.k("contentTextLength", false);
```

### `sources/defpackage/fvw.java:35`
```text
33: 
34:     public final Object a(String str, String str2, String str3, rsg rsgVar) {
35:         return f(dvv.D0(new g100("conversationId", str), new g100("messageId", str2)), new bvw(this, str, str2, str3, null, (byte) 0), rsgVar);
36:     }
37: 
```

### `sources/defpackage/fvw.java:81`
```text
79: 
80:     public final Object c(String str, String str2, String str3, rsg rsgVar) {
81:         return f(dvv.D0(new g100("sharedConversationId", str), new g100("messageId", str2)), new bvw(this, str, str2, str3, null, (byte) 1), rsgVar);
82:     }
83: 
```

### `sources/defpackage/g310.java:18`
```text
16:         a = g310Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Gq7RMTAf_AsRCLj0rT9b_g891O5i_e_X5urlzZYNzI0=", g310Var, 1);
18:         pluginGeneratedSerialDescriptor.k("recordsByConversationId", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
20:     }
```

### `sources/defpackage/ga5.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("id", false);
20:         pluginGeneratedSerialDescriptor.k("updatedAt", true);
21:         pluginGeneratedSerialDescriptor.k("conversationId", true);
22:         pluginGeneratedSerialDescriptor.k("sourceConversationIsWorkMode", true);
23:         pluginGeneratedSerialDescriptor.k("title", false);
```

### `sources/defpackage/gcu.java:17`
```text
15:         a = gcuVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("SahdpmD8LEk9GTF9L2hH5XKkC8uhaugQXfI588se-ng=", gcuVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/gga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesPreviousAssistantTurnButtonClicked chatgptPlacesPreviousAssistantTurnButtonClicked = (ChatgptPlacesPreviousAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/gga.java:15`
```text
13:         ChatgptPlacesPreviousAssistantTurnButtonClicked chatgptPlacesPreviousAssistantTurnButtonClicked = (ChatgptPlacesPreviousAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/gha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductGroupShownEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductGroupShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupShownEvent.getConversation_id());
22:         }
```

### `sources/defpackage/gha.java:21`
```text
19:         }
20:         if (chatgptProductGroupShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupShownEvent.getConversation_id());
22:         }
23:         if (chatgptProductGroupShownEvent.getMessage_id() != null) {
```

### `sources/defpackage/go0.java:20`
```text
18:     public static final go0 r = new go0("Dil Widget Retry", 13);
19:     public static final go0 s = new go0("Dil Widget WebView Ready Latency", 14);
20:     public static final go0 t = new go0("Edit Message", 15);
21:     public static final go0 u = new go0("Error Banner Shown", 16);
22:     public static final go0 v = new go0("Generate Completion", 17);
```

### `sources/defpackage/go1.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("2Smk92UHZvzQ9Wvfuj2A4PjO7YMJD8wn0gYorEhxjYo=", go1Var, 6);
17:         pluginGeneratedSerialDescriptor.k("url", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("title", true);
20:         pluginGeneratedSerialDescriptor.k("preview", true);
```

### `sources/defpackage/gtw.java:17`
```text
15:         a = gtwVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("V9GeZRQL7IPP58Qe1RNpHLxiP5tdJA__gueyZsu58Lk=", gtwVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/guw.java:17`
```text
15:         a = guwVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("PaUo0MxLOPYmRKEc3l1YELKUJ6pDkMpsUqeL-7D67vo=", guwVar, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("id", false);
19:         pluginGeneratedSerialDescriptor.k("userId", false);
```

### `sources/defpackage/h9.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("status", false);
19:         pluginGeneratedSerialDescriptor.k("handoffId", false);
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
```

### `sources/defpackage/h9.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
23:         pluginGeneratedSerialDescriptor.k("destinationUserMessageId", false);
24:         pluginGeneratedSerialDescriptor.k("restorationSnapshot", true);
```

### `sources/defpackage/hdc0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("nsTVr1i5xFN5Er6CXjDLrq11mpJYF_nKVrMcd1Dky5I=", hdc0Var, 5);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("workConversationId", false);
20:         pluginGeneratedSerialDescriptor.k("restoredUserMessageId", false);
```

### `sources/defpackage/hdc0.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("workConversationId", false);
20:         pluginGeneratedSerialDescriptor.k("restoredUserMessageId", false);
21:         pluginGeneratedSerialDescriptor.k("restoredModelSlug", false);
```

### `sources/defpackage/hga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesSearchHereButtonClicked chatgptPlacesSearchHereButtonClicked = (ChatgptPlacesSearchHereButtonClicked) aVar;
14:         if (chatgptPlacesSearchHereButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesSearchHereButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/hga.java:15`
```text
13:         ChatgptPlacesSearchHereButtonClicked chatgptPlacesSearchHereButtonClicked = (ChatgptPlacesSearchHereButtonClicked) aVar;
14:         if (chatgptPlacesSearchHereButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesSearchHereButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesSearchHereButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/hij.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B-\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0018
8: public final class hij extends b {
```

### `sources/defpackage/hij.java:7`
```text
5: 
6: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B-\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0018
8: public final class hij extends b {
9:     private Double _contentReferenceIndex;
```

### `sources/defpackage/hij.java:10`
```text
8: public final class hij extends b {
9:     private Double _contentReferenceIndex;
10:     private String _conversationId;
11:     private String _messageId;
12: 
```

### `sources/defpackage/hij.java:14`
```text
12: 
13:     public hij(String str, String str2, Double d) {
14:         this._conversationId = str;
15:         this._messageId = str2;
16:         this._contentReferenceIndex = d;
```

### `sources/defpackage/i1q.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("saveId", true);
18:         pluginGeneratedSerialDescriptor.k("projectId", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationTitle", true);
21:         pluginGeneratedSerialDescriptor.k("title", true);
```

### `sources/defpackage/i3i.java:187`
```text
185:         this.c.b(jygVar, stringExtra);
186:         if (jygVar == jyg.ScreenShare && stringExtra != null) {
187:             String stringExtra3 = intent.getStringExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID");
188:             String str = stringExtra3 != null ? stringExtra3 : null;
189:             n3i n3iVar = this.b;
```

### `sources/defpackage/i53.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("2RSRwgE7HSL3QFKJ45raMqqb0_5bsJ7GjneqHZr5fn4=", i53Var, 6);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("writingBlockId", false);
21:         pluginGeneratedSerialDescriptor.k("feedback", false);
```

### `sources/defpackage/idi.java:17`
```text
15:         a = idiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("swwt_wCse71rBTYUEnPQgLIGAC0MqiObKIjCBtzmra0=", idiVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("inputMessage", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/iga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesTimeToFirstPin chatgptPlacesTimeToFirstPin = (ChatgptPlacesTimeToFirstPin) aVar;
14:         if (chatgptPlacesTimeToFirstPin.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesTimeToFirstPin.getConversation_id());
16:         }
```

### `sources/defpackage/iga.java:15`
```text
13:         ChatgptPlacesTimeToFirstPin chatgptPlacesTimeToFirstPin = (ChatgptPlacesTimeToFirstPin) aVar;
14:         if (chatgptPlacesTimeToFirstPin.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesTimeToFirstPin.getConversation_id());
16:         }
17:         if (chatgptPlacesTimeToFirstPin.getMessage_id() != null) {
```

### `sources/defpackage/ilh.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("continued_in_work_banner", ilhVar, 2);
17:         pluginGeneratedSerialDescriptor.k("sourceMessageId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.m(new v10(false, (byte) 16));
20:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/iqk.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("source", true);
21:         pluginGeneratedSerialDescriptor.k("allowFileExport", true);
22:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
24:     }
```

### `sources/defpackage/j1l.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("referenceStartIdx", false);
20:         pluginGeneratedSerialDescriptor.k("referenceEndIdx", false);
21:         pluginGeneratedSerialDescriptor.k("sheetConversationId", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
23:     }
```

### `sources/defpackage/jhj.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'payload':m<s,u>,'conversationId':s?,'sourceMessageId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
```

### `sources/defpackage/jhj.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'payload':m<s,u>,'conversationId':s?,'sourceMessageId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
10:     private String _conversationId;
```

### `sources/defpackage/jhj.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
10:     private String _conversationId;
11:     private Map<String, ? extends Object> _payload;
12:     private String _sourceMessageId;
```

### `sources/defpackage/jhj.java:16`
```text
14:     public jhj(Map<String, ? extends Object> map, String str, String str2) {
15:         this._payload = map;
16:         this._conversationId = str;
17:         this._sourceMessageId = str2;
18:     }
```

### `sources/defpackage/jsa.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoicePreFirstAssistantUserTurnFinished chatgptVoicePreFirstAssistantUserTurnFinished = (ChatgptVoicePreFirstAssistantUserTurnFinished) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id());
16:         }
```

### `sources/defpackage/jsa.java:15`
```text
13:         ChatgptVoicePreFirstAssistantUserTurnFinished chatgptVoicePreFirstAssistantUserTurnFinished = (ChatgptVoicePreFirstAssistantUserTurnFinished) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id());
16:         }
17:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getDuration_ms() != null) {
```

### `sources/defpackage/jvt.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("conversation_reference", true);
18:         pluginGeneratedSerialDescriptor.k("localViewedAt", true);
19:         pluginGeneratedSerialDescriptor.k("remote_conversation_id", true);
20:         pluginGeneratedSerialDescriptor.k("local_conversation_id", true);
21:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
```

### `sources/defpackage/jvt.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("localViewedAt", true);
19:         pluginGeneratedSerialDescriptor.k("remote_conversation_id", true);
20:         pluginGeneratedSerialDescriptor.k("local_conversation_id", true);
21:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/k1i.java:17`
```text
15:         a = k1iVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("IrZwQ8hG4GykRMAz22Z2TfE32CPdXV7OwuaJEfCtzf4=", k1iVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("token", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kc2.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("width", true);
20:         pluginGeneratedSerialDescriptor.k("height", true);
21:         pluginGeneratedSerialDescriptor.k("conversationId", true);
22:         pluginGeneratedSerialDescriptor.k("generatedWithThinkingModel", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kcb0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Ahgs58qTwF4L2qWhjLj-pliK2x4F_jdc_BimewMvc7M=", kcb0Var, 4);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("version", true);
```

### `sources/defpackage/kdh.java:17`
```text
15:         a = kdhVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("5-q4VkbWOt09LSFMpkdNDccgIYC8c1pB2UBQTvDpc_k=", kdhVar, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationOwnerId", false);
19:         pluginGeneratedSerialDescriptor.k("gizmoId", false);
```

### `sources/defpackage/kei.java:17`
```text
15:         a = keiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("a9RI58khYWjF-AxTRF6a31v0wslUMUdOXDwOv7brKc4=", keiVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("title", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kmi.java:4`
```text
2: 
3: public abstract class kmi {
4:     public static final vk30 a = new vk30("Conversations", dvv.D0(new g100(-2052184858, "MessageChunk.sq:saveMessageChunk"), new g100(-625220995, "MessageChunk.sq:deleteByMessageId"), new g100(-164501711, "Message.sq:delete"), new g100(-127674581, "Conversation.sq:delete"), new g100(-112721744, "Message.sq:deleteAll"), new g100(-102650410, "Conversation.sq:exists"), new g100(-81574436, "Conversation.sq:exists"), new g100(-41583637, "Conversation.sq:getAll"), new g100(23991353, "Conversation.sq:i
5: }
```

### `sources/defpackage/ksa.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoicePreFirstAssistantUserTurnStarted chatgptVoicePreFirstAssistantUserTurnStarted = (ChatgptVoicePreFirstAssistantUserTurnStarted) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id());
16:         }
```

### `sources/defpackage/ksa.java:15`
```text
13:         ChatgptVoicePreFirstAssistantUserTurnStarted chatgptVoicePreFirstAssistantUserTurnStarted = (ChatgptVoicePreFirstAssistantUserTurnStarted) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id());
16:         }
17:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getUser_turn_index() != null) {
```

### `sources/defpackage/ku9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptAssistantResponseEndVisible.getAssistant_message_id());
16:         }
17:         if (chatgptAssistantResponseEndVisible.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptAssistantResponseEndVisible.getConversation_id());
19:         }
```

### `sources/defpackage/ku9.java:18`
```text
16:         }
17:         if (chatgptAssistantResponseEndVisible.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptAssistantResponseEndVisible.getConversation_id());
19:         }
20:         if (chatgptAssistantResponseEndVisible.getUser_prompt_message_id() != null) {
```

### `sources/defpackage/kx1.java:17`
```text
15:         a = kx1Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("conversation", kx1Var, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.m(new v10((byte) 3));
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kze0.java:17`
```text
15:         a = kze0Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("h_nzZnyLXkgIUw8OtJV3zGyj8wO-k2_kJsBNHDtvwnU=", kze0Var, 7);
17:         pluginGeneratedSerialDescriptor.k("conversationId", true);
18:         pluginGeneratedSerialDescriptor.k("gizmoId", false);
19:         pluginGeneratedSerialDescriptor.k("nonce", false);
```

### `sources/defpackage/kzi.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("items", false);
19:         pluginGeneratedSerialDescriptor.k("shippingAddress", true);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
```

### `sources/defpackage/l7a.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptImageLightboxMetadata chatgptImageLightboxMetadata = (ChatgptImageLightboxMetadata) aVar;
14:         if (chatgptImageLightboxMetadata.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptImageLightboxMetadata.getConversation_id());
16:         }
```

### `sources/defpackage/l7a.java:15`
```text
13:         ChatgptImageLightboxMetadata chatgptImageLightboxMetadata = (ChatgptImageLightboxMetadata) aVar;
14:         if (chatgptImageLightboxMetadata.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptImageLightboxMetadata.getConversation_id());
16:         }
17:         if (chatgptImageLightboxMetadata.getFile_id() != null) {
```

### `sources/defpackage/ldz.java:23`
```text
21:         pluginGeneratedSerialDescriptor.k("url", true);
22:         pluginGeneratedSerialDescriptor.k("urls", true);
23:         pluginGeneratedSerialDescriptor.k("conversationId", true);
24:         pluginGeneratedSerialDescriptor.k("assetId", true);
25:         pluginGeneratedSerialDescriptor.k("buttonType", true);
```

### `sources/defpackage/lt.java:62`
```text
60:         byte b = 2;
61:         yn ynVar = new yn(mz80VarM, mz80VarM3, new mm(3, psgVar, b), (byte) 2);
62:         asg asgVarD = vqi.d(asgVarA, "ActivelyStreamingConversationRepository/conversationIds");
63:         g6h g6hVar = zc70.a;
64:         this.t = cea0.R(ynVar, asgVarD, g6hVar, ggnVar);
```

### `sources/defpackage/m56.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("eventType", false);
19:         pluginGeneratedSerialDescriptor.k("eventCtaId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("messageId", false);
22:         pluginGeneratedSerialDescriptor.k("benefitId", true);
```

### `sources/defpackage/m6w.java:30`
```text
28:         pluginGeneratedSerialDescriptor.k("isArchived", true);
29:         pluginGeneratedSerialDescriptor.k("assetPointer", true);
30:         pluginGeneratedSerialDescriptor.k("conversationId", true);
31:         pluginGeneratedSerialDescriptor.k("createdAt", true);
32:         pluginGeneratedSerialDescriptor.k("prompt", true);
```

### `sources/defpackage/m9l.java:17`
```text
15:         a = m9lVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("RNfkCBCzr-0bkiZfnW-Ms3CNyGVkTH2QHyOSMGNXna4=", m9lVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/mdi.java:17`
```text
15:         a = mdiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("BaUO8q-KuTCMTJqFmVaxoaAxdc0ZFSU-y0TNHGxPEPE=", mdiVar, 4);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("marker", false);
```

### `sources/defpackage/mk40.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("wc4pSfZn_zsPaKWjaWuu3OAHRSH4IsFQrOURBRbSaZk=", mk40Var, 4);
17:         pluginGeneratedSerialDescriptor.k("accountId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("deviceId", false);
20:         pluginGeneratedSerialDescriptor.k("parentMessageId", false);
```

### `sources/defpackage/mnn.java:36`
```text
34:         ul0 ul0Var = ul0.h;
35:         g100 g100Var = new g100("message_id", str2);
36:         g100 g100Var2 = new g100("conversation_id", str);
37:         g100 g100Var3 = new g100("sidebar_session_id", this.c);
38:         g100 g100Var4 = new g100("entity_name", str3);
```

### `sources/defpackage/mnn.java:55`
```text
53:         ul0 ul0Var = ul0.g;
54:         g100 g100Var = new g100("message_id", str2);
55:         g100 g100Var2 = new g100("conversation_id", str);
56:         g100 g100Var3 = new g100("sidebar_session_id", this.c);
57:         g100 g100Var4 = new g100("entity_name", lnnVar.a);
```

### `sources/defpackage/mp9.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("accepted", mp9Var, 4);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("canUndo", false);
```

### `sources/defpackage/mu9.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptBackToLastViewedConversation chatgptBackToLastViewedConversation = (ChatgptBackToLastViewedConversation) aVar;
14:         if (chatgptBackToLastViewedConversation.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptBackToLastViewedConversation.getConversation_id());
16:         }
```

### `sources/defpackage/mu9.java:15`
```text
13:         ChatgptBackToLastViewedConversation chatgptBackToLastViewedConversation = (ChatgptBackToLastViewedConversation) aVar;
14:         if (chatgptBackToLastViewedConversation.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptBackToLastViewedConversation.getConversation_id());
16:         }
17:         if (chatgptBackToLastViewedConversation.getLast_viewed_age_seconds() != null) {
```

### `sources/defpackage/mv1.java:17`
```text
15:         a = mv1Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Ne8cMSk9rjMRAArnKtc-MKDhH0iCSDnudIs76e6MQ3o=", mv1Var, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/mw9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockEditButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockEditButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockEditButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/mw9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockEditButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockEditButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockEditButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/myr.java:18`
```text
16:         a = myrVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("nYw9PplnhJOmYiYc1VEeAFFFKFyAEHKOEV3guQKGp1Q=", myrVar, 7);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("count", false);
20:         pluginGeneratedSerialDescriptor.k("renderFormat", false);
```

### `sources/defpackage/n32.java:17`
```text
15:         a = n32Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("uBk-WFOqpx_gDP796Rs-Qeb6uEOVaHaVazZkpPk2hWQ=", n32Var, 3);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("currentNodeId", true);
19:         pluginGeneratedSerialDescriptor.k("isAnonymous", false);
```

### `sources/defpackage/nav.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("hasPin", true);
19:         pluginGeneratedSerialDescriptor.k("projectId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationIds", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
```

### `sources/defpackage/ne90.java:99`
```text
97:             }
98:             if (str2 != null) {
99:                 intentPutExtra.putExtra("conversation_id", str2);
100:             }
101:         }
```

### `sources/defpackage/nhi.java:25`
```text
23:         dgt dgtVarC = dhtVar.c();
24:         c cVarL = jht.l(dhtVar.h());
25:         String str = ((zch) dgtVarC.a(zch.Companion.serializer(), (b) dvv.A0(cVarL, "conversation_id"))).a;
26:         b bVar = (b) cVarL.get("update_type");
27:         if (bVar == null || (strA = jht.m(bVar).a()) == null) {
```

### `sources/defpackage/no9.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("47mQTng_hDfBuFNNAWhQ9muqB1JXSGIws89ysRaZwcQ=", no9Var, 6);
18:         pluginGeneratedSerialDescriptor.k("id", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("author", false);
21:         pluginGeneratedSerialDescriptor.k("recipient", true);
```

### `sources/defpackage/nph.java:17`
```text
15:         a = nphVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("L-3v4JYFDHblHYPrHGsLLYfF6KU-GKQ5ZQasXb3JW0w=", nphVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("turnExchangeId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/nra.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoiceCotTap chatgptVoiceCotTap = (ChatgptVoiceCotTap) aVar;
14:         if (chatgptVoiceCotTap.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoiceCotTap.getConversation_id());
16:         }
```

### `sources/defpackage/nra.java:15`
```text
13:         ChatgptVoiceCotTap chatgptVoiceCotTap = (ChatgptVoiceCotTap) aVar;
14:         if (chatgptVoiceCotTap.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoiceCotTap.getConversation_id());
16:         }
17:         if (chatgptVoiceCotTap.getMessage_id() != null) {
```

### `sources/defpackage/nsh.java:17`
```text
15:         a = nshVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("qB5oUqtRHJmrMgXVDR1N-lb9TTstceCcPakaHFz1Teg=", nshVar, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         descriptor = pluginGeneratedSerialDescriptor;
19:     }
```

### `sources/defpackage/nw9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockFullScreenButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockFullScreenButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockFullScreenButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/nw9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockFullScreenButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockFullScreenButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockFullScreenButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/nyk.java:17`
```text
15:         a = nykVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("existing-conversation", nykVar, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.m(new v10((byte) 21));
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/o210.java:17`
```text
15:         a = o210Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("F7tT5sfvHK8L6_SVEozg8ZEyBmfhrnzw5r-LzAs2lNU=", o210Var, 6);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/o48.java:210`
```text
208:         if (i2 == 0) {
209:             ct40.j(objA);
210:             ml30 ml30VarR2 = this.a.r2(new Integer(750218886), "DELETE\nFROM DBMessage\nWHERE conversationId = ?", 1, new l0x(this, str, (byte) 0));
211:             n0xVar.p = 1;
212:             objA = ml30VarR2.a(n0xVar);
```

### `sources/defpackage/o48.java:357`
```text
355:         if (i2 == 0) {
356:             ct40.j(objA);
357:             ml30 ml30VarR2 = this.a.r2(new Integer(1180159107), "INSERT OR REPLACE\nINTO DBMessage (id, conversationId)\nVALUES (?, ?)", 2, new svw(this, lgjVar, b));
358:             p0xVar.p = 1;
359:             objA = ml30VarR2.a(p0xVar);
```

### `sources/defpackage/oei.java:17`
```text
15:         a = oeiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("3ojDDFJ742G6_C65HYW-_cHzBM03lkKeOAF22_7KdW0=", oeiVar, 4);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("numVariantsInStream", false);
19:         pluginGeneratedSerialDescriptor.k("displayTreatment", true);
```

### `sources/defpackage/oh40.java:24`
```text
22:         pluginGeneratedSerialDescriptor.k("calpicoRoomId", true);
23:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
24:         pluginGeneratedSerialDescriptor.k("conversationId", true);
25:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
26:         pluginGeneratedSerialDescriptor.k("shareId", true);
```

### `sources/defpackage/oh40.java:25`
```text
23:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
24:         pluginGeneratedSerialDescriptor.k("conversationId", true);
25:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
26:         pluginGeneratedSerialDescriptor.k("shareId", true);
27:         pluginGeneratedSerialDescriptor.k("productId", true);
```

### `sources/defpackage/oha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductOfferListShownEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductOfferListShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductOfferListShownEvent.getConversation_id());
22:         }
```

### `sources/defpackage/oha.java:21`
```text
19:         }
20:         if (chatgptProductOfferListShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductOfferListShownEvent.getConversation_id());
22:         }
23:         if (chatgptProductOfferListShownEvent.getMessage_id() != null) {
```

### `sources/defpackage/oi60.java:19`
```text
17:         a = oi60Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("l0fa4MYmh_C5r1ScAmZBEVikBeML7O6wOGl96O1bmVI=", oi60Var, 12);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/okk.java:17`
```text
15:         a = okkVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("jmN2Wscrb0V9UllU--TXk-lckBxOlKGdDV8c0qL13o8=", okkVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ot.java:89`
```text
87: 
88:     public static void G(NotificationChannel notificationChannel, String str, String str2) {
89:         notificationChannel.setConversationId(str, str2);
90:     }
91: 
```

### `sources/defpackage/ot.java:150`
```text
148:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_INT_ID", xxgVar.e);
149:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str4);
150:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str);
151:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_ID", str2);
152:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
```

### `sources/defpackage/ot.java:161`
```text
159: 
160:     public static final PendingIntent d(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
161:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
162:         if (bundle != null) {
163:             intentPutExtra.putExtras(bundle);
```

### `sources/defpackage/ot.java:169`
```text
167: 
168:     public static final Intent e(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
169:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
170:         if (bundle != null) {
171:             intentPutExtra.putExtras(bundle);
```

### `sources/defpackage/ot.java:186`
```text
184:         NotificationChannel notificationChannel2 = new NotificationChannel(str2, str4, notificationChannel.getImportance());
185:         if (i >= 30) {
186:             notificationChannel2.setConversationId(str, str3);
187:         }
188:         notificationChannel2.setAllowBubbles(true);
```

### `sources/defpackage/ot.java:326`
```text
324: 
325:     public static String q(NotificationChannel notificationChannel) {
326:         return notificationChannel.getConversationId();
327:     }
328: 
```

### `sources/defpackage/ow9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockPreviewButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockPreviewButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockPreviewButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/ow9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockPreviewButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockPreviewButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockPreviewButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/p0h.java:18`
```text
16:         a = p0hVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("f_XXtjAPVPPJG_9sQwjWWOKsSKIEwwJgCMnxyBSxrx0=", p0hVar, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationIds", false);
```

_Hits captured: 180 (cap 180)_

## GENERATION_MESSAGE_ACTIONS

### `sources/androidx/camera/core/internal/compat/quirk/CaptureFailedRetryQuirk.java:8`
```text
6: import java.util.HashSet;
7: 
8: public class CaptureFailedRetryQuirk implements pn30 {
9:     public static final HashSet a = new HashSet(Collections.singletonList(Pair.create("SAMSUNG", "SM-G981U1")));
10: }
```

### `sources/androidx/compose/ui/node/Owner.java:64`
```text
62:     rtq getGraphicsContext();
63: 
64:     f0r getHapticFeedBack();
65: 
66:     bos getInputModeManager();
```

### `sources/androidx/core/widget/NestedScrollView.java:116`
```text
114:     }
115: 
116:     private mt50 getScrollFeedbackProvider() {
117:         mt50 mt50Var = this.g;
118:         if (mt50Var != null) {
```

### `sources/androidx/core/widget/NestedScrollView.java:1371`
```text
1369:         int scrollY2 = getScrollY() - scrollY;
1370:         if (motionEvent != null && scrollY2 != 0) {
1371:             getScrollFeedbackProvider().a.onScrollProgress(motionEvent.getDeviceId(), motionEvent.getSource(), i2, scrollY2);
1372:         }
1373:         iArr2[1] = 0;
```

### `sources/androidx/core/widget/NestedScrollView.java:1385`
```text
1383:                 if (motionEvent != null) {
1384:                     z2 = false;
1385:                     getScrollFeedbackProvider().a.onScrollLimit(motionEvent.getDeviceId(), motionEvent.getSource(), i2, false);
1386:                 } else {
1387:                     z2 = false;
```

### `sources/androidx/core/widget/NestedScrollView.java:1412`
```text
1410:             he7.G(edgeEffect2, (-i8) / getHeight(), i3 / getWidth());
1411:             if (motionEvent != null) {
1412:                 getScrollFeedbackProvider().a.onScrollLimit(motionEvent.getDeviceId(), motionEvent.getSource(), i2, true);
1413:             }
1414:             if (!edgeEffect.isFinished()) {
```

### `sources/androidx/credentials/playservices/controllers/CredentialProviderBaseController.java:50`
```text
48: 
49:     public static final Companion INSTANCE = new Companion(null);
50:     private static final Set<Integer> retryables = cr3.e1(new Integer[]{7, 20});
51:     private static final int CONTROLLER_REQUEST_CODE = 1;
52: 
```

### `sources/androidx/credentials/playservices/controllers/CredentialProviderBaseController.java:73`
```text
71:     }
72: 
73:     @Metadata(d1 = {"\u0000L\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\b\n\u0002\u0010\"\n\u0002\b\u001c\b\u0086\u0003\u0018\u00002\u00020\u0001B\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003J#\u0010\n\u001a\u00020\u00072\b\u0010\u0005\u001a\u0004
74:     public static final class Companion {
75:         public Companion(DefaultConstructorMarker defaultConstructorMarker) {
```

### `sources/androidx/credentials/playservices/controllers/CredentialProviderBaseController.java:108`
```text
106:         }
107: 
108:         public final Set<Integer> getRetryables() {
109:             return CredentialProviderBaseController.retryables;
110:         }
```

### `sources/androidx/credentials/playservices/controllers/CredentialProviderBaseController.java:109`
```text
107: 
108:         public final Set<Integer> getRetryables() {
109:             return CredentialProviderBaseController.retryables;
110:         }
111: 
```

### `sources/com/openai/chatgpt/R.java:3264`
```text
3262:         public static final int hand_peace = 0x7f08023f;
3263:         public static final int hand_raised = 0x7f080240;
3264:         public static final int haptic_feedback = 0x7f080241;
3265:         public static final int haze_noise = 0x7f080243;
3266:         public static final int headphones = 0x7f080244;
```

### `sources/com/openai/chatgpt/R.java:3579`
```text
3577:         public static final int rainy_cloud = 0x7f0803d9;
3578:         public static final int redo = 0x7f0803df;
3579:         public static final int regenerate = 0x7f0803e0;
3580:         public static final int remix_circle = 0x7f0803e2;
3581:         public static final int remix_images = 0x7f0803e3;
```

### `sources/com/openai/chatgpt/R.java:5095`
```text
5093:         public static final int retake_button = 0x7f0b0468;
5094:         public static final int retreat = 0x7f0b0469;
5095:         public static final int retry_button = 0x7f0b046a;
5096:         public static final int retry_container = 0x7f0b046b;
5097:         public static final int reverse = 0x7f0b046c;
```

### `sources/com/openai/chatgpt/R.java:5096`
```text
5094:         public static final int retreat = 0x7f0b0469;
5095:         public static final int retry_button = 0x7f0b046a;
5096:         public static final int retry_container = 0x7f0b046b;
5097:         public static final int reverse = 0x7f0b046c;
5098:         public static final int reverseSawtooth = 0x7f0b046d;
```

### `sources/com/openai/chatgpt/R.java:5180`
```text
5178:         public static final int selfie_overlay = 0x7f0b04bd;
5179:         public static final int selfie_window = 0x7f0b04be;
5180:         public static final int sentry_dialog_user_feedback_btn_cancel = 0x7f0b04bf;
5181:         public static final int sentry_dialog_user_feedback_btn_send = 0x7f0b04c0;
5182:         public static final int sentry_dialog_user_feedback_edt_description = 0x7f0b04c1;
```

### `sources/com/openai/chatgpt/R.java:5181`
```text
5179:         public static final int selfie_window = 0x7f0b04be;
5180:         public static final int sentry_dialog_user_feedback_btn_cancel = 0x7f0b04bf;
5181:         public static final int sentry_dialog_user_feedback_btn_send = 0x7f0b04c0;
5182:         public static final int sentry_dialog_user_feedback_edt_description = 0x7f0b04c1;
5183:         public static final int sentry_dialog_user_feedback_edt_email = 0x7f0b04c2;
```

### `sources/com/openai/chatgpt/R.java:5182`
```text
5180:         public static final int sentry_dialog_user_feedback_btn_cancel = 0x7f0b04bf;
5181:         public static final int sentry_dialog_user_feedback_btn_send = 0x7f0b04c0;
5182:         public static final int sentry_dialog_user_feedback_edt_description = 0x7f0b04c1;
5183:         public static final int sentry_dialog_user_feedback_edt_email = 0x7f0b04c2;
5184:         public static final int sentry_dialog_user_feedback_edt_name = 0x7f0b04c3;
```

### `sources/com/openai/chatgpt/R.java:5183`
```text
5181:         public static final int sentry_dialog_user_feedback_btn_send = 0x7f0b04c0;
5182:         public static final int sentry_dialog_user_feedback_edt_description = 0x7f0b04c1;
5183:         public static final int sentry_dialog_user_feedback_edt_email = 0x7f0b04c2;
5184:         public static final int sentry_dialog_user_feedback_edt_name = 0x7f0b04c3;
5185:         public static final int sentry_dialog_user_feedback_layout = 0x7f0b04c4;
```

### `sources/com/openai/chatgpt/R.java:5184`
```text
5182:         public static final int sentry_dialog_user_feedback_edt_description = 0x7f0b04c1;
5183:         public static final int sentry_dialog_user_feedback_edt_email = 0x7f0b04c2;
5184:         public static final int sentry_dialog_user_feedback_edt_name = 0x7f0b04c3;
5185:         public static final int sentry_dialog_user_feedback_layout = 0x7f0b04c4;
5186:         public static final int sentry_dialog_user_feedback_logo = 0x7f0b04c5;
```

### `sources/com/openai/chatgpt/R.java:5185`
```text
5183:         public static final int sentry_dialog_user_feedback_edt_email = 0x7f0b04c2;
5184:         public static final int sentry_dialog_user_feedback_edt_name = 0x7f0b04c3;
5185:         public static final int sentry_dialog_user_feedback_layout = 0x7f0b04c4;
5186:         public static final int sentry_dialog_user_feedback_logo = 0x7f0b04c5;
5187:         public static final int sentry_dialog_user_feedback_title = 0x7f0b04c6;
```

### `sources/com/openai/chatgpt/R.java:5186`
```text
5184:         public static final int sentry_dialog_user_feedback_edt_name = 0x7f0b04c3;
5185:         public static final int sentry_dialog_user_feedback_layout = 0x7f0b04c4;
5186:         public static final int sentry_dialog_user_feedback_logo = 0x7f0b04c5;
5187:         public static final int sentry_dialog_user_feedback_title = 0x7f0b04c6;
5188:         public static final int sentry_dialog_user_feedback_txt_description = 0x7f0b04c7;
```

### `sources/com/openai/chatgpt/R.java:5187`
```text
5185:         public static final int sentry_dialog_user_feedback_layout = 0x7f0b04c4;
5186:         public static final int sentry_dialog_user_feedback_logo = 0x7f0b04c5;
5187:         public static final int sentry_dialog_user_feedback_title = 0x7f0b04c6;
5188:         public static final int sentry_dialog_user_feedback_txt_description = 0x7f0b04c7;
5189:         public static final int sentry_dialog_user_feedback_txt_email = 0x7f0b04c8;
```

### `sources/com/openai/chatgpt/R.java:5188`
```text
5186:         public static final int sentry_dialog_user_feedback_logo = 0x7f0b04c5;
5187:         public static final int sentry_dialog_user_feedback_title = 0x7f0b04c6;
5188:         public static final int sentry_dialog_user_feedback_txt_description = 0x7f0b04c7;
5189:         public static final int sentry_dialog_user_feedback_txt_email = 0x7f0b04c8;
5190:         public static final int sentry_dialog_user_feedback_txt_name = 0x7f0b04c9;
```

### `sources/com/openai/chatgpt/R.java:5189`
```text
5187:         public static final int sentry_dialog_user_feedback_title = 0x7f0b04c6;
5188:         public static final int sentry_dialog_user_feedback_txt_description = 0x7f0b04c7;
5189:         public static final int sentry_dialog_user_feedback_txt_email = 0x7f0b04c8;
5190:         public static final int sentry_dialog_user_feedback_txt_name = 0x7f0b04c9;
5191:         public static final int sentry_privacy = 0x7f0b04ca;
```

### `sources/com/openai/chatgpt/R.java:5190`
```text
5188:         public static final int sentry_dialog_user_feedback_txt_description = 0x7f0b04c7;
5189:         public static final int sentry_dialog_user_feedback_txt_email = 0x7f0b04c8;
5190:         public static final int sentry_dialog_user_feedback_txt_name = 0x7f0b04c9;
5191:         public static final int sentry_privacy = 0x7f0b04ca;
5192:         public static final int shadow = 0x7f0b04cb;
```

### `sources/com/openai/chatgpt/R.java:6838`
```text
6836:         public static final int select_dialog_multichoice_material = 0x7f0e057c;
6837:         public static final int select_dialog_singlechoice_material = 0x7f0e057d;
6838:         public static final int sentry_dialog_user_feedback = 0x7f0e057e;
6839:         public static final int size_match_match = 0x7f0e057f;
6840:         public static final int size_match_wrap = 0x7f0e0580;
```

### `sources/com/openai/chatgpt/R.java:6951`
```text
6949:         public static final int image_gen_tool_summarizer_display_text_progress_creating_final = 0x7f12004a;
6950:         public static final int image_share_menu_series = 0x7f12004b;
6951:         public static final int locked_conversations_pin_retry_minutes = 0x7f12004c;
6952:         public static final int message_sources_show_more_count = 0x7f12004d;
6953:         public static final int pins_max_pins_reached_title = 0x7f12004f;
```

### `sources/com/openai/feature/conversation/common/businesslogic/FailedMessageRetryException.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/businesslogic/FailedMessageRetryException;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: final class FailedMessageRetryException extends Exception {
7:     public FailedMessageRetryException() {
```

### `sources/com/openai/feature/conversation/common/businesslogic/FailedMessageRetryException.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/businesslogic/FailedMessageRetryException;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: final class FailedMessageRetryException extends Exception {
7:     public FailedMessageRetryException() {
8:         super("failedMessageRetry");
```

### `sources/com/openai/feature/conversation/common/businesslogic/FailedMessageRetryException.java:7`
```text
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/businesslogic/FailedMessageRetryException;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: final class FailedMessageRetryException extends Exception {
7:     public FailedMessageRetryException() {
8:         super("failedMessageRetry");
9:     }
```

### `sources/com/openai/feature/conversation/common/businesslogic/FailedMessageRetryException.java:8`
```text
6: final class FailedMessageRetryException extends Exception {
7:     public FailedMessageRetryException() {
8:         super("failedMessageRetry");
9:     }
10: }
```

### `sources/com/openai/feature/notification/impl/NotificationDeregisterWorker.java:108`
```text
106:         Throwable th = ((vey) bfyVar).a;
107:         if (pas.w(th)) {
108:             gev.f(gevVar, "Failed to de-register notification token, retrying", th, null, 12);
109:         } else {
110:             gev.f(gevVar, "Failed to de-register notification token, failed", th, null, 12);
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSchedulingException.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/notification/impl/NotificationFeedbackSchedulingException;", "Ljava/lang/RuntimeException;", "Lkotlin/RuntimeException;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class NotificationFeedbackSchedulingException extends RuntimeException {
7: }
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSchedulingException.java:6`
```text
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/notification/impl/NotificationFeedbackSchedulingException;", "Ljava/lang/RuntimeException;", "Lkotlin/RuntimeException;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class NotificationFeedbackSchedulingException extends RuntimeException {
7: }
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:41`
```text
39: import defpackage.zyu;
40: import kotlin.Metadata;
41: import protobuf_analytics_events.v1.ChatgptNotificationFeedbackLifecycle;
42: 
43: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerP
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:43`
```text
41: import protobuf_analytics_events.v1.ChatgptNotificationFeedbackLifecycle;
42: 
43: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerP
44: public final class NotificationFeedbackSubmissionWorker extends CoroutineWorker {
45:     public static final idv d = new idv(28);
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:44`
```text
42: 
43: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerP
44: public final class NotificationFeedbackSubmissionWorker extends CoroutineWorker {
45:     public static final idv d = new idv(28);
46:     public static final long e;
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:56`
```text
54:     }
55: 
56:     public NotificationFeedbackSubmissionWorker(Context context, WorkerParameters workerParameters) {
57:         super(context, workerParameters);
58:         this.c = wnm.F(6, "NotificationFeedbackSubmissionWorker");
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:58`
```text
56:     public NotificationFeedbackSubmissionWorker(Context context, WorkerParameters workerParameters) {
57:         super(context, workerParameters);
58:         this.c = wnm.F(6, "NotificationFeedbackSubmissionWorker");
59:     }
60: 
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:107`
```text
105:             gev gevVar = this.c;
106:             if (fm2Var == null) {
107:                 gev.f(gevVar, "Missing or invalid notification feedback submission data", null, null, 14);
108:                 return new yyu();
109:             }
```

### `sources/com/openai/feature/notification/impl/NotificationFeedbackSubmissionWorker.java:151`
```text
149:             x0zVar = null;
150:         }
151:         x0zVar.a.i(new ChatgptNotificationFeedbackLifecycle(fm2Var2.a, d1zVar.a(), fm2Var2.b, null, 8, null));
152:         if (d1zVar.equals(a1z.a)) {
153:             return bzu.a();
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:35`
```text
33: import kotlin.Metadata;
34: 
35: @Metadata(d1 = {"\u0000R\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u0000 (2\u00020\u0001:\u0002)*B\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u001
36: public final class NotificationMediaFetchWorker extends CoroutineWorker {
37:     public static final int $stable = 8;
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:72`
```text
70:     }
71: 
72:     private final bzu mediaFetchRetryResult() {
73:         return getRunAttemptCount() < 3 ? new zyu() : new yyu();
74:     }
```

### `sources/com/openai/feature/notification/impl/NotificationRegisterWorker.java:99`
```text
97:             Throwable th = ((rxb0) yxb0Var).b;
98:             if (pas.w(th)) {
99:                 gev.f(gevVar, "Failed to register notification token, retrying", th, null, 12);
100:                 return new zyu();
101:             }
```

### `sources/com/openai/integrity/impl/c.java:522`
```text
520:         usv usvVar = new usv();
521:         usvVar.putAll(map);
522:         usvVar.put("initialization_retry_count", Integer.valueOf(this.i));
523:         usvVar.put("token_retry_count", Integer.valueOf(this.j));
524:         usvVar.put("lifetime_integrity_initialization_count", Integer.valueOf(n));
```

### `sources/com/openai/integrity/impl/c.java:523`
```text
521:         usvVar.putAll(map);
522:         usvVar.put("initialization_retry_count", Integer.valueOf(this.i));
523:         usvVar.put("token_retry_count", Integer.valueOf(this.j));
524:         usvVar.put("lifetime_integrity_initialization_count", Integer.valueOf(n));
525:         return usvVar.b();
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceCreditVerificationHost.java:13`
```text
11: import kotlin.Metadata;
12: 
13: @Metadata(d1 = {"\u0000<\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J%\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\u00062\u0006\u0010\u0003\u001a\u00020\u00022\u0006\u0010\u0005\u001a\u00020\u0004H&¢\u0006\u0004\b\b\u0010\tJ\u001f\u001
14: @t5d0(propertyReplacements = "", proxyClass = yvo.class, schema = "'runCreditVerification':f|m|(r:'[0]', s): p<r:'[1]'>,'onCreditVerificationCompleted':f|m|(s, b),'closeCreditVerification':f?|m|()", typeReferences = {FinanceCreditVerificationEnvironment.class, zvo.class})
15: public interface FinanceCreditVerificationHost extends ValdiMarshallable {
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceCreditVerificationHost.java:19`
```text
17:     void closeCreditVerification();
18: 
19:     void onCreditVerificationCompleted(String status, boolean retryable);
20: 
21:     @Override
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Purchase':0,'RestorePurchases':1,'OpenExternalCheckout':2,'OpenLegal':3,'Retry':4,'Dismiss':5", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0007\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005j\u0002\b\u0006j\u0002\b\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind;", "", "Purchase", "RestorePurchases", "OpenExternalCheckout", "OpenLegal", "Retry", "Dismiss", "modules_chatgpt_subscription_pricing-chatgpt_subscription_pricing_ap
9: public final class SubscriptionPricingActionKind {
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Purchase':0,'RestorePurchases':1,'OpenExternalCheckout':2,'OpenLegal':3,'Retry':4,'Dismiss':5", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0007\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005j\u0002\b\u0006j\u0002\b\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind;", "", "Purchase", "RestorePurchases", "OpenExternalCheckout", "OpenLegal", "Retry", "Dismiss", "modules_chatgpt_subscription_pricing-chatgpt_subscription_pricing_ap
9: public final class SubscriptionPricingActionKind {
10:     public static final SubscriptionPricingActionKind Dismiss;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind.java:15`
```text
13:     public static final SubscriptionPricingActionKind Purchase;
14:     public static final SubscriptionPricingActionKind RestorePurchases;
15:     public static final SubscriptionPricingActionKind Retry;
16:     public static final SubscriptionPricingActionKind[] a;
17: 
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind.java:27`
```text
25:         SubscriptionPricingActionKind subscriptionPricingActionKind4 = new SubscriptionPricingActionKind("OpenLegal", 3);
26:         OpenLegal = subscriptionPricingActionKind4;
27:         SubscriptionPricingActionKind subscriptionPricingActionKind5 = new SubscriptionPricingActionKind("Retry", 4);
28:         Retry = subscriptionPricingActionKind5;
29:         SubscriptionPricingActionKind subscriptionPricingActionKind6 = new SubscriptionPricingActionKind("Dismiss", 5);
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingActionKind.java:28`
```text
26:         OpenLegal = subscriptionPricingActionKind4;
27:         SubscriptionPricingActionKind subscriptionPricingActionKind5 = new SubscriptionPricingActionKind("Retry", 4);
28:         Retry = subscriptionPricingActionKind5;
29:         SubscriptionPricingActionKind subscriptionPricingActionKind6 = new SubscriptionPricingActionKind("Dismiss", 5);
30:         Dismiss = subscriptionPricingActionKind6;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:222`
```text
220:             ikj inputData = getInputData();
221:             HashMap map = inputData.a;
222:             String strA5 = inputData.a("feedback_type");
223:             if (strA5 == null || (f9e0VarValueOf = f9e0.valueOf(strA5)) == null || (strA = inputData.a("feedback_voice_mode")) == null || (ife0VarValueOf = ife0.valueOf(strA)) == null) {
224:                 i = 14;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:223`
```text
221:             HashMap map = inputData.a;
222:             String strA5 = inputData.a("feedback_type");
223:             if (strA5 == null || (f9e0VarValueOf = f9e0.valueOf(strA5)) == null || (strA = inputData.a("feedback_voice_mode")) == null || (ife0VarValueOf = ife0.valueOf(strA)) == null) {
224:                 i = 14;
225:                 y8e0Var = null;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:227`
```text
225:                 y8e0Var = null;
226:             } else {
227:                 Object obj2 = map.get("feedback_options");
228:                 if (obj2 instanceof Object[]) {
229:                     Object[] objArr = (Object[]) obj2;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:247`
```text
245:                     listD1 = vfn.a;
246:                 }
247:                 String strA6 = inputData.a("feedback_other_option_text");
248:                 if (Collections.unmodifiableMap(map).containsKey("feedback_share_voice_session")) {
249:                     Object obj4 = Boolean.FALSE;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:248`
```text
246:                 }
247:                 String strA6 = inputData.a("feedback_other_option_text");
248:                 if (Collections.unmodifiableMap(map).containsKey("feedback_share_voice_session")) {
249:                     Object obj4 = Boolean.FALSE;
250:                     Object obj5 = map.get("feedback_share_voice_session");
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:250`
```text
248:                 if (Collections.unmodifiableMap(map).containsKey("feedback_share_voice_session")) {
249:                     Object obj4 = Boolean.FALSE;
250:                     Object obj5 = map.get("feedback_share_voice_session");
251:                     if (obj5 instanceof Boolean) {
252:                         obj4 = obj5;
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:258`
```text
256:                     bool = null;
257:                 }
258:                 String strA7 = inputData.a("feedback_source");
259:                 d9e0 d9e0VarValueOf = strA7 != null ? d9e0.valueOf(strA7) : null;
260:                 i = 14;
```

### `sources/com/plaid/internal/r0.java:167`
```text
165:                             }
166:                             y8 y8Var4 = z8.d;
167:                             String str8 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
168:                             y8Var4.getClass();
169:                             y8Var4.a(y6.WARN, (Throwable) null, str8);
```

### `sources/com/plaid/internal/r0.java:180`
```text
178:                     }
179:                     y8 y8Var6 = z8.d;
180:                     String str9 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
181:                     y8Var6.getClass();
182:                     y8Var6.a(y6.WARN, (Throwable) null, str9);
```

### `sources/com/plaid/internal/r0.java:185`
```text
183:                 } else if (m7Var instanceof j7) {
184:                     y8 y8Var7 = z8.d;
185:                     String str10 = "Channel fetch network error: " + ((j7) m7Var).a.getMessage() + ", will retry";
186:                     y8Var7.getClass();
187:                     y8Var7.a(y6.WARN, (Throwable) null, str10);
```

### `sources/com/plaid/internal/r0.java:194`
```text
192:                     }
193:                     y8 y8Var8 = z8.d;
194:                     String str11 = "Channel fetch unknown error: " + ((l7) m7Var).a.getMessage() + ", will retry";
195:                     y8Var8.getClass();
196:                     y8Var8.a(y6.ERROR, (Throwable) null, y8.a(str11, null));
```

### `sources/com/plaid/internal/r0.java:284`
```text
282:                         }
283:                         y8 y8Var12 = z8.d;
284:                         String str14 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
285:                         y8Var12.getClass();
286:                         y8Var12.a(y6.WARN, (Throwable) null, str14);
```

### `sources/com/plaid/internal/r0.java:297`
```text
295:                 }
296:                 y8 y8Var14 = z8.d;
297:                 String str15 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
298:                 y8Var14.getClass();
299:                 y8Var14.a(y6.WARN, (Throwable) null, str15);
```

### `sources/com/plaid/internal/r0.java:302`
```text
300:             } else if (m7Var instanceof j7) {
301:                 y8 y8Var15 = z8.d;
302:                 String str16 = "Channel fetch network error: " + ((j7) m7Var).a.getMessage() + ", will retry";
303:                 y8Var15.getClass();
304:                 y8Var15.a(y6.WARN, (Throwable) null, str16);
```

### `sources/com/plaid/internal/r0.java:311`
```text
309:                 }
310:                 y8 y8Var16 = z8.d;
311:                 String str17 = "Channel fetch unknown error: " + ((l7) m7Var).a.getMessage() + ", will retry";
312:                 y8Var16.getClass();
313:                 y8Var16.a(y6.ERROR, (Throwable) null, y8.a(str17, null));
```

### `sources/com/plaid/internal/r0.java:492`
```text
490:                         }
491:                         y8 y8Var112 = z8.d;
492:                         String str112 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
493:                         y8Var112.getClass();
494:                         y8Var112.a(y6.WARN, (Throwable) null, str112);
```

### `sources/com/plaid/internal/r0.java:505`
```text
503:                 }
504:                 y8 y8Var114 = z8.d;
505:                 String str113 = "Channel fetch HTTP error " + i7Var.a + ", will retry";
506:                 y8Var114.getClass();
507:                 y8Var114.a(y6.WARN, (Throwable) null, str113);
```

### `sources/com/plaid/internal/r0.java:510`
```text
508:             } else if (m7Var instanceof j7) {
509:                 y8 y8Var115 = z8.d;
510:                 String str114 = "Channel fetch network error: " + ((j7) m7Var).a.getMessage() + ", will retry";
511:                 y8Var115.getClass();
512:                 y8Var115.a(y6.WARN, (Throwable) null, str114);
```

### `sources/com/plaid/internal/r0.java:519`
```text
517:                 }
518:                 y8 y8Var116 = z8.d;
519:                 String str115 = "Channel fetch unknown error: " + ((l7) m7Var).a.getMessage() + ", will retry";
520:                 y8Var116.getClass();
521:                 y8Var116.a(y6.ERROR, (Throwable) null, y8.a(str115, null));
```

### `sources/com/segment/analytics/kotlin/core/retry/DropReason$Companion.java:1`
```text
1: package com.segment.analytics.kotlin.core.retry;
2: 
3: import defpackage.rpm;
```

### `sources/com/segment/analytics/kotlin/core/retry/DropReason$Companion.java:7`
```text
5: import kotlinx.serialization.KSerializer;
6: 
7: @Metadata(d1 = {"\u0000\u0012\n\u0000\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"com/segment/analytics/kotlin/core/retry/DropReason$Companion", "", "Lkotlinx/serialization/KSerializer;", "Lrpm;", "serializer", "()Lkotlinx/serialization/KSerializer;", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
8: public final class DropReason$Companion {
9:     public final KSerializer serializer() {
```

### `sources/com/segment/analytics/kotlin/core/retry/PipelineState$Companion.java:1`
```text
1: package com.segment.analytics.kotlin.core.retry;
2: 
3: import defpackage.qo10;
```

### `sources/com/segment/analytics/kotlin/core/retry/PipelineState$Companion.java:7`
```text
5: import kotlinx.serialization.KSerializer;
6: 
7: @Metadata(d1 = {"\u0000\u0012\n\u0000\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"com/segment/analytics/kotlin/core/retry/PipelineState$Companion", "", "Lkotlinx/serialization/KSerializer;", "Lqo10;", "serializer", "()Lkotlinx/serialization/KSerializer;", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
8: public final class PipelineState$Companion {
9:     public final KSerializer serializer() {
```

### `sources/com/segment/analytics/kotlin/core/retry/RateLimitConfig.java:1`
```text
1: package com.segment.analytics.kotlin.core.retry;
2: 
3: import com.google.mlkit.common.MlKitException;
```

### `sources/com/segment/analytics/kotlin/core/retry/RateLimitConfig.java:11`
```text
9: 
10: @ii60
11: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0003\b\u0087\b\u0018\u0000 \u00022\u00020\u0001:\u0002\u0003\u0002¨\u0006\u0004"}, d2 = {"Lcom/segment/analytics/kotlin/core/retry/RateLimitConfig;", "", "Companion", "$serializer", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
12: public final class RateLimitConfig {
13: 
```

### `sources/com/segment/analytics/kotlin/core/retry/RateLimitConfig.java:19`
```text
17:     public final int c;
18: 
19:     @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"Lcom/segment/analytics/kotlin/core/retry/RateLimitConfig$Companion;", "", "Lkotlinx/serialization/KSerializer;", "Lcom/segment/analytics/kotlin/core/retry/RateLimitConfig;", "serializer", "()Lkotlinx/s
20:     public static final class Companion {
21:         public final KSerializer serializer() {
```

### `sources/com/segment/analytics/kotlin/core/retry/RateLimitConfig.java:73`
```text
71:         StringBuilder sb = new StringBuilder("RateLimitConfig(enabled=");
72:         sb.append(this.a);
73:         sb.append(", maxRetryCount=");
74:         sb.append(this.b);
75:         sb.append(", maxRetryInterval=");
```

### `sources/com/segment/analytics/kotlin/core/retry/RateLimitConfig.java:75`
```text
73:         sb.append(", maxRetryCount=");
74:         sb.append(this.b);
75:         sb.append(", maxRetryInterval=");
76:         return jtz.p(sb, this.c, ')');
77:     }
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryBehavior$Companion.java:1`
```text
1: package com.segment.analytics.kotlin.core.retry;
2: 
3: import defpackage.ju40;
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryBehavior$Companion.java:7`
```text
5: import kotlinx.serialization.KSerializer;
6: 
7: @Metadata(d1 = {"\u0000\u0012\n\u0000\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"com/segment/analytics/kotlin/core/retry/RetryBehavior$Companion", "", "Lkotlinx/serialization/KSerializer;", "Lju40;", "serializer", "()Lkotlinx/serialization/KSerializer;", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
8: public final class RetryBehavior$Companion {
9:     public final KSerializer serializer() {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryBehavior$Companion.java:8`
```text
6: 
7: @Metadata(d1 = {"\u0000\u0012\n\u0000\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"com/segment/analytics/kotlin/core/retry/RetryBehavior$Companion", "", "Lkotlinx/serialization/KSerializer;", "Lju40;", "serializer", "()Lkotlinx/serialization/KSerializer;", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
8: public final class RetryBehavior$Companion {
9:     public final KSerializer serializer() {
10:         return (KSerializer) ju40.a.getValue();
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:1`
```text
1: package com.segment.analytics.kotlin.core.retry;
2: 
3: import defpackage.ii60;
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:14`
```text
12: 
13: @ii60
14: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0003\b\u0087\b\u0018\u0000 \u00022\u00020\u0001:\u0002\u0003\u0002¨\u0006\u0004"}, d2 = {"Lcom/segment/analytics/kotlin/core/retry/RetryState;", "", "Companion", "$serializer", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
15: public final class RetryState {
16: 
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:15`
```text
13: @ii60
14: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0003\b\u0087\b\u0018\u0000 \u00022\u00020\u0001:\u0002\u0003\u0002¨\u0006\u0004"}, d2 = {"Lcom/segment/analytics/kotlin/core/retry/RetryState;", "", "Companion", "$serializer", "core"}, k = 1, mv = {1, 8, 0}, xi = 48)
15: public final class RetryState {
16: 
17:     public static final Companion INSTANCE = new Companion();
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:23`
```text
21:     public final Map d;
22: 
23:     @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0086\u0003\u0018\u00002\u00020\u0001J\u0016\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002HÆ\u0001¢\u0006\u0004\b\u0004\u0010\u0005¨\u0006\u0006"}, d2 = {"Lcom/segment/analytics/kotlin/core/retry/RetryState$Companion;", "", "Lkotlinx/serialization/KSerializer;", "Lcom/segment/analytics/kotlin/core/retry/RetryState;", "serializer", "()Lkotlinx/serializati
24:     public static final class Companion {
25:         public final KSerializer serializer() {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:26`
```text
24:     public static final class Companion {
25:         public final KSerializer serializer() {
26:             return RetryState$$serializer.INSTANCE;
27:         }
28:     }
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:30`
```text
28:     }
29: 
30:     public RetryState(int i, qo10 qo10Var, Long l, int i2, Map map) {
31:         this.a = (i & 1) == 0 ? qo10.b : qo10Var;
32:         if ((i & 2) == 0) {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:49`
```text
47:     }
48: 
49:     public static RetryState a(RetryState retryState, qo10 qo10Var, Long l, int i, Map map, int i2) {
50:         if ((i2 & 1) != 0) {
51:             qo10Var = retryState.a;
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:51`
```text
49:     public static RetryState a(RetryState retryState, qo10 qo10Var, Long l, int i, Map map, int i2) {
50:         if ((i2 & 1) != 0) {
51:             qo10Var = retryState.a;
52:         }
53:         if ((i2 & 2) != 0) {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:54`
```text
52:         }
53:         if ((i2 & 2) != 0) {
54:             l = retryState.b;
55:         }
56:         if ((i2 & 4) != 0) {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:57`
```text
55:         }
56:         if ((i2 & 4) != 0) {
57:             i = retryState.c;
58:         }
59:         if ((i2 & 8) != 0) {
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:60`
```text
58:         }
59:         if ((i2 & 8) != 0) {
60:             map = retryState.d;
61:         }
62:         retryState.getClass();
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:62`
```text
60:             map = retryState.d;
61:         }
62:         retryState.getClass();
63:         return new RetryState(qo10Var, l, i, map);
64:     }
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:63`
```text
61:         }
62:         retryState.getClass();
63:         return new RetryState(qo10Var, l, i, map);
64:     }
65: 
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:70`
```text
68:             return true;
69:         }
70:         if (!(obj instanceof RetryState)) {
71:             return false;
72:         }
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:73`
```text
71:             return false;
72:         }
73:         RetryState retryState = (RetryState) obj;
74:         return this.a == retryState.a && wnm.k(this.b, retryState.b) && this.c == retryState.c && wnm.k(this.d, retryState.d);
75:     }
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:74`
```text
72:         }
73:         RetryState retryState = (RetryState) obj;
74:         return this.a == retryState.a && wnm.k(this.b, retryState.b) && this.c == retryState.c && wnm.k(this.d, retryState.d);
75:     }
76: 
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:84`
```text
82: 
83:     public final String toString() {
84:         StringBuilder sb = new StringBuilder("RetryState(pipelineState=");
85:         sb.append(this.a);
86:         sb.append(", waitUntilTime=");
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:88`
```text
86:         sb.append(", waitUntilTime=");
87:         sb.append(this.b);
88:         sb.append(", globalRetryCount=");
89:         sb.append(this.c);
90:         sb.append(", batchMetadata=");
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:94`
```text
92:     }
93: 
94:     public RetryState(qo10 qo10Var, Long l, int i, Map map) {
95:         this.a = qo10Var;
96:         this.b = l;
```

### `sources/com/segment/analytics/kotlin/core/retry/RetryState.java:101`
```text
99:     }
100: 
101:     public RetryState() {
102:         this(qo10.b, null, 0, wfn.a);
103:     }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:7`
```text
5: import kotlin.jvm.internal.DefaultConstructorMarker;
6: 
7: @Metadata(d1 = {"\u0000\u001e\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\bp\u0018\u00002\u00020\u0001:\u0004\u0002\u0003\u0004\u0005\u0082\u0001\u0004\u0006\u0007\b\tø\u0001\u0000\u0082\u0002\u0006\n\u0004\b!0\u0001¨\u0006\nÀ\u0006\u0001"}, d2 = {"Lcom/statsig/androidsdk/EventDeliveryResult;", "", "Success", "Retryable", "PermanentFailure", "PayloadTooLarge", "Lcom/statsig/androidsdk/EventDeliver
8: public interface EventDeliveryResult {
9: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:105`
```text
103:     }
104: 
105:     @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\t\n\u0002\b\r\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\b\u0086\b\u0018\u00002\u00020\u0001B\u001f\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0006\u0010\u0007J\u0010\u0010\u000e\u001a\u0004\u0018\u00010\u0003HÆ\u0003¢\u0006\u0002\u0010\tJ\u0010
106:     public static final class Retryable implements EventDeliveryResult {
107:         private final Long retryAfterMs;
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:106`
```text
104: 
105:     @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\t\n\u0002\b\r\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\b\u0086\b\u0018\u00002\u00020\u0001B\u001f\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0006\u0010\u0007J\u0010\u0010\u000e\u001a\u0004\u0018\u00010\u0003HÆ\u0003¢\u0006\u0002\u0010\tJ\u0010
106:     public static final class Retryable implements EventDeliveryResult {
107:         private final Long retryAfterMs;
108:         private final Integer statusCode;
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:107`
```text
105:     @Metadata(d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\t\n\u0002\b\r\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\b\u0086\b\u0018\u00002\u00020\u0001B\u001f\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0006\u0010\u0007J\u0010\u0010\u000e\u001a\u0004\u0018\u00010\u0003HÆ\u0003¢\u0006\u0002\u0010\tJ\u0010
106:     public static final class Retryable implements EventDeliveryResult {
107:         private final Long retryAfterMs;
108:         private final Integer statusCode;
109: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:110`
```text
108:         private final Integer statusCode;
109: 
110:         public Retryable(Integer num, Long l, int i, DefaultConstructorMarker defaultConstructorMarker) {
111:             this((i & 1) != 0 ? null : num, (i & 2) != 0 ? null : l);
112:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:114`
```text
112:         }
113: 
114:         public static Retryable copy$default(Retryable retryable, Integer num, Long l, int i, Object obj) {
115:             if ((i & 1) != 0) {
116:                 num = retryable.statusCode;
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:116`
```text
114:         public static Retryable copy$default(Retryable retryable, Integer num, Long l, int i, Object obj) {
115:             if ((i & 1) != 0) {
116:                 num = retryable.statusCode;
117:             }
118:             if ((i & 2) != 0) {
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:119`
```text
117:             }
118:             if ((i & 2) != 0) {
119:                 l = retryable.retryAfterMs;
120:             }
121:             return retryable.copy(num, l);
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:121`
```text
119:                 l = retryable.retryAfterMs;
120:             }
121:             return retryable.copy(num, l);
122:         }
123: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:128`
```text
126:         }
127: 
128:         public final Long getRetryAfterMs() {
129:             return this.retryAfterMs;
130:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:129`
```text
127: 
128:         public final Long getRetryAfterMs() {
129:             return this.retryAfterMs;
130:         }
131: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:132`
```text
130:         }
131: 
132:         public final Retryable copy(Integer statusCode, Long retryAfterMs) {
133:             return new Retryable(statusCode, retryAfterMs);
134:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:133`
```text
131: 
132:         public final Retryable copy(Integer statusCode, Long retryAfterMs) {
133:             return new Retryable(statusCode, retryAfterMs);
134:         }
135: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:140`
```text
138:                 return true;
139:             }
140:             if (!(other instanceof Retryable)) {
141:                 return false;
142:             }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:143`
```text
141:                 return false;
142:             }
143:             Retryable retryable = (Retryable) other;
144:             return wnm.k(this.statusCode, retryable.statusCode) && wnm.k(this.retryAfterMs, retryable.retryAfterMs);
145:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:144`
```text
142:             }
143:             Retryable retryable = (Retryable) other;
144:             return wnm.k(this.statusCode, retryable.statusCode) && wnm.k(this.retryAfterMs, retryable.retryAfterMs);
145:         }
146: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:147`
```text
145:         }
146: 
147:         public final Long getRetryAfterMs() {
148:             return this.retryAfterMs;
149:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:148`
```text
146: 
147:         public final Long getRetryAfterMs() {
148:             return this.retryAfterMs;
149:         }
150: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:158`
```text
156:             Integer num = this.statusCode;
157:             int iHashCode = (num == null ? 0 : num.hashCode()) * 31;
158:             Long l = this.retryAfterMs;
159:             return iHashCode + (l != null ? l.hashCode() : 0);
160:         }
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:163`
```text
161: 
162:         public String toString() {
163:             return "Retryable(statusCode=" + this.statusCode + ", retryAfterMs=" + this.retryAfterMs + ")";
164:         }
165: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:166`
```text
164:         }
165: 
166:         public Retryable(Integer num, Long l) {
167:             this.statusCode = num;
168:             this.retryAfterMs = l;
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:168`
```text
166:         public Retryable(Integer num, Long l) {
167:             this.statusCode = num;
168:             this.retryAfterMs = l;
169:         }
170: 
```

### `sources/com/statsig/androidsdk/EventDeliveryResult.java:171`
```text
169:         }
170: 
171:         public Retryable() {
172:             this(null, 0 == true ? 1 : 0, 3, 0 == true ? 1 : 0);
173:         }
```

### `sources/com/statsig/androidsdk/EventQueueStorage.java:9`
```text
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000T\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0010\t\n\u0002\b\u0005\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\b`\u0018\u00002\u00020\u0001J\u001e\u0010\u0006\u001a\u00020\u00052\f\u0010\u0004\u001a\b\u0012\u000
10: public interface EventQueueStorage {
11:     static Object release$default(EventQueueStorage eventQueueStorage, String str, long j, boolean z, psg psgVar, int i, Object obj) {
```

### `sources/com/statsig/androidsdk/KeyType.java:9`
```text
7: import kotlin.jvm.internal.DefaultConstructorMarker;
8: 
9: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\f\b\u0086\u0081\u0002\u0018\u0000 \f2\b\u0012\u0004\u0012\u00020\u00000\u0001:\u0001\fB\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003j\u0002\b\u0004j\u0002\b\u0005j\u0002\b\u0006j\u0002\b\u0007j\u0002\b\bj\u0002\b\tj\u0002\b\nj\u0002\b\u000b¨\u0006\r"}, d2 = {"Lcom/statsig/androidsdk/KeyType;", "", "<init>", "(Ljava/lang/String;I)V", "INITIALIZE", "BOOTSTRAP", "OVERALL", "CHECK_GATE", "GET_CONFIG", "GET_EXPERIMENT", "GET_LA
10: public enum KeyType {
11:     INITIALIZE,
```

### `sources/com/statsig/androidsdk/KeyType.java:18`
```text
16:     GET_EXPERIMENT,
17:     GET_LAYER,
18:     RETRY_FAILED_LOG;
19: 
20:     private static final gon $ENTRIES = new hon(values());
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:62`
```text
60: import kotlin.jvm.internal.DefaultConstructorMarker;
61: 
62: @Metadata(d1 = {"\u0000î\u0001\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\t\n\u0002\u0010\u000e\n\u0002\b\u0011\n
63: public final class LoggingCoordinator {
64:     private static final long INITIAL_DISK_FULL_RETRY_DELAY_MS = 30000;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:64`
```text
62: @Metadata(d1 = {"\u0000î\u0001\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\t\n\u0002\u0010\u000e\n\u0002\b\u0011\n
63: public final class LoggingCoordinator {
64:     private static final long INITIAL_DISK_FULL_RETRY_DELAY_MS = 30000;
65:     private static final long INITIAL_PERSISTENCE_RETRY_DELAY_MS = 1000;
66:     private static final int MAX_BATCH_BYTES = 524288;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:65`
```text
63: public final class LoggingCoordinator {
64:     private static final long INITIAL_DISK_FULL_RETRY_DELAY_MS = 30000;
65:     private static final long INITIAL_PERSISTENCE_RETRY_DELAY_MS = 1000;
66:     private static final int MAX_BATCH_BYTES = 524288;
67:     private static final int MAX_PENDING_PERSISTENCE_EVENTS = 1000;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:68`
```text
66:     private static final int MAX_BATCH_BYTES = 524288;
67:     private static final int MAX_PENDING_PERSISTENCE_EVENTS = 1000;
68:     private static final long MAX_PERSISTENCE_RETRY_DELAY_MS = 60000;
69:     private static final String TAG = "statsig::LogCoordinator";
70:     private final Object admissionLock;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:84`
```text
82:     private final List<QueuedEvent> pendingEvents;
83:     private int persistenceFailureCount;
84:     private oet persistenceRetryJob;
85:     private Long retryDeadlineMs;
86:     private oet retryJob;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:85`
```text
83:     private int persistenceFailureCount;
84:     private oet persistenceRetryJob;
85:     private Long retryDeadlineMs;
86:     private oet retryJob;
87:     private final rqi scope;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:86`
```text
84:     private oet persistenceRetryJob;
85:     private Long retryDeadlineMs;
86:     private oet retryJob;
87:     private final rqi scope;
88:     private final long startedAtMs;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:93`
```text
91:     private static final Companion Companion = new Companion(null);
92:     private static final long LEASE_DURATION_MS = 120000;
93:     private static final long MAX_RETRY_BACKOFF_MS = 600000;
94: 
95:     @uuj(c = "com.statsig.androidsdk.LoggingCoordinator$1", f = "LoggingCoordinator.kt", l = {}, m = "invokeSuspend", v = 2)
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:298`
```text
296:     }
297: 
298:     @Metadata(d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\b\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\br\u0018\u00002\u00020\u0001:\b\u0002\u0003\u0004\u0005\u0006\u0007\b\t\u0082\u0001\b\n\u000b\f\r\u000e\u000f\u0010\u0011ø\u0001\u0000\u0082\u0002\u0006\n\u0004\b!0\u0001¨\u0006\u0012À\u0006\u0001"}, d2 = {"Lcom/statsig/androidsdk/LoggingCoordinator$C
299:     public interface Command {
300: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:530`
```text
528:         }
529: 
530:         @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0000\bÆ\n\u0018\u00002\u00020\u0001B\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003J\u0014\u0010\u0004\u001a\u00020\u00052\b\u0010\u0006\u001a\u0004\u0018\u00010\u0007HÖ\u0083\u0004J\n\u0010\b\u001a\u00020\tHÖ\u0081\u0004J\n\u0010\n\u001a\u00020\u000bHÖ\u0081\u0004¨\u0006\f"}, d2 = {"Lcom/statsig/androidsdk/Log
531:         public static final class RetryPersistence implements Command {
532:             public static final RetryPersistence INSTANCE = new RetryPersistence();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:531`
```text
529: 
530:         @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0000\bÆ\n\u0018\u00002\u00020\u0001B\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003J\u0014\u0010\u0004\u001a\u00020\u00052\b\u0010\u0006\u001a\u0004\u0018\u00010\u0007HÖ\u0083\u0004J\n\u0010\b\u001a\u00020\tHÖ\u0081\u0004J\n\u0010\n\u001a\u00020\u000bHÖ\u0081\u0004¨\u0006\f"}, d2 = {"Lcom/statsig/androidsdk/Log
531:         public static final class RetryPersistence implements Command {
532:             public static final RetryPersistence INSTANCE = new RetryPersistence();
533: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:532`
```text
530:         @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0000\bÆ\n\u0018\u00002\u00020\u0001B\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003J\u0014\u0010\u0004\u001a\u00020\u00052\b\u0010\u0006\u001a\u0004\u0018\u00010\u0007HÖ\u0083\u0004J\n\u0010\b\u001a\u00020\tHÖ\u0081\u0004J\n\u0010\n\u001a\u00020\u000bHÖ\u0081\u0004¨\u0006\f"}, d2 = {"Lcom/statsig/androidsdk/Log
531:         public static final class RetryPersistence implements Command {
532:             public static final RetryPersistence INSTANCE = new RetryPersistence();
533: 
534:             private RetryPersistence() {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:534`
```text
532:             public static final RetryPersistence INSTANCE = new RetryPersistence();
533: 
534:             private RetryPersistence() {
535:             }
536: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:538`
```text
536: 
537:             public boolean equals(Object other) {
538:                 return this == other || (other instanceof RetryPersistence);
539:             }
540: 
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:546`
```text
544: 
545:             public String toString() {
546:                 return "RetryPersistence";
547:             }
548:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:611`
```text
609:     }
610: 
611:     @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0005\b\u0082\u0081\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001B\t\b\u0002¢\u0006\u0004\b\u0002\u0010\u0003j\u0002\b\u0004j\u0002\b\u0005¨\u0006\u0006"}, d2 = {"Lcom/statsig/androidsdk/LoggingCoordinator$DeliveryOutcome;", "", "<init>", "(Ljava/lang/String;I)V", "PROCESSED", "RETRY_WITH_SMALLER_BATCH", "android-sdk_release"}, k = 1, mv = {2, 3, 0}, xi = 48)
612:     public enum DeliveryOutcome {
613:         PROCESSED,
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:614`
```text
612:     public enum DeliveryOutcome {
613:         PROCESSED,
614:         RETRY_WITH_SMALLER_BATCH;
615: 
616:         private static final gon $ENTRIES = new hon(values());
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:944`
```text
942:     }
943: 
944:     @uuj(c = "com.statsig.androidsdk.LoggingCoordinator$schedulePersistenceRetry$1", f = "LoggingCoordinator.kt", l = {451}, m = "invokeSuspend", v = 2)
945:     @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\u0010\u0002\u001a\u00020\u0001*\u00020\u0000H\n¢\u0006\u0004\b\u0002\u0010\u0003"}, d2 = {"Lrqi;", "Lwec0;", "<anonymous>", "(Lrqi;)V"}, k = 3, mv = {2, 3, 0})
946:     public static final class C00131 extends gw90 implements Function2 {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:986`
```text
984:                 ct40.j(obj);
985:             }
986:             this.this$0.persistenceRetryJob = null;
987:             this.this$0.commands.p(Command.RetryPersistence.INSTANCE);
988:             return wec0.a;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:987`
```text
985:             }
986:             this.this$0.persistenceRetryJob = null;
987:             this.this$0.commands.p(Command.RetryPersistence.INSTANCE);
988:             return wec0.a;
989:         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:992`
```text
990:     }
991: 
992:     @uuj(c = "com.statsig.androidsdk.LoggingCoordinator$scheduleRetry$2", f = "LoggingCoordinator.kt", l = {632, 635}, m = "invokeSuspend", v = 2)
993:     @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\u0010\u0002\u001a\u00020\u0001*\u00020\u0000H\n¢\u0006\u0004\b\u0002\u0010\u0003"}, d2 = {"Lrqi;", "Lwec0;", "<anonymous>", "(Lrqi;)V"}, k = 3, mv = {2, 3, 0})
994:     public static final class AnonymousClass2 extends gw90 implements Function2 {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1040`
```text
1038:             }
1039:             return wec0.a;
1040:             this.this$0.retryJob = null;
1041:             this.this$0.retryDeadlineMs = null;
1042:             cg9 cg9Var = this.this$0.uploadSignals;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1041`
```text
1039:             return wec0.a;
1040:             this.this$0.retryJob = null;
1041:             this.this$0.retryDeadlineMs = null;
1042:             cg9 cg9Var = this.this$0.uploadSignals;
1043:             UploadSignal uploadSignal = new UploadSignal(yqeVar, i2, objArr == true ? 1 : 0);
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1131`
```text
1129:         EventDeliveryResult eventDeliveryResult;
1130:         EventDeliveryResult eventDeliveryResult2;
1131:         EventDeliveryResult.Retryable retryable;
1132:         Integer statusCode;
1133:         Integer statusCode2;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1136`
```text
1134:         int attemptCount;
1135:         long j;
1136:         EventDeliveryResult.Retryable retryable2;
1137:         Long retryAfterMs;
1138:         long jLongValue;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1137`
```text
1135:         long j;
1136:         EventDeliveryResult.Retryable retryable2;
1137:         Long retryAfterMs;
1138:         long jLongValue;
1139:         EventQueueStorage eventQueueStorage;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1197`
```text
1195:                     if (objSend != obj) {
1196:                         eventDeliveryResult = (EventDeliveryResult) objSend;
1197:                         if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1198:                             retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1199:                             if (retryable.getStatusCode() == null) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1198`
```text
1196:                         eventDeliveryResult = (EventDeliveryResult) objSend;
1197:                         if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1198:                             retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1199:                             if (retryable.getStatusCode() == null) {
1200:                             }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1199`
```text
1197:                         if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1198:                             retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1199:                             if (retryable.getStatusCode() == null) {
1200:                             }
1201:                         }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1229`
```text
1227:                             }
1228:                         } else if (wnm.k(eventDeliveryResult2, EventDeliveryResult.PayloadTooLarge.INSTANCE)) {
1229:                             if (eventDeliveryResult2 instanceof EventDeliveryResult.Retryable) {
1230:                                 d7y.b();
1231:                                 return null;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1248`
```text
1246:                                     attemptCount = 10;
1247:                                 }
1248:                                 j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1249:                                 retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1250:                                 retryAfterMs = retryable2.getRetryAfterMs();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1249`
```text
1247:                                 }
1248:                                 j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1249:                                 retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1250:                                 retryAfterMs = retryable2.getRetryAfterMs();
1251:                                 if (retryAfterMs != null) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1250`
```text
1248:                                 j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1249:                                 retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1250:                                 retryAfterMs = retryable2.getRetryAfterMs();
1251:                                 if (retryAfterMs != null) {
1252:                                     jLongValue = retryAfterMs.longValue();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1251`
```text
1249:                                 retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1250:                                 retryAfterMs = retryable2.getRetryAfterMs();
1251:                                 if (retryAfterMs != null) {
1252:                                     jLongValue = retryAfterMs.longValue();
1253:                                 } else {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1252`
```text
1250:                                 retryAfterMs = retryable2.getRetryAfterMs();
1251:                                 if (retryAfterMs != null) {
1252:                                     jLongValue = retryAfterMs.longValue();
1253:                                 } else {
1254:                                     jLongValue = MAX_RETRY_BACKOFF_MS;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1254`
```text
1252:                                     jLongValue = retryAfterMs.longValue();
1253:                                 } else {
1254:                                     jLongValue = MAX_RETRY_BACKOFF_MS;
1255:                                     if (j <= jLongValue) {
1256:                                         jLongValue = j;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1262`
```text
1260:                                 leaseId = leasedBatch2.getLeaseId();
1261:                                 jLongValue2 = ((Number) this.clock.invoke()).longValue() + jLongValue;
1262:                                 if (retryable2.getRetryAfterMs() == null) {
1263:                                     z = false;
1264:                                 }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1276`
```text
1274:                                 if (eventQueueStorage.release(leaseId, jLongValue2, z, c00092) != obj) {
1275:                                     j2 = jLongValue;
1276:                                     scheduleRetry(j2);
1277:                                     return DeliveryOutcome.PROCESSED;
1278:                                 }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1349`
```text
1347:                         if (objSend != obj) {
1348:                             eventDeliveryResult = (EventDeliveryResult) objSend;
1349:                             if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1350:                                 retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1351:                                 if (retryable.getStatusCode() == null && (((statusCode = retryable.getStatusCode()) == null || statusCode.intValue() != 400) && (((statusCode2 = retryable.getStatusCode()) == null || statusCode2.intValue() != 429) && retryable.getRetryAfterMs() == null && leasedBatch2.getAttemptCount() == 1))) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1350`
```text
1348:                             eventDeliveryResult = (EventDeliveryResult) objSend;
1349:                             if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1350:                                 retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1351:                                 if (retryable.getStatusCode() == null && (((statusCode = retryable.getStatusCode()) == null || statusCode.intValue() != 400) && (((statusCode2 = retryable.getStatusCode()) == null || statusCode2.intValue() != 429) && retryable.getRetryAfterMs() == null && leasedBatch2.getAttemptCount() == 1))) {
1352:                                     c00092.L$0 = leasedBatch2;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1351`
```text
1349:                             if (eventDeliveryResult instanceof EventDeliveryResult.Retryable) {
1350:                                 retryable = (EventDeliveryResult.Retryable) eventDeliveryResult;
1351:                                 if (retryable.getStatusCode() == null && (((statusCode = retryable.getStatusCode()) == null || statusCode.intValue() != 400) && (((statusCode2 = retryable.getStatusCode()) == null || statusCode2.intValue() != 429) && retryable.getRetryAfterMs() == null && leasedBatch2.getAttemptCount() == 1))) {
1352:                                     c00092.L$0 = leasedBatch2;
1353:                                     c00092.L$1 = null;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1389`
```text
1387:                                 }
1388:                             } else if (wnm.k(eventDeliveryResult2, EventDeliveryResult.PayloadTooLarge.INSTANCE)) {
1389:                                 if (eventDeliveryResult2 instanceof EventDeliveryResult.Retryable) {
1390:                                     d7y.b();
1391:                                     return null;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1408`
```text
1406:                                         attemptCount = 10;
1407:                                     }
1408:                                     j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1409:                                     retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1410:                                     retryAfterMs = retryable2.getRetryAfterMs();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1409`
```text
1407:                                     }
1408:                                     j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1409:                                     retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1410:                                     retryAfterMs = retryable2.getRetryAfterMs();
1411:                                     if (retryAfterMs != null) {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1410`
```text
1408:                                     j = (1 << attemptCount) * INITIAL_PERSISTENCE_RETRY_DELAY_MS;
1409:                                     retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1410:                                     retryAfterMs = retryable2.getRetryAfterMs();
1411:                                     if (retryAfterMs != null) {
1412:                                         jLongValue = retryAfterMs.longValue();
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1411`
```text
1409:                                     retryable2 = (EventDeliveryResult.Retryable) eventDeliveryResult2;
1410:                                     retryAfterMs = retryable2.getRetryAfterMs();
1411:                                     if (retryAfterMs != null) {
1412:                                         jLongValue = retryAfterMs.longValue();
1413:                                     } else {
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1412`
```text
1410:                                     retryAfterMs = retryable2.getRetryAfterMs();
1411:                                     if (retryAfterMs != null) {
1412:                                         jLongValue = retryAfterMs.longValue();
1413:                                     } else {
1414:                                         jLongValue = MAX_RETRY_BACKOFF_MS;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1414`
```text
1412:                                         jLongValue = retryAfterMs.longValue();
1413:                                     } else {
1414:                                         jLongValue = MAX_RETRY_BACKOFF_MS;
1415:                                         if (j <= jLongValue) {
1416:                                             jLongValue = j;
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1422`
```text
1420:                                     leaseId = leasedBatch2.getLeaseId();
1421:                                     jLongValue2 = ((Number) this.clock.invoke()).longValue() + jLongValue;
1422:                                     if (retryable2.getRetryAfterMs() == null && ((statusCode3 = retryable2.getStatusCode()) == null || statusCode3.intValue() != 429)) {
1423:                                         z = false;
1424:                                     }
```

### `sources/com/statsig/androidsdk/LoggingCoordinator.java:1436`
```text
1434:                                     if (eventQueueStorage.release(leaseId, jLongValue2, z, c00092) != obj) {
1435:                                         j2 = jLongValue;
1436:                                         scheduleRetry(j2);
1437:                                         return DeliveryOutcome.PROCESSED;
1438:                                     }
```

_Hits captured: 180 (cap 180)_

## MODEL_TOOLS

### `sources/androidx/browser/auth/AuthTabIntent$AuthenticateUserResultContract.java:1`
```text
1: package androidx.browser.auth;
2: 
3: import android.content.Context;
```

### `sources/com/datadog/android/rum/internal/domain/scope/RumRawEvent.java:191`
```text
189:                     break;
190:                 case 2:
191:                     str = "BROWSER";
192:                     break;
193:                 case 3:
```

### `sources/com/google/android/gms/internal/mlkit_common/zzmv.java:98`
```text
96:     CLOUD_TEXT_DETECT(122),
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
```

### `sources/com/google/android/gms/internal/mlkit_common/zzmv.java:99`
```text
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
```

### `sources/com/google/android/gms/internal/mlkit_common/zzmv.java:100`
```text
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
102:     CUSTOM_MODEL_CREATE(103),
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzrc.java:98`
```text
96:     CLOUD_TEXT_DETECT(122),
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzrc.java:99`
```text
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
```

### `sources/com/google/android/gms/internal/mlkit_vision_barcode/zzrc.java:100`
```text
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
102:     CUSTOM_MODEL_CREATE(103),
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zzeo.java:243`
```text
241:         HashMap map35 = new HashMap();
242:         map35.put(zzaiVarM35.annotationType(), zzaiVarM35);
243:         zzJ = new iho("cloudWebSearchDetectionLogEvent", yi2.l(map35));
244:         zzai zzaiVarM36 = hve0.m(23);
245:         HashMap map36 = new HashMap();
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zziv.java:98`
```text
96:     CLOUD_TEXT_DETECT(122),
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zziv.java:99`
```text
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
```

### `sources/com/google/android/gms/internal/mlkit_vision_common/zziv.java:100`
```text
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
102:     CUSTOM_MODEL_CREATE(103),
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzgq.java:229`
```text
227:         HashMap map35 = new HashMap();
228:         map35.put(zzcuVarN35.annotationType(), zzcuVarN35);
229:         zzJ = new iho("cloudWebSearchDetectionLogEvent", yi2.l(map35));
230:         zzcu zzcuVarN36 = hve0.n(23);
231:         HashMap map36 = new HashMap();
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzkt.java:98`
```text
96:     CLOUD_TEXT_DETECT(122),
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzkt.java:99`
```text
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
```

### `sources/com/google/android/gms/internal/mlkit_vision_face/zzkt.java:100`
```text
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
102:     CUSTOM_MODEL_CREATE(103),
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzov.java:98`
```text
96:     CLOUD_TEXT_DETECT(122),
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzov.java:99`
```text
97:     CLOUD_TEXT_CLOSE(123),
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
```

### `sources/com/google/android/gms/internal/mlkit_vision_text_common/zzov.java:100`
```text
98:     CLOUD_WEB_SEARCH_CREATE(131),
99:     CLOUD_WEB_SEARCH_DETECT(132),
100:     CLOUD_WEB_SEARCH_CLOSE(133),
101:     CUSTOM_MODEL_RUN(MlKitException.MODEL_HASH_MISMATCH),
102:     CUSTOM_MODEL_CREATE(103),
```

### `sources/com/openai/auth/AuthError.java:7`
```text
5: import org.chromium.net.PrivateKeyType;
6: 
7: @Metadata(d1 = {"\u0000:\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\n\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b7\u0018\u00002\u00060\u0001j\u0002`\u0002:\n\u0003\u0004\u0005\u0006\u0007\b\t\n\u000b\f\u0082\u0001\n\r\u000e\u000f\u0010\u0011\u0012\u0013\u0014\u0015\u0016¨\u0006\u0017"}, d2 = {"Lcom/openai/
8: public abstract class AuthError extends Exception {
9:     public final ju4 a;
```

### `sources/com/openai/auth/AuthError.java:14`
```text
12:     public final int d;
13: 
14:     @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/openai/auth/AuthError$BrowserUnavailable;", "Lcom/openai/auth/AuthError;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
15:     public static final class BrowserUnavailable extends AuthError {
16:         public BrowserUnavailable(ju4 ju4Var) {
```

### `sources/com/openai/auth/AuthError.java:15`
```text
13: 
14:     @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/openai/auth/AuthError$BrowserUnavailable;", "Lcom/openai/auth/AuthError;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
15:     public static final class BrowserUnavailable extends AuthError {
16:         public BrowserUnavailable(ju4 ju4Var) {
17:             super(ju4Var, "browser_unavailable", "AuthError.BrowserUnavailable", 2, null, 16);
```

### `sources/com/openai/auth/AuthError.java:16`
```text
14:     @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/openai/auth/AuthError$BrowserUnavailable;", "Lcom/openai/auth/AuthError;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
15:     public static final class BrowserUnavailable extends AuthError {
16:         public BrowserUnavailable(ju4 ju4Var) {
17:             super(ju4Var, "browser_unavailable", "AuthError.BrowserUnavailable", 2, null, 16);
18:         }
```

### `sources/com/openai/auth/AuthError.java:17`
```text
15:     public static final class BrowserUnavailable extends AuthError {
16:         public BrowserUnavailable(ju4 ju4Var) {
17:             super(ju4Var, "browser_unavailable", "AuthError.BrowserUnavailable", 2, null, 16);
18:         }
19:     }
```

### `sources/com/openai/chatgpt/R.java:138`
```text
136:         public static final int actionModeStyle = 0x7f04001f;
137:         public static final int actionModeTheme = 0x7f040020;
138:         public static final int actionModeWebSearchDrawable = 0x7f040021;
139:         public static final int actionOverflowButtonStyle = 0x7f040022;
140:         public static final int actionOverflowMenuStyle = 0x7f040023;
```

### `sources/com/openai/chatgpt/R.java:2821`
```text
2819:         public static final int pay_button_generic_text_size = 0x7f07045c;
2820:         public static final int pay_button_generic_text_start_end_padding = 0x7f07045d;
2821:         public static final int pay_image_generic_height = 0x7f07045e;
2822:         public static final int pay_image_generic_width = 0x7f07045f;
2823:         public static final int photo_viewer_attribution_open_now_button_margin_start = 0x7f070460;
```

### `sources/com/openai/chatgpt/R.java:2822`
```text
2820:         public static final int pay_button_generic_text_start_end_padding = 0x7f07045d;
2821:         public static final int pay_image_generic_height = 0x7f07045e;
2822:         public static final int pay_image_generic_width = 0x7f07045f;
2823:         public static final int photo_viewer_attribution_open_now_button_margin_start = 0x7f070460;
2824:         public static final int photo_viewer_attribution_open_now_button_size = 0x7f070461;
```

### `sources/com/openai/chatgpt/R.java:3097`
```text
3095:         public static final int close_lg = 0x7f080119;
3096:         public static final int close_xs = 0x7f08011a;
3097:         public static final int cloud_browser_use = 0x7f08011b;
3098:         public static final int cloud_foggy = 0x7f08011c;
3099:         public static final int cloudy = 0x7f08011d;
```

### `sources/com/openai/chatgpt/R.java:3111`
```text
3109:         public static final int compose = 0x7f08013b;
3110:         public static final int confetti = 0x7f08013c;
3111:         public static final int connector_promo = 0x7f08013e;
3112:         public static final int connectors = 0x7f08013f;
3113:         public static final int copy = 0x7f080140;
```

### `sources/com/openai/chatgpt/R.java:3112`
```text
3110:         public static final int confetti = 0x7f08013c;
3111:         public static final int connector_promo = 0x7f08013e;
3112:         public static final int connectors = 0x7f08013f;
3113:         public static final int copy = 0x7f080140;
3114:         public static final int credit_card = 0x7f080141;
```

### `sources/com/openai/chatgpt/R.java:3298`
```text
3296:         public static final int identity = 0x7f08026a;
3297:         public static final int image_gallery = 0x7f08026b;
3298:         public static final int image_gen = 0x7f08026c;
3299:         public static final int image_lightbox_comment_marker_background = 0x7f08026d;
3300:         public static final int image_lightbox_comment_marker_outline = 0x7f08026e;
```

### `sources/com/openai/chatgpt/R.java:3948`
```text
3946:         public static final int writing = 0x7f080585;
3947:         public static final int writing_2 = 0x7f080586;
3948:         public static final int writing_block_email_connector_upsell = 0x7f080587;
3949:         public static final int x = 0x7f080588;
3950:         public static final int xmark_circle_filled = 0x7f080589;
```

### `sources/com/openai/chatgpt/R.java:4173`
```text
4171:         public static final int brand_logo = 0x7f0b00ce;
4172:         public static final int brand_text = 0x7f0b00cf;
4173:         public static final int browser_actions_header_text = 0x7f0b00d0;
4174:         public static final int browser_actions_menu_item_icon = 0x7f0b00d1;
4175:         public static final int browser_actions_menu_item_text = 0x7f0b00d2;
```

### `sources/com/openai/chatgpt/R.java:4174`
```text
4172:         public static final int brand_text = 0x7f0b00cf;
4173:         public static final int browser_actions_header_text = 0x7f0b00d0;
4174:         public static final int browser_actions_menu_item_icon = 0x7f0b00d1;
4175:         public static final int browser_actions_menu_item_text = 0x7f0b00d2;
4176:         public static final int browser_actions_menu_items = 0x7f0b00d3;
```

### `sources/com/openai/chatgpt/R.java:4175`
```text
4173:         public static final int browser_actions_header_text = 0x7f0b00d0;
4174:         public static final int browser_actions_menu_item_icon = 0x7f0b00d1;
4175:         public static final int browser_actions_menu_item_text = 0x7f0b00d2;
4176:         public static final int browser_actions_menu_items = 0x7f0b00d3;
4177:         public static final int browser_actions_menu_view = 0x7f0b00d4;
```

### `sources/com/openai/chatgpt/R.java:4176`
```text
4174:         public static final int browser_actions_menu_item_icon = 0x7f0b00d1;
4175:         public static final int browser_actions_menu_item_text = 0x7f0b00d2;
4176:         public static final int browser_actions_menu_items = 0x7f0b00d3;
4177:         public static final int browser_actions_menu_view = 0x7f0b00d4;
4178:         public static final int bsb_edit_text = 0x7f0b00d5;
```

### `sources/com/openai/chatgpt/R.java:4177`
```text
4175:         public static final int browser_actions_menu_item_text = 0x7f0b00d2;
4176:         public static final int browser_actions_menu_items = 0x7f0b00d3;
4177:         public static final int browser_actions_menu_view = 0x7f0b00d4;
4178:         public static final int bsb_edit_text = 0x7f0b00d5;
4179:         public static final int bsb_text_input_layout = 0x7f0b00d6;
```

### `sources/com/openai/chatgpt/R.java:4354`
```text
4352:         public static final int confirmed_icon = 0x7f0b0183;
4353:         public static final int confirming_icon = 0x7f0b0184;
4354:         public static final int connector_name = 0x7f0b0185;
4355:         public static final int constraint = 0x7f0b0186;
4356:         public static final int consume_window_insets_tag = 0x7f0b0187;
```

### `sources/com/openai/chatgpt/R.java:4862`
```text
4860:         public static final int noScroll = 0x7f0b037f;
4861:         public static final int noState = 0x7f0b0380;
4862:         public static final int no_browser_error_ok = 0x7f0b0381;
4863:         public static final int none = 0x7f0b0382;
4864:         public static final int normal = 0x7f0b0383;
```

### `sources/com/openai/chatgpt/R.java:6186`
```text
6184:         public static final int mtrl_layout_snackbar = 0x7f0e02c0;
6185:         public static final int mtrl_layout_snackbar_include = 0x7f0e02c1;
6186:         public static final int no_gmm_or_browser_dialog = 0x7f0e02cf;
6187:         public static final int pay_button_pix_static = 0x7f0e02d7;
6188:         public static final int paybutton_generic = 0x7f0e02d8;
```

### `sources/com/openai/chatgpt/R.java:6931`
```text
6929:         public static final int codex_tool_call_ran_commands_continuation = 0x7f120036;
6930:         public static final int codex_tool_call_searched_web_queries = 0x7f120037;
6931:         public static final int connectors_email_verification_dialog_time_remaining_content_description = 0x7f120038;
6932:         public static final int conversation_file_upload_message_attachment_limit_description = 0x7f120039;
6933:         public static final int conversation_file_upload_message_attachment_limit_reached = 0x7f12003a;
```

### `sources/com/openai/chatgpt/R.java:6947`
```text
6945:         public static final int image_download_series_error = 0x7f120046;
6946:         public static final int image_download_series_success = 0x7f120047;
6947:         public static final int image_gen_tool_summarizer_display_text_progress_creating = 0x7f120048;
6948:         public static final int image_gen_tool_summarizer_display_text_progress_creating_detail = 0x7f120049;
6949:         public static final int image_gen_tool_summarizer_display_text_progress_creating_final = 0x7f12004a;
```

### `sources/com/openai/chatgpt/R.java:6948`
```text
6946:         public static final int image_download_series_success = 0x7f120047;
6947:         public static final int image_gen_tool_summarizer_display_text_progress_creating = 0x7f120048;
6948:         public static final int image_gen_tool_summarizer_display_text_progress_creating_detail = 0x7f120049;
6949:         public static final int image_gen_tool_summarizer_display_text_progress_creating_final = 0x7f12004a;
6950:         public static final int image_share_menu_series = 0x7f12004b;
```

### `sources/com/openai/chatgpt/R.java:6949`
```text
6947:         public static final int image_gen_tool_summarizer_display_text_progress_creating = 0x7f120048;
6948:         public static final int image_gen_tool_summarizer_display_text_progress_creating_detail = 0x7f120049;
6949:         public static final int image_gen_tool_summarizer_display_text_progress_creating_final = 0x7f12004a;
6950:         public static final int image_share_menu_series = 0x7f12004b;
6951:         public static final int locked_conversations_pin_retry_minutes = 0x7f12004c;
```

### `sources/com/openai/chatgpt/R.java:6987`
```text
6985:         public static final int horizon_orb_frag = 0x7f13000e;
6986:         public static final int horizon_orb_vert = 0x7f13000f;
6987:         public static final int image_gen_animals = 0x7f130010;
6988:         public static final int listening_start_0db = 0x7f130012;
6989:         public static final int listening_start_instant_0db = 0x7f130013;
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:10`
```text
8: import android.os.Looper;
9: import androidx.activity.result.contract.ActivityResultContracts$StartActivityForResult;
10: import androidx.browser.auth.AuthTabIntent$AuthenticateUserResultContract;
11: import com.openai.feature.auth.impl.web.WebAuthenticationActivity;
12: import defpackage.bu;
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:301`
```text
299:             this.z = null;
300:             this.A = null;
301:             gev.f(this.s, "Could not connect to the browser service; opening a Custom Tab", e, null, 12);
302:             k(n7f0Var, null);
303:         }
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:318`
```text
316:                 unbindService(w6f0Var);
317:             } catch (IllegalArgumentException e) {
318:                 gev.a(this.s, "Browser service was already disconnected", e, null, 12);
319:             }
320:             this.z = null;
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:383`
```text
381:             this.u.b(((Intent) v9jVar.a().b).setData(n7f0Var.a), null);
382:         } catch (ActivityNotFoundException e) {
383:             gev.f(gevVar, "The selected browser could not be opened", e, null, 12);
384:             j();
385:         } catch (SecurityException e2) {
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:386`
```text
384:             j();
385:         } catch (SecurityException e2) {
386:             gev.f(gevVar, "The selected browser could not be opened", e2, null, 12);
387:             j();
388:         }
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:401`
```text
399:         this.r = (q6f0) ug3VarM.m1.invoke();
400:         boolean z = false;
401:         if (bundle != null && bundle.getBoolean("browser_launched")) {
402:             z = true;
403:         }
```

### `sources/com/openai/feature/auth/impl/web/WebAuthenticationActivity.java:469`
```text
467:     public final void onSaveInstanceState(Bundle bundle) {
468:         super.onSaveInstanceState(bundle);
469:         bundle.putBoolean("browser_launched", this.w);
470:     }
471: }
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationHost.java:11`
```text
9: import kotlin.Metadata;
10: 
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u001d\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0006\u0010\u0007J\u000f\u0010\t\u001a\u00020\bH&¢\u0006\u0004\b\t\u0010\nJ\u0017\u0010\u000e\u001a\u00020
12: @t5d0(propertyReplacements = "", proxyClass = ovo.class, schema = "'authorizeFinancesConnector':f|m|(r:'[0]'): p<r<e>:'[1]'>,'cancelFinancesConnectorAuthorization':f|m|()", typeReferences = {OAIAPIService.class, FinanceConnectorAuthorizationOutcome.class})
13: public interface FinanceConnectorAuthorizationHost extends ValdiMarshallable {
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationHost.java:12`
```text
10: 
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u001d\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0006\u0010\u0007J\u000f\u0010\t\u001a\u00020\bH&¢\u0006\u0004\b\t\u0010\nJ\u0017\u0010\u000e\u001a\u00020
12: @t5d0(propertyReplacements = "", proxyClass = ovo.class, schema = "'authorizeFinancesConnector':f|m|(r:'[0]'): p<r<e>:'[1]'>,'cancelFinancesConnectorAuthorization':f|m|()", typeReferences = {OAIAPIService.class, FinanceConnectorAuthorizationOutcome.class})
13: public interface FinanceConnectorAuthorizationHost extends ValdiMarshallable {
14:     Promise<FinanceConnectorAuthorizationOutcome> authorizeFinancesConnector(OAIAPIService apiService);
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationHost.java:13`
```text
11: @Metadata(d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u001d\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0006\u0010\u0007J\u000f\u0010\t\u001a\u00020\bH&¢\u0006\u0004\b\t\u0010\nJ\u0017\u0010\u000e\u001a\u00020
12: @t5d0(propertyReplacements = "", proxyClass = ovo.class, schema = "'authorizeFinancesConnector':f|m|(r:'[0]'): p<r<e>:'[1]'>,'cancelFinancesConnectorAuthorization':f|m|()", typeReferences = {OAIAPIService.class, FinanceConnectorAuthorizationOutcome.class})
13: public interface FinanceConnectorAuthorizationHost extends ValdiMarshallable {
14:     Promise<FinanceConnectorAuthorizationOutcome> authorizeFinancesConnector(OAIAPIService apiService);
15: 
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationHost.java:14`
```text
12: @t5d0(propertyReplacements = "", proxyClass = ovo.class, schema = "'authorizeFinancesConnector':f|m|(r:'[0]'): p<r<e>:'[1]'>,'cancelFinancesConnectorAuthorization':f|m|()", typeReferences = {OAIAPIService.class, FinanceConnectorAuthorizationOutcome.class})
13: public interface FinanceConnectorAuthorizationHost extends ValdiMarshallable {
14:     Promise<FinanceConnectorAuthorizationOutcome> authorizeFinancesConnector(OAIAPIService apiService);
15: 
16:     void cancelFinancesConnectorAuthorization();
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationHost.java:16`
```text
14:     Promise<FinanceConnectorAuthorizationOutcome> authorizeFinancesConnector(OAIAPIService apiService);
15: 
16:     void cancelFinancesConnectorAuthorization();
17: 
18:     @Override
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Authorized':0,'Cancelled':1,'Failed':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome;", "", "Authorized", "Cancelled", "Failed", "modules_chatgpt_finance_connections-chatgpt_finance_connections_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FinanceConnectorAuthorizationOutcome {
10:     public static final FinanceConnectorAuthorizationOutcome Authorized;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:9`
```text
7: @q4d0(propertyReplacements = "", schema = "'Authorized':0,'Cancelled':1,'Failed':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome;", "", "Authorized", "Cancelled", "Failed", "modules_chatgpt_finance_connections-chatgpt_finance_connections_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FinanceConnectorAuthorizationOutcome {
10:     public static final FinanceConnectorAuthorizationOutcome Authorized;
11:     public static final FinanceConnectorAuthorizationOutcome Cancelled;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome;", "", "Authorized", "Cancelled", "Failed", "modules_chatgpt_finance_connections-chatgpt_finance_connections_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class FinanceConnectorAuthorizationOutcome {
10:     public static final FinanceConnectorAuthorizationOutcome Authorized;
11:     public static final FinanceConnectorAuthorizationOutcome Cancelled;
12:     public static final FinanceConnectorAuthorizationOutcome Failed;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:11`
```text
9: public final class FinanceConnectorAuthorizationOutcome {
10:     public static final FinanceConnectorAuthorizationOutcome Authorized;
11:     public static final FinanceConnectorAuthorizationOutcome Cancelled;
12:     public static final FinanceConnectorAuthorizationOutcome Failed;
13:     public static final FinanceConnectorAuthorizationOutcome[] a;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:12`
```text
10:     public static final FinanceConnectorAuthorizationOutcome Authorized;
11:     public static final FinanceConnectorAuthorizationOutcome Cancelled;
12:     public static final FinanceConnectorAuthorizationOutcome Failed;
13:     public static final FinanceConnectorAuthorizationOutcome[] a;
14: 
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:13`
```text
11:     public static final FinanceConnectorAuthorizationOutcome Cancelled;
12:     public static final FinanceConnectorAuthorizationOutcome Failed;
13:     public static final FinanceConnectorAuthorizationOutcome[] a;
14: 
15:     static {
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:16`
```text
14: 
15:     static {
16:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome = new FinanceConnectorAuthorizationOutcome("Authorized", 0);
17:         Authorized = financeConnectorAuthorizationOutcome;
18:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome2 = new FinanceConnectorAuthorizationOutcome("Cancelled", 1);
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:17`
```text
15:     static {
16:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome = new FinanceConnectorAuthorizationOutcome("Authorized", 0);
17:         Authorized = financeConnectorAuthorizationOutcome;
18:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome2 = new FinanceConnectorAuthorizationOutcome("Cancelled", 1);
19:         Cancelled = financeConnectorAuthorizationOutcome2;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:18`
```text
16:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome = new FinanceConnectorAuthorizationOutcome("Authorized", 0);
17:         Authorized = financeConnectorAuthorizationOutcome;
18:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome2 = new FinanceConnectorAuthorizationOutcome("Cancelled", 1);
19:         Cancelled = financeConnectorAuthorizationOutcome2;
20:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome3 = new FinanceConnectorAuthorizationOutcome("Failed", 2);
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:19`
```text
17:         Authorized = financeConnectorAuthorizationOutcome;
18:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome2 = new FinanceConnectorAuthorizationOutcome("Cancelled", 1);
19:         Cancelled = financeConnectorAuthorizationOutcome2;
20:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome3 = new FinanceConnectorAuthorizationOutcome("Failed", 2);
21:         Failed = financeConnectorAuthorizationOutcome3;
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:20`
```text
18:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome2 = new FinanceConnectorAuthorizationOutcome("Cancelled", 1);
19:         Cancelled = financeConnectorAuthorizationOutcome2;
20:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome3 = new FinanceConnectorAuthorizationOutcome("Failed", 2);
21:         Failed = financeConnectorAuthorizationOutcome3;
22:         a = new FinanceConnectorAuthorizationOutcome[]{financeConnectorAuthorizationOutcome, financeConnectorAuthorizationOutcome2, financeConnectorAuthorizationOutcome3};
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:21`
```text
19:         Cancelled = financeConnectorAuthorizationOutcome2;
20:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome3 = new FinanceConnectorAuthorizationOutcome("Failed", 2);
21:         Failed = financeConnectorAuthorizationOutcome3;
22:         a = new FinanceConnectorAuthorizationOutcome[]{financeConnectorAuthorizationOutcome, financeConnectorAuthorizationOutcome2, financeConnectorAuthorizationOutcome3};
23:     }
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:22`
```text
20:         FinanceConnectorAuthorizationOutcome financeConnectorAuthorizationOutcome3 = new FinanceConnectorAuthorizationOutcome("Failed", 2);
21:         Failed = financeConnectorAuthorizationOutcome3;
22:         a = new FinanceConnectorAuthorizationOutcome[]{financeConnectorAuthorizationOutcome, financeConnectorAuthorizationOutcome2, financeConnectorAuthorizationOutcome3};
23:     }
24: 
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:25`
```text
23:     }
24: 
25:     public static FinanceConnectorAuthorizationOutcome valueOf(String str) {
26:         return (FinanceConnectorAuthorizationOutcome) Enum.valueOf(FinanceConnectorAuthorizationOutcome.class, str);
27:     }
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:26`
```text
24: 
25:     public static FinanceConnectorAuthorizationOutcome valueOf(String str) {
26:         return (FinanceConnectorAuthorizationOutcome) Enum.valueOf(FinanceConnectorAuthorizationOutcome.class, str);
27:     }
28: 
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:29`
```text
27:     }
28: 
29:     public static FinanceConnectorAuthorizationOutcome[] values() {
30:         return (FinanceConnectorAuthorizationOutcome[]) a.clone();
31:     }
```

### `sources/com/openai/valdi/chatgpt/finance/connections/FinanceConnectorAuthorizationOutcome.java:30`
```text
28: 
29:     public static FinanceConnectorAuthorizationOutcome[] values() {
30:         return (FinanceConnectorAuthorizationOutcome[]) a.clone();
31:     }
32: }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import com.snap.valdi.utils.b;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:8`
```text
6: import kotlin.Metadata;
7: 
8: @o2d0(propertyReplacements = "", schema = "'id':s,'kind':r<e>:'[0]','texts':a<s>,'toolIcons':a<s>", typeReferences = {ChatGPTReasoningActiveKind.class})
9: @Metadata(d1 = {"\u0000\u001c\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004\u0012\f\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006¢\u0006\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e
10: public final class ChatGPTReasoningActiveItem extends b {
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:9`
```text
7: 
8: @o2d0(propertyReplacements = "", schema = "'id':s,'kind':r<e>:'[0]','texts':a<s>,'toolIcons':a<s>", typeReferences = {ChatGPTReasoningActiveKind.class})
9: @Metadata(d1 = {"\u0000\u001c\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004\u0012\f\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006¢\u0006\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e
10: public final class ChatGPTReasoningActiveItem extends b {
11:     private String _id;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:10`
```text
8: @o2d0(propertyReplacements = "", schema = "'id':s,'kind':r<e>:'[0]','texts':a<s>,'toolIcons':a<s>", typeReferences = {ChatGPTReasoningActiveKind.class})
9: @Metadata(d1 = {"\u0000\u001c\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004\u0012\f\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00020\u0006¢\u0006\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e
10: public final class ChatGPTReasoningActiveItem extends b {
11:     private String _id;
12:     private ChatGPTReasoningActiveKind _kind;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:12`
```text
10: public final class ChatGPTReasoningActiveItem extends b {
11:     private String _id;
12:     private ChatGPTReasoningActiveKind _kind;
13:     private List<String> _texts;
14:     private List<String> _toolIcons;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:16`
```text
14:     private List<String> _toolIcons;
15: 
16:     public ChatGPTReasoningActiveItem(String str, ChatGPTReasoningActiveKind chatGPTReasoningActiveKind, List<String> list, List<String> list2) {
17:         this._id = str;
18:         this._kind = chatGPTReasoningActiveKind;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveItem.java:18`
```text
16:     public ChatGPTReasoningActiveItem(String str, ChatGPTReasoningActiveKind chatGPTReasoningActiveKind, List<String> list, List<String> list2) {
17:         this._id = str;
18:         this._kind = chatGPTReasoningActiveKind;
19:         this._texts = list;
20:         this._toolIcons = list2;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import defpackage.q4d0;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Activity':0,'Placeholder':1,'Thought':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind;", "", "Activity", "Placeholder", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningActiveKind {
10:     public static final ChatGPTReasoningActiveKind Activity;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:9`
```text
7: @q4d0(propertyReplacements = "", schema = "'Activity':0,'Placeholder':1,'Thought':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind;", "", "Activity", "Placeholder", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningActiveKind {
10:     public static final ChatGPTReasoningActiveKind Activity;
11:     public static final ChatGPTReasoningActiveKind Placeholder;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind;", "", "Activity", "Placeholder", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningActiveKind {
10:     public static final ChatGPTReasoningActiveKind Activity;
11:     public static final ChatGPTReasoningActiveKind Placeholder;
12:     public static final ChatGPTReasoningActiveKind Thought;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:11`
```text
9: public final class ChatGPTReasoningActiveKind {
10:     public static final ChatGPTReasoningActiveKind Activity;
11:     public static final ChatGPTReasoningActiveKind Placeholder;
12:     public static final ChatGPTReasoningActiveKind Thought;
13:     public static final ChatGPTReasoningActiveKind[] a;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:12`
```text
10:     public static final ChatGPTReasoningActiveKind Activity;
11:     public static final ChatGPTReasoningActiveKind Placeholder;
12:     public static final ChatGPTReasoningActiveKind Thought;
13:     public static final ChatGPTReasoningActiveKind[] a;
14: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:13`
```text
11:     public static final ChatGPTReasoningActiveKind Placeholder;
12:     public static final ChatGPTReasoningActiveKind Thought;
13:     public static final ChatGPTReasoningActiveKind[] a;
14: 
15:     static {
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:16`
```text
14: 
15:     static {
16:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind = new ChatGPTReasoningActiveKind("Activity", 0);
17:         Activity = chatGPTReasoningActiveKind;
18:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind2 = new ChatGPTReasoningActiveKind("Placeholder", 1);
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:17`
```text
15:     static {
16:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind = new ChatGPTReasoningActiveKind("Activity", 0);
17:         Activity = chatGPTReasoningActiveKind;
18:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind2 = new ChatGPTReasoningActiveKind("Placeholder", 1);
19:         Placeholder = chatGPTReasoningActiveKind2;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:18`
```text
16:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind = new ChatGPTReasoningActiveKind("Activity", 0);
17:         Activity = chatGPTReasoningActiveKind;
18:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind2 = new ChatGPTReasoningActiveKind("Placeholder", 1);
19:         Placeholder = chatGPTReasoningActiveKind2;
20:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind3 = new ChatGPTReasoningActiveKind("Thought", 2);
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:19`
```text
17:         Activity = chatGPTReasoningActiveKind;
18:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind2 = new ChatGPTReasoningActiveKind("Placeholder", 1);
19:         Placeholder = chatGPTReasoningActiveKind2;
20:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind3 = new ChatGPTReasoningActiveKind("Thought", 2);
21:         Thought = chatGPTReasoningActiveKind3;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:20`
```text
18:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind2 = new ChatGPTReasoningActiveKind("Placeholder", 1);
19:         Placeholder = chatGPTReasoningActiveKind2;
20:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind3 = new ChatGPTReasoningActiveKind("Thought", 2);
21:         Thought = chatGPTReasoningActiveKind3;
22:         a = new ChatGPTReasoningActiveKind[]{chatGPTReasoningActiveKind, chatGPTReasoningActiveKind2, chatGPTReasoningActiveKind3};
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:21`
```text
19:         Placeholder = chatGPTReasoningActiveKind2;
20:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind3 = new ChatGPTReasoningActiveKind("Thought", 2);
21:         Thought = chatGPTReasoningActiveKind3;
22:         a = new ChatGPTReasoningActiveKind[]{chatGPTReasoningActiveKind, chatGPTReasoningActiveKind2, chatGPTReasoningActiveKind3};
23:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:22`
```text
20:         ChatGPTReasoningActiveKind chatGPTReasoningActiveKind3 = new ChatGPTReasoningActiveKind("Thought", 2);
21:         Thought = chatGPTReasoningActiveKind3;
22:         a = new ChatGPTReasoningActiveKind[]{chatGPTReasoningActiveKind, chatGPTReasoningActiveKind2, chatGPTReasoningActiveKind3};
23:     }
24: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:25`
```text
23:     }
24: 
25:     public static ChatGPTReasoningActiveKind valueOf(String str) {
26:         return (ChatGPTReasoningActiveKind) Enum.valueOf(ChatGPTReasoningActiveKind.class, str);
27:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:26`
```text
24: 
25:     public static ChatGPTReasoningActiveKind valueOf(String str) {
26:         return (ChatGPTReasoningActiveKind) Enum.valueOf(ChatGPTReasoningActiveKind.class, str);
27:     }
28: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:29`
```text
27:     }
28: 
29:     public static ChatGPTReasoningActiveKind[] values() {
30:         return (ChatGPTReasoningActiveKind[]) a.clone();
31:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningActiveKind.java:30`
```text
28: 
29:     public static ChatGPTReasoningActiveKind[] values() {
30:         return (ChatGPTReasoningActiveKind[]) a.clone();
31:     }
32: }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import android.content.Context;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:12`
```text
10: import kotlin.jvm.functions.Function1;
11: 
12: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\u0018\u0000 \b2\u000e\u0012\u0004\u0012\u00020\u0002\u0012\u0004\u0012\u00020\u00030\u0001:\u0001\tB\u000f\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent;", "Lcom/snap/valdi/views/ValdiGeneratedRootView;", "Lim9;", "", "Landroid/content/Context
13: public final class ChatGPTReasoningComponent extends ValdiGeneratedRootView<im9, Object> {
14:     public static final gm9 Companion = new gm9();
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:13`
```text
11: 
12: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\u0018\u0000 \b2\u000e\u0012\u0004\u0012\u00020\u0002\u0012\u0004\u0012\u00020\u00030\u0001:\u0001\tB\u000f\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent;", "Lcom/snap/valdi/views/ValdiGeneratedRootView;", "Lim9;", "", "Landroid/content/Context
13: public final class ChatGPTReasoningComponent extends ValdiGeneratedRootView<im9, Object> {
14:     public static final gm9 Companion = new gm9();
15: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:16`
```text
14:     public static final gm9 Companion = new gm9();
15: 
16:     public ChatGPTReasoningComponent(Context context) {
17:         super(context);
18:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:21`
```text
19: 
20:     public static final String access$getComponentPath$cp() {
21:         return "ChatGPTReasoningComponent@chatgpt_reasoning/src/ChatGPTReasoningComponent";
22:     }
23: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:24`
```text
22:     }
23: 
24:     public static final ChatGPTReasoningComponent create(rir rirVar, wbd0 wbd0Var) {
25:         Companion.getClass();
26:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:26`
```text
24:     public static final ChatGPTReasoningComponent create(rir rirVar, wbd0 wbd0Var) {
25:         Companion.getClass();
26:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
27:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), null, null, null);
28:         return chatGPTReasoningComponent;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:27`
```text
25:         Companion.getClass();
26:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
27:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), null, null, null);
28:         return chatGPTReasoningComponent;
29:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:28`
```text
26:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
27:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), null, null, null);
28:         return chatGPTReasoningComponent;
29:     }
30: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:31`
```text
29:     }
30: 
31:     public static final ChatGPTReasoningComponent create(rir rirVar, im9 im9Var, Object obj, wbd0 wbd0Var, Function1 function1) {
32:         Companion.getClass();
33:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:33`
```text
31:     public static final ChatGPTReasoningComponent create(rir rirVar, im9 im9Var, Object obj, wbd0 wbd0Var, Function1 function1) {
32:         Companion.getClass();
33:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
34:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), im9Var, obj, function1);
35:         return chatGPTReasoningComponent;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:34`
```text
32:         Companion.getClass();
33:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
34:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), im9Var, obj, function1);
35:         return chatGPTReasoningComponent;
36:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningComponent.java:35`
```text
33:         ChatGPTReasoningComponent chatGPTReasoningComponent = new ChatGPTReasoningComponent(rirVar.getContext());
34:         rirVar.s(chatGPTReasoningComponent, access$getComponentPath$cp(), im9Var, obj, function1);
35:         return chatGPTReasoningComponent;
36:     }
37: }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import defpackage.q4d0;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Activity':0,'Preamble':1,'Thought':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind;", "", "Activity", "Preamble", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningItemKind {
10:     public static final ChatGPTReasoningItemKind Activity;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:9`
```text
7: @q4d0(propertyReplacements = "", schema = "'Activity':0,'Preamble':1,'Thought':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind;", "", "Activity", "Preamble", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningItemKind {
10:     public static final ChatGPTReasoningItemKind Activity;
11:     public static final ChatGPTReasoningItemKind Preamble;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind;", "", "Activity", "Preamble", "Thought", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningItemKind {
10:     public static final ChatGPTReasoningItemKind Activity;
11:     public static final ChatGPTReasoningItemKind Preamble;
12:     public static final ChatGPTReasoningItemKind Thought;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:11`
```text
9: public final class ChatGPTReasoningItemKind {
10:     public static final ChatGPTReasoningItemKind Activity;
11:     public static final ChatGPTReasoningItemKind Preamble;
12:     public static final ChatGPTReasoningItemKind Thought;
13:     public static final ChatGPTReasoningItemKind[] a;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:12`
```text
10:     public static final ChatGPTReasoningItemKind Activity;
11:     public static final ChatGPTReasoningItemKind Preamble;
12:     public static final ChatGPTReasoningItemKind Thought;
13:     public static final ChatGPTReasoningItemKind[] a;
14: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:13`
```text
11:     public static final ChatGPTReasoningItemKind Preamble;
12:     public static final ChatGPTReasoningItemKind Thought;
13:     public static final ChatGPTReasoningItemKind[] a;
14: 
15:     static {
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:16`
```text
14: 
15:     static {
16:         ChatGPTReasoningItemKind chatGPTReasoningItemKind = new ChatGPTReasoningItemKind("Activity", 0);
17:         Activity = chatGPTReasoningItemKind;
18:         ChatGPTReasoningItemKind chatGPTReasoningItemKind2 = new ChatGPTReasoningItemKind("Preamble", 1);
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:17`
```text
15:     static {
16:         ChatGPTReasoningItemKind chatGPTReasoningItemKind = new ChatGPTReasoningItemKind("Activity", 0);
17:         Activity = chatGPTReasoningItemKind;
18:         ChatGPTReasoningItemKind chatGPTReasoningItemKind2 = new ChatGPTReasoningItemKind("Preamble", 1);
19:         Preamble = chatGPTReasoningItemKind2;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:18`
```text
16:         ChatGPTReasoningItemKind chatGPTReasoningItemKind = new ChatGPTReasoningItemKind("Activity", 0);
17:         Activity = chatGPTReasoningItemKind;
18:         ChatGPTReasoningItemKind chatGPTReasoningItemKind2 = new ChatGPTReasoningItemKind("Preamble", 1);
19:         Preamble = chatGPTReasoningItemKind2;
20:         ChatGPTReasoningItemKind chatGPTReasoningItemKind3 = new ChatGPTReasoningItemKind("Thought", 2);
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:19`
```text
17:         Activity = chatGPTReasoningItemKind;
18:         ChatGPTReasoningItemKind chatGPTReasoningItemKind2 = new ChatGPTReasoningItemKind("Preamble", 1);
19:         Preamble = chatGPTReasoningItemKind2;
20:         ChatGPTReasoningItemKind chatGPTReasoningItemKind3 = new ChatGPTReasoningItemKind("Thought", 2);
21:         Thought = chatGPTReasoningItemKind3;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:20`
```text
18:         ChatGPTReasoningItemKind chatGPTReasoningItemKind2 = new ChatGPTReasoningItemKind("Preamble", 1);
19:         Preamble = chatGPTReasoningItemKind2;
20:         ChatGPTReasoningItemKind chatGPTReasoningItemKind3 = new ChatGPTReasoningItemKind("Thought", 2);
21:         Thought = chatGPTReasoningItemKind3;
22:         a = new ChatGPTReasoningItemKind[]{chatGPTReasoningItemKind, chatGPTReasoningItemKind2, chatGPTReasoningItemKind3};
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:21`
```text
19:         Preamble = chatGPTReasoningItemKind2;
20:         ChatGPTReasoningItemKind chatGPTReasoningItemKind3 = new ChatGPTReasoningItemKind("Thought", 2);
21:         Thought = chatGPTReasoningItemKind3;
22:         a = new ChatGPTReasoningItemKind[]{chatGPTReasoningItemKind, chatGPTReasoningItemKind2, chatGPTReasoningItemKind3};
23:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:22`
```text
20:         ChatGPTReasoningItemKind chatGPTReasoningItemKind3 = new ChatGPTReasoningItemKind("Thought", 2);
21:         Thought = chatGPTReasoningItemKind3;
22:         a = new ChatGPTReasoningItemKind[]{chatGPTReasoningItemKind, chatGPTReasoningItemKind2, chatGPTReasoningItemKind3};
23:     }
24: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:25`
```text
23:     }
24: 
25:     public static ChatGPTReasoningItemKind valueOf(String str) {
26:         return (ChatGPTReasoningItemKind) Enum.valueOf(ChatGPTReasoningItemKind.class, str);
27:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:26`
```text
24: 
25:     public static ChatGPTReasoningItemKind valueOf(String str) {
26:         return (ChatGPTReasoningItemKind) Enum.valueOf(ChatGPTReasoningItemKind.class, str);
27:     }
28: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:29`
```text
27:     }
28: 
29:     public static ChatGPTReasoningItemKind[] values() {
30:         return (ChatGPTReasoningItemKind[]) a.clone();
31:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningItemKind.java:30`
```text
28: 
29:     public static ChatGPTReasoningItemKind[] values() {
30:         return (ChatGPTReasoningItemKind[]) a.clone();
31:     }
32: }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import com.snap.valdi.utils.b;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:9`
```text
7: import kotlin.Metadata;
8: 
9: @o2d0(propertyReplacements = "", schema = "'activeItem':r?:'[0]','items':a<r:'[1]'>,'status':r<e>:'[2]','summaryTitle':s?", typeReferences = {ChatGPTReasoningActiveItem.class, hm9.class, ChatGPTReasoningStatus.class})
10: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\u0006\u0010\b\u001a\u00020\u0007\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\t¢\u0006\u0004\b\u000b\u0010\fR\u0018\u0010\r\u
11: public final class ChatGPTReasoningState extends b {
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:10`
```text
8: 
9: @o2d0(propertyReplacements = "", schema = "'activeItem':r?:'[0]','items':a<r:'[1]'>,'status':r<e>:'[2]','summaryTitle':s?", typeReferences = {ChatGPTReasoningActiveItem.class, hm9.class, ChatGPTReasoningStatus.class})
10: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\u0006\u0010\b\u001a\u00020\u0007\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\t¢\u0006\u0004\b\u000b\u0010\fR\u0018\u0010\r\u
11: public final class ChatGPTReasoningState extends b {
12:     private ChatGPTReasoningActiveItem _activeItem;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:11`
```text
9: @o2d0(propertyReplacements = "", schema = "'activeItem':r?:'[0]','items':a<r:'[1]'>,'status':r<e>:'[2]','summaryTitle':s?", typeReferences = {ChatGPTReasoningActiveItem.class, hm9.class, ChatGPTReasoningStatus.class})
10: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\u0006\u0010\b\u001a\u00020\u0007\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\t¢\u0006\u0004\b\u000b\u0010\fR\u0018\u0010\r\u
11: public final class ChatGPTReasoningState extends b {
12:     private ChatGPTReasoningActiveItem _activeItem;
13:     private List<hm9> _items;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:12`
```text
10: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\f\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004\u0012\u0006\u0010\b\u001a\u00020\u0007\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\t¢\u0006\u0004\b\u000b\u0010\fR\u0018\u0010\r\u
11: public final class ChatGPTReasoningState extends b {
12:     private ChatGPTReasoningActiveItem _activeItem;
13:     private List<hm9> _items;
14:     private ChatGPTReasoningStatus _status;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:14`
```text
12:     private ChatGPTReasoningActiveItem _activeItem;
13:     private List<hm9> _items;
14:     private ChatGPTReasoningStatus _status;
15:     private String _summaryTitle;
16: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:17`
```text
15:     private String _summaryTitle;
16: 
17:     public ChatGPTReasoningState(ChatGPTReasoningActiveItem chatGPTReasoningActiveItem, List<hm9> list, ChatGPTReasoningStatus chatGPTReasoningStatus, String str) {
18:         this._activeItem = chatGPTReasoningActiveItem;
19:         this._items = list;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:18`
```text
16: 
17:     public ChatGPTReasoningState(ChatGPTReasoningActiveItem chatGPTReasoningActiveItem, List<hm9> list, ChatGPTReasoningStatus chatGPTReasoningStatus, String str) {
18:         this._activeItem = chatGPTReasoningActiveItem;
19:         this._items = list;
20:         this._status = chatGPTReasoningStatus;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningState.java:20`
```text
18:         this._activeItem = chatGPTReasoningActiveItem;
19:         this._items = list;
20:         this._status = chatGPTReasoningStatus;
21:         this._summaryTitle = str;
22:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:1`
```text
1: package com.openai.valdi.chatgpt.reasoning;
2: 
3: import defpackage.q4d0;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'InProgress':0,'Complete':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus;", "", "InProgress", "Complete", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningStatus {
10:     public static final ChatGPTReasoningStatus Complete;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:9`
```text
7: @q4d0(propertyReplacements = "", schema = "'InProgress':0,'Complete':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus;", "", "InProgress", "Complete", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningStatus {
10:     public static final ChatGPTReasoningStatus Complete;
11:     public static final ChatGPTReasoningStatus InProgress;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus;", "", "InProgress", "Complete", "modules_chatgpt_reasoning-chatgpt_reasoning_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class ChatGPTReasoningStatus {
10:     public static final ChatGPTReasoningStatus Complete;
11:     public static final ChatGPTReasoningStatus InProgress;
12:     public static final ChatGPTReasoningStatus[] a;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:11`
```text
9: public final class ChatGPTReasoningStatus {
10:     public static final ChatGPTReasoningStatus Complete;
11:     public static final ChatGPTReasoningStatus InProgress;
12:     public static final ChatGPTReasoningStatus[] a;
13: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:12`
```text
10:     public static final ChatGPTReasoningStatus Complete;
11:     public static final ChatGPTReasoningStatus InProgress;
12:     public static final ChatGPTReasoningStatus[] a;
13: 
14:     static {
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:15`
```text
13: 
14:     static {
15:         ChatGPTReasoningStatus chatGPTReasoningStatus = new ChatGPTReasoningStatus("InProgress", 0);
16:         InProgress = chatGPTReasoningStatus;
17:         ChatGPTReasoningStatus chatGPTReasoningStatus2 = new ChatGPTReasoningStatus("Complete", 1);
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:16`
```text
14:     static {
15:         ChatGPTReasoningStatus chatGPTReasoningStatus = new ChatGPTReasoningStatus("InProgress", 0);
16:         InProgress = chatGPTReasoningStatus;
17:         ChatGPTReasoningStatus chatGPTReasoningStatus2 = new ChatGPTReasoningStatus("Complete", 1);
18:         Complete = chatGPTReasoningStatus2;
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:17`
```text
15:         ChatGPTReasoningStatus chatGPTReasoningStatus = new ChatGPTReasoningStatus("InProgress", 0);
16:         InProgress = chatGPTReasoningStatus;
17:         ChatGPTReasoningStatus chatGPTReasoningStatus2 = new ChatGPTReasoningStatus("Complete", 1);
18:         Complete = chatGPTReasoningStatus2;
19:         a = new ChatGPTReasoningStatus[]{chatGPTReasoningStatus, chatGPTReasoningStatus2};
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:18`
```text
16:         InProgress = chatGPTReasoningStatus;
17:         ChatGPTReasoningStatus chatGPTReasoningStatus2 = new ChatGPTReasoningStatus("Complete", 1);
18:         Complete = chatGPTReasoningStatus2;
19:         a = new ChatGPTReasoningStatus[]{chatGPTReasoningStatus, chatGPTReasoningStatus2};
20:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:19`
```text
17:         ChatGPTReasoningStatus chatGPTReasoningStatus2 = new ChatGPTReasoningStatus("Complete", 1);
18:         Complete = chatGPTReasoningStatus2;
19:         a = new ChatGPTReasoningStatus[]{chatGPTReasoningStatus, chatGPTReasoningStatus2};
20:     }
21: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:22`
```text
20:     }
21: 
22:     public static ChatGPTReasoningStatus valueOf(String str) {
23:         return (ChatGPTReasoningStatus) Enum.valueOf(ChatGPTReasoningStatus.class, str);
24:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:23`
```text
21: 
22:     public static ChatGPTReasoningStatus valueOf(String str) {
23:         return (ChatGPTReasoningStatus) Enum.valueOf(ChatGPTReasoningStatus.class, str);
24:     }
25: 
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:26`
```text
24:     }
25: 
26:     public static ChatGPTReasoningStatus[] values() {
27:         return (ChatGPTReasoningStatus[]) a.clone();
28:     }
```

### `sources/com/openai/valdi/chatgpt/reasoning/ChatGPTReasoningStatus.java:27`
```text
25: 
26:     public static ChatGPTReasoningStatus[] values() {
27:         return (ChatGPTReasoningStatus[]) a.clone();
28:     }
29: }
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'basicModels':s,'coreModel':s,'moreMessages':s,'moreUploads':s,'goImageCreation':s,'longerMemory':s,'noAds':s,'smarterModels':s,'moreMessagesAndUploads':s,'plusImageCreation':s,'moreMemory':s,'agentsAndDeepResearch':s,'earlyAccess':s,'proFrontierModel':s,'proCodex':s,'proDeepResearch':s,'proUnlimitedModel':s,'proMaximumMemory':s,'advancedChatIntelligence':s,'expandedCodexTokenUsage':s,'advancedCodingModels':s,'expandedDataAnalysisTools':s,'moreParallelT
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\bB\b\u0007\u0018\u00002\u00020\u0001B\u0081\u0002\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002\u0012\u0006\u0010\b\u001a\u00020\u0002\u0012\u0006\u0010\t\u001a\u00020\u0002\u0012\u0006\u0010\n\u001a\u00020\u0002\u0012\u0006\
9: public final class SubscriptionPricingNativeFeatureCopy extends b {
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'basicModels':s,'coreModel':s,'moreMessages':s,'moreUploads':s,'goImageCreation':s,'longerMemory':s,'noAds':s,'smarterModels':s,'moreMessagesAndUploads':s,'plusImageCreation':s,'moreMemory':s,'agentsAndDeepResearch':s,'earlyAccess':s,'proFrontierModel':s,'proCodex':s,'proDeepResearch':s,'proUnlimitedModel':s,'proMaximumMemory':s,'advancedChatIntelligence':s,'expandedCodexTokenUsage':s,'advancedCodingModels':s,'expandedDataAnalysisTools':s,'moreParallelT
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\bB\b\u0007\u0018\u00002\u00020\u0001B\u0081\u0002\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002\u0012\u0006\u0010\b\u001a\u00020\u0002\u0012\u0006\u0010\t\u001a\u00020\u0002\u0012\u0006\u0010\n\u001a\u00020\u0002\u0012\u0006\
9: public final class SubscriptionPricingNativeFeatureCopy extends b {
10:     private String _advancedChatIntelligence;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\bB\b\u0007\u0018\u00002\u00020\u0001B\u0081\u0002\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002\u0012\u0006\u0010\b\u001a\u00020\u0002\u0012\u0006\u0010\t\u001a\u00020\u0002\u0012\u0006\u0010\n\u001a\u00020\u0002\u0012\u0006\
9: public final class SubscriptionPricingNativeFeatureCopy extends b {
10:     private String _advancedChatIntelligence;
11:     private String _advancedCodingModels;
12:     private String _advancedImageQualityWithThinking;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:13`
```text
11:     private String _advancedCodingModels;
12:     private String _advancedImageQualityWithThinking;
13:     private String _advancedIntelligence;
14:     private String _agentsAndDeepResearch;
15:     private String _basicModels;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:61`
```text
59:         this._proUnlimitedModel = str17;
60:         this._proMaximumMemory = str18;
61:         this._advancedChatIntelligence = str19;
62:         this._expandedCodexTokenUsage = str20;
63:         this._advancedCodingModels = str21;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativeFeatureCopy.java:69`
```text
67:         this._multiImageOutput = str25;
68:         this._noWatermarks = str26;
69:         this._advancedIntelligence = str27;
70:         this._connectToBankAccounts = str28;
71:         this._spendingBreakdowns = str29;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Coding':0,'ImageGeneration':1,'PersonalFinance':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent;", "", "Coding", "ImageGeneration", "PersonalFinance", "modules_chatgpt_subscription_pricing-chatgpt_subscription_pricing_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class SubscriptionPricingNativePersonalizationIntent {
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Coding':0,'ImageGeneration':1,'PersonalFinance':2", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0004\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004¨\u0006\u0005"}, d2 = {"Lcom/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent;", "", "Coding", "ImageGeneration", "PersonalFinance", "modules_chatgpt_subscription_pricing-chatgpt_subscription_pricing_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class SubscriptionPricingNativePersonalizationIntent {
10:     public static final SubscriptionPricingNativePersonalizationIntent Coding;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent.java:11`
```text
9: public final class SubscriptionPricingNativePersonalizationIntent {
10:     public static final SubscriptionPricingNativePersonalizationIntent Coding;
11:     public static final SubscriptionPricingNativePersonalizationIntent ImageGeneration;
12:     public static final SubscriptionPricingNativePersonalizationIntent PersonalFinance;
13:     public static final SubscriptionPricingNativePersonalizationIntent[] a;
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent.java:18`
```text
16:         SubscriptionPricingNativePersonalizationIntent subscriptionPricingNativePersonalizationIntent = new SubscriptionPricingNativePersonalizationIntent("Coding", 0);
17:         Coding = subscriptionPricingNativePersonalizationIntent;
18:         SubscriptionPricingNativePersonalizationIntent subscriptionPricingNativePersonalizationIntent2 = new SubscriptionPricingNativePersonalizationIntent("ImageGeneration", 1);
19:         ImageGeneration = subscriptionPricingNativePersonalizationIntent2;
20:         SubscriptionPricingNativePersonalizationIntent subscriptionPricingNativePersonalizationIntent3 = new SubscriptionPricingNativePersonalizationIntent("PersonalFinance", 2);
```

### `sources/com/openai/valdi/chatgpt/subscription/pricing/SubscriptionPricingNativePersonalizationIntent.java:19`
```text
17:         Coding = subscriptionPricingNativePersonalizationIntent;
18:         SubscriptionPricingNativePersonalizationIntent subscriptionPricingNativePersonalizationIntent2 = new SubscriptionPricingNativePersonalizationIntent("ImageGeneration", 1);
19:         ImageGeneration = subscriptionPricingNativePersonalizationIntent2;
20:         SubscriptionPricingNativePersonalizationIntent subscriptionPricingNativePersonalizationIntent3 = new SubscriptionPricingNativePersonalizationIntent("PersonalFinance", 2);
21:         PersonalFinance = subscriptionPricingNativePersonalizationIntent3;
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationCapabilities.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'browser':b,'codex':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class OAIAuthenticationCapabilities extends b {
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationCapabilities.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'browser':b,'codex':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class OAIAuthenticationCapabilities extends b {
10:     private boolean _browser;
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationCapabilities.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/val
9: public final class OAIAuthenticationCapabilities extends b {
10:     private boolean _browser;
11:     private boolean _codex;
12: 
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationCapabilities.java:14`
```text
12: 
13:     public OAIAuthenticationCapabilities(boolean z, boolean z2) {
14:         this._browser = z;
15:         this._codex = z2;
16:     }
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationMethod.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Browser':0,'Codex':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/oai/platform/OAIAuthenticationMethod;", "", "Browser", "Codex", "modules_oai_authentication-oai_authentication_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class OAIAuthenticationMethod {
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationMethod.java:8`
```text
6: 
7: @q4d0(propertyReplacements = "", schema = "'Browser':0,'Codex':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/oai/platform/OAIAuthenticationMethod;", "", "Browser", "Codex", "modules_oai_authentication-oai_authentication_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class OAIAuthenticationMethod {
10:     public static final OAIAuthenticationMethod Browser;
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationMethod.java:10`
```text
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/oai/platform/OAIAuthenticationMethod;", "", "Browser", "Codex", "modules_oai_authentication-oai_authentication_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class OAIAuthenticationMethod {
10:     public static final OAIAuthenticationMethod Browser;
11:     public static final OAIAuthenticationMethod Codex;
12:     public static final OAIAuthenticationMethod[] a;
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationMethod.java:15`
```text
13: 
14:     static {
15:         OAIAuthenticationMethod oAIAuthenticationMethod = new OAIAuthenticationMethod("Browser", 0);
16:         Browser = oAIAuthenticationMethod;
17:         OAIAuthenticationMethod oAIAuthenticationMethod2 = new OAIAuthenticationMethod("Codex", 1);
```

### `sources/com/openai/valdi/oai/platform/OAIAuthenticationMethod.java:16`
```text
14:     static {
15:         OAIAuthenticationMethod oAIAuthenticationMethod = new OAIAuthenticationMethod("Browser", 0);
16:         Browser = oAIAuthenticationMethod;
17:         OAIAuthenticationMethod oAIAuthenticationMethod2 = new OAIAuthenticationMethod("Codex", 1);
18:         Codex = oAIAuthenticationMethod2;
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsActionHandler.java:9`
```text
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0007\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u0017\u0010\n\u001a\u00020\u00022\u0006\u0010\t\u001a\u00020\u0005H&¢\u0006\u0004\b\n\u0010\b
10: @t5d0(propertyReplacements = "", proxyClass = tgz.class, schema = "'refresh':f|m|(),'disconnect':f|m|(s),'addConnector':f|m|(s),'renderFailure':f|m|(s)", typeReferences = {})
11: public interface OlympicConnectionsActionHandler extends ValdiMarshallable {
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsActionHandler.java:10`
```text
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0007\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u0017\u0010\n\u001a\u00020\u00022\u0006\u0010\t\u001a\u00020\u0005H&¢\u0006\u0004\b\n\u0010\b
10: @t5d0(propertyReplacements = "", proxyClass = tgz.class, schema = "'refresh':f|m|(),'disconnect':f|m|(s),'addConnector':f|m|(s),'renderFailure':f|m|(s)", typeReferences = {})
11: public interface OlympicConnectionsActionHandler extends ValdiMarshallable {
12:     void addConnector(String connectorID);
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsActionHandler.java:12`
```text
10: @t5d0(propertyReplacements = "", proxyClass = tgz.class, schema = "'refresh':f|m|(),'disconnect':f|m|(s),'addConnector':f|m|(s),'renderFailure':f|m|(s)", typeReferences = {})
11: public interface OlympicConnectionsActionHandler extends ValdiMarshallable {
12:     void addConnector(String connectorID);
13: 
14:     void disconnect(String connectionID);
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsHost.java:11`
```text
9: import kotlin.Metadata;
10: 
11: @Metadata(d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\n\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J%\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00020\u00052\u0006\u0010\u0003\u001a\u00020\u00022\u0006\u0010\u0004\u001a\u00020\u0002H&¢\u0006\u0004\b\u0006\u0010\u0007J\u0017\u0010\n\u001a\u00020\t2\u0006\u0010\b\u001a\u00020\u0002H&¢\u000
12: @t5d0(propertyReplacements = "", proxyClass = xgz.class, schema = "'callTool':f|m|(s, s): p<s>,'requestModal':f|m|(s),'requestLinkToConnector':f|m|(s),'openExternal':f|m|(s),'renderFailure':f|m|(s),'sendInstrument':f?|m|(s)", typeReferences = {})
13: public interface OlympicConnectionsHost extends ValdiMarshallable {
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsHost.java:12`
```text
10: 
11: @Metadata(d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\n\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J%\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00020\u00052\u0006\u0010\u0003\u001a\u00020\u00022\u0006\u0010\u0004\u001a\u00020\u0002H&¢\u0006\u0004\b\u0006\u0010\u0007J\u0017\u0010\n\u001a\u00020\t2\u0006\u0010\b\u001a\u00020\u0002H&¢\u000
12: @t5d0(propertyReplacements = "", proxyClass = xgz.class, schema = "'callTool':f|m|(s, s): p<s>,'requestModal':f|m|(s),'requestLinkToConnector':f|m|(s),'openExternal':f|m|(s),'renderFailure':f|m|(s),'sendInstrument':f?|m|(s)", typeReferences = {})
13: public interface OlympicConnectionsHost extends ValdiMarshallable {
14:     Promise<String> callTool(String name, String argsJson);
```

### `sources/com/openai/valdi/olympic/connections/OlympicConnectionsHost.java:23`
```text
21:     void renderFailure(String message);
22: 
23:     void requestLinkToConnector(String connectorID);
24: 
25:     void requestModal(String paramsJson);
```

_Hits captured: 180 (cap 180)_

## ROUTES_INTENTS

### `sources/androidx/core/content/FileProvider.java:251`
```text
249:         int i;
250:         File fileB = ((hmo) a()).b(uri);
251:         String queryParameter = uri.getQueryParameter(DISPLAYNAME_FIELD);
252:         if (strArr == null) {
253:             strArr = COLUMNS;
```

### `sources/com/openai/feature/conversation/common/businesslogic/FailedMessageRetryException.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/businesslogic/FailedMessageRetryException;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: final class FailedMessageRetryException extends Exception {
7:     public FailedMessageRetryException() {
```

### `sources/com/openai/feature/conversation/common/instructions/api/CustomInstructionsUpdateException.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/instructions/api/CustomInstructionsUpdateException;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
7: public final class CustomInstructionsUpdateException extends Exception {
8:     public final f42 a;
```

### `sources/com/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechAudioPlayerFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechAudioPlayerFailure extends Exception {
7: }
```

### `sources/com/openai/feature/conversation/common/speech/SpeechPlaybackFailure.java:5`
```text
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/conversation/common/speech/SpeechPlaybackFailure;", "Ljava/lang/Exception;", "Lkotlin/Exception;", "public"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class SpeechPlaybackFailure extends Exception {
7:     public final int a;
```

### `sources/com/openai/feature/conversations/impl/conversation/stream/StreamHandoffException.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @Metadata(d1 = {"\u0000\n\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00020\u0001¨\u0006\u0002"}, d2 = {"Lcom/openai/feature/conversations/impl/conversation/stream/StreamHandoffException;", "Ljava/io/IOException;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
7: final class StreamHandoffException extends IOException {
8: }
```

### `sources/defpackage/a2a.java:23`
```text
21:         }
22:         try {
23:             iArr[ChatgptFileLibraryAction.CHATGPT_FILE_LIBRARY_ACTION_VIEW_CHANGED.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
```

### `sources/defpackage/auk.java:17`
```text
15:         ArrayList arrayListC = super.c();
16:         buk.INSTANCE.getClass();
17:         return fke.l1(Uri.parse("com.openai.chat://codex/open"), fke.l1(Uri.parse("chatgpt://codex"), arrayListC));
18:     }
19: 
```

### `sources/defpackage/auk.java:29`
```text
27:         ArrayList arrayListF = super.f();
28:         buk.INSTANCE.getClass();
29:         return fke.l1(Uri.parse("com.openai.chat://codex/open"), fke.l1(Uri.parse("chatgpt://codex"), arrayListF));
30:     }
31: 
```

### `sources/defpackage/b2a.java:31`
```text
29:                 return;
30:             }
31:             str = "CHATGPT_FILE_LIBRARY_ACTION_VIEW_CHANGED";
32:         }
33:         encoder.G(str);
```

### `sources/defpackage/bpk.java:98`
```text
96:             case 1:
97:                 fpk fpkVar = (fpk) m350Var;
98:                 Set<String> queryParameterNames = uri.getQueryParameterNames();
99:                 int iX0 = evv.x0(gke.r0(queryParameterNames, 10));
100:                 if (iX0 < 16) {
```

### `sources/defpackage/bpk.java:105`
```text
103:                 LinkedHashMap linkedHashMap = new LinkedHashMap(iX0);
104:                 for (Object obj : queryParameterNames) {
105:                     String queryParameter = uri.getQueryParameter((String) obj);
106:                     if (queryParameter == null) {
107:                         queryParameter = "";
```

### `sources/defpackage/bpk.java:117`
```text
115:             case 11:
116:                 hbl hblVar = (hbl) m350Var;
117:                 return new hbl(hblVar.a, uri.getQueryParameter("campaign"), hblVar.c);
118:             default:
119:                 return m350Var;
```

### `sources/defpackage/bqk.java:194`
```text
192:                 return new dqk("/apps/" + ((Object) pathSegments.get(1)) + "/" + ((Object) pathSegments.get(2)));
193:             case 4:
194:                 String queryParameter = uri.getQueryParameter("pairing_code");
195:                 if (queryParameter == null || (string = qa90.W0(queryParameter).toString()) == null || (strE = ra90.e(string)) == null) {
196:                     return null;
```

### `sources/defpackage/d1s.java:40`
```text
38:                 return q1d0.Companion.serializer();
39:             case 10:
40:                 return e8s.a("8o5K8YFH73RC7Gw+62Q452I35mA46Gc/62xG73FM8nVP9npZ+IBj+oVq+4hx+4x7+5WK/JuT/J6X+6Cb/KSi/Kqo/K6w/LGz/Lq8/MPG/MbK/MnN/MjN/MrN/M3Q/c7Q/M/R/NHS+9LT+NXU9tfT8trW7d/c7N/c7N/b6+Db69/b693a6t3a6dzZ6NvX5tnV5NfT49bT49XS49XR85VP8Y1I8HtD7Wk951425l4y5V4y42I452lC7HBM8HZU9HtZ939g+INn+opx/I16/JGB/JiO/KCY/KSh/Kak/Kqn/LCw/LS3/La5/L7B/MbK/MvQ/czT/MzR/M7P/c/R/NHS/NLT+9PT+NXU9tfU8NzY7d/c7N/c6+Db6+Db697a697a6tzZ6dvX6NrW5tjV49fS4tXR4tTQ4tTQ9JZV85NS8IlJ7XZB6WM55Vow41ov4GE44mY85W9G6nVS73lZ835f94
41:             case 11:
42:                 return e8s.a("k0M+kEI9jkI9jkI+ij05jEA9ij06iD06iT89iD8+hT8+gz4+gz8/gT4/gT8/fj0+fD0/ej0/dj0/cz0+cDs9bjs9bTw9aTo8Zzo8Yzg6YTg7YTo8Xzg6Wzc5WTg5WDg5VTY5UjU2UTU2TjQ2TDM2SjM1RzI0RjI0RTIzQjEyQTAxQDAxPS8xOy4vPDExOi8wOjEyOjM0ODEzNjAxl0tFkD86jT04jzw3jjw3jT06jT07jj88jkE+jEA/iUFAiEBAhj9AhT8/hT8/gz4/gD9AfT9Aez5AeD5AdDw/cjw+cDw+bTw9bDw+aDs9ZDk8Yzo8YTo7Xzg7XDg6Wjg6WDc5VjY4VDc4UDY3TjQ2TTQ2SjM1SDM0RjIzRjI0QzIzQDEyPzAyPC8wOi4vOS4vNi0uNS0uNC0vODEzl0lDkT43kT04kj04kT04kT46kT47kj88kUA+j0A/jUA/i0BAikBAiU
```

### `sources/defpackage/dai.java:236`
```text
234:         lt80 lt80Var = (lt80) ((xxb0) vxb0Var).b;
235:         localeH = lpf.H(this.b);
236:         queryParameter = Uri.parse(URLDecoder.decode(vmoVar.b, "UTF-8")).getQueryParameter("rscd");
237:         if (queryParameter != null && (str5 = (String) fke.Z0(qa90.H0(queryParameter, new String[]{"filename="}, 0, 6))) != null) {
238:             strM = qk80.m(str5, localeH);
```

### `sources/defpackage/dai.java:308`
```text
306:             lt80 lt80Var2 = (lt80) ((xxb0) vxb0Var).b;
307:             localeH = lpf.H(this.b);
308:             queryParameter = Uri.parse(URLDecoder.decode(vmoVar.b, "UTF-8")).getQueryParameter("rscd");
309:             if (queryParameter != null) {
310:                 strM = qk80.m(str5, localeH);
```

### `sources/defpackage/dc50.java:4`
```text
2: 
3: public final class dc50 {
4:     ConfiguredInstantModel("chatgpt://safety-faster-model", 0),
5:     EventFasterModel("chatgpt://safety-faster-model-from-event", 1);
6: 
```

### `sources/defpackage/dc50.java:5`
```text
3: public final class dc50 {
4:     ConfiguredInstantModel("chatgpt://safety-faster-model", 0),
5:     EventFasterModel("chatgpt://safety-faster-model-from-event", 1);
6: 
7:     public static final hon f;
```

### `sources/defpackage/df70.java:32`
```text
30:                 try {
31:                     URLDecoder.decode(encodedQuery, StandardCharsets.UTF_8.name());
32:                     Set<String> queryParameterNames = uri.getQueryParameterNames();
33:                     Set<String> set2 = queryParameterNames;
34:                     if (!(set2 instanceof Collection) || !set2.isEmpty()) {
```

### `sources/defpackage/df70.java:41`
```text
39:                                 for (String str2 : queryParameterNames) {
40:                                     if (!set.contains(str2)) {
41:                                         Iterator<T> it2 = uri.getQueryParameters(str2).iterator();
42:                                         while (it2.hasNext()) {
43:                                             builderClearQuery.appendQueryParameter(str2, (String) it2.next());
```

### `sources/defpackage/ixm.java:26`
```text
24:         this.k = wnm.F(6, "EditParagenUseCase");
25:         this.l = new LinkedHashSet();
26:         bvj.t(h2hVar.j(), this.b, new pi3(2, this, ixm.class, "onConversationUpdated", "onConversationUpdated(Lcom/openai/feature/conversation/common/domain/conversation/Conversation;)V", 4, (byte) 7));
27:         bvj.t(new qo(h2hVar.j(), (byte) 27), this.b, new txl(this, null, (byte) 1));
28:     }
```

### `sources/defpackage/kqg.java:16`
```text
14:         lke lkeVar = new lke(rpgVar, (byte) 3);
15:         if (rpgVar instanceof hfg) {
16:             ph60VarC = th60.C(new lke(((hfg) rpgVar).j, (byte) 0), new arf(1, this, kqg.class, "flattenedWithEmbeddedReferences", "flattenedWithEmbeddedReferences(Lcom/openai/feature/conversation/common/api/message/ContentReference;)Lkotlin/sequences/Sequence;", 0, (byte) 3));
17:         } else {
18:             ph60VarC = fgn.a;
```

### `sources/defpackage/kqg.java:67`
```text
65:             return null;
66:         }
67:         t7p t7pVar = new t7p(th60.C(new lke(list, (byte) 0), new arf(1, this, kqg.class, "flattenedWithEmbeddedReferences", "flattenedWithEmbeddedReferences(Lcom/openai/feature/conversation/common/api/message/ContentReference;)Lkotlin/sequences/Sequence;", 0, (byte) 4)));
68:         while (t7pVar.hasNext()) {
69:             Object next = t7pVar.next();
```

### `sources/defpackage/kwk.java:26`
```text
24:         pluginGeneratedSerialDescriptor.k("messageMetadata", true);
25:         pluginGeneratedSerialDescriptor.k("submissionContext", true);
26:         pluginGeneratedSerialDescriptor.k("allowWhenLoggedIn", true);
27:         pluginGeneratedSerialDescriptor.k("imagePromptId", true);
28:         pluginGeneratedSerialDescriptor.k("modelSelection", true);
```

### `sources/defpackage/m7u.java:240`
```text
238: 
239:     public m7u(ibx ibxVar) {
240:         super(1, ibxVar, ibx.class, "submitCustomActionMessage", "submitCustomActionMessage(Lcom/openai/feature/conversation/common/domain/message/Message;)V", 0);
241:         this.b = (byte) 29;
242:     }
```

### `sources/defpackage/mm2.java:32`
```text
30:         pluginGeneratedSerialDescriptor.k("systemHints", true);
31:         pluginGeneratedSerialDescriptor.k("destinationMetadata", true);
32:         pluginGeneratedSerialDescriptor.k("autoSend", true);
33:         descriptor = pluginGeneratedSerialDescriptor;
34:     }
```

### `sources/defpackage/nj90.java:14`
```text
12:         nj90 nj90Var = new nj90("PrefillComposer", 0);
13:         b = nj90Var;
14:         nj90 nj90Var2 = new nj90("AutoSend", 1);
15:         c = nj90Var2;
16:         d = new nj90[]{nj90Var, nj90Var2};
```

### `sources/defpackage/nx1.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("prompt", false);
19:         pluginGeneratedSerialDescriptor.k("entrypoint", true);
20:         pluginGeneratedSerialDescriptor.k("autoSend", true);
21:         pluginGeneratedSerialDescriptor.k("developerMessage", true);
22:         pluginGeneratedSerialDescriptor.k("inputRequirements", true);
```

### `sources/defpackage/pwg.java:78`
```text
76:         int i5 = 20;
77:         j = new pwg("gmail_memory_nux_modal", "Gmail Memory NUX Modal", new q76("A modal title goes here for this preview", "A modal description goes here to show how supporting copy wraps across lines in this preview.", null, null, d76Var, 25), bvj.T(new i26("gmail_memory_nux_modal_settings", "Button A", p26Var3, new rmz("https://chatgpt.com/settings/personalization"), 20), new i26("gmail_memory_nux_modal_try_it_out", "Button B", p26Var2, new rmz("https://chatgpt.com/?q=What%20important%20thing
78:         k = new pwg("tasks_nux_modal", "Tasks NUX Modal", new t36("Tasks in ChatGPT", "Ask ChatGPT to handle tasks, monitor changes, and follow up for you, even when you're away."), Collections.singletonList(new i26("tasks_nux_modal_get_started", "Get started", p26Var2, new rmz("chatgpt://scheduled"), i5)));
79:     }
80: 
```

### `sources/defpackage/q6f0.java:146`
```text
144:         if (uri == null || !wnm.k(uri.getScheme(), uri2.getScheme()) || !wnm.k(uri.getHost(), uri2.getHost()) || !wnm.k(uri.getPath(), uri2.getPath())) {
145:             txb0Var = new txb0(new AuthError.WebAuthFailed("Authorization callback did not match the configured redirect URI", o6f0Var.c(), 4));
146:         } else if (wnm.k(uri.getQueryParameter("state"), o6f0Var.a().c())) {
147:             String queryParameter = uri.getQueryParameter("error");
148:             if (queryParameter != null) {
```

### `sources/defpackage/q6f0.java:147`
```text
145:             txb0Var = new txb0(new AuthError.WebAuthFailed("Authorization callback did not match the configured redirect URI", o6f0Var.c(), 4));
146:         } else if (wnm.k(uri.getQueryParameter("state"), o6f0Var.a().c())) {
147:             String queryParameter = uri.getQueryParameter("error");
148:             if (queryParameter != null) {
149:                 String queryParameter2 = uri.getQueryParameter("error_description");
```

### `sources/defpackage/q6f0.java:149`
```text
147:             String queryParameter = uri.getQueryParameter("error");
148:             if (queryParameter != null) {
149:                 String queryParameter2 = uri.getQueryParameter("error_description");
150:                 ju4 ju4VarA = ju4.a(o6f0Var.c(), null, null, queryParameter, null, null, 223);
151:                 if (o6f0Var.d() == l8f0.b && i.contains(queryParameter)) {
```

### `sources/defpackage/q6f0.java:162`
```text
160:                 xxb0Var = new txb0(webAuthFailed);
161:             } else {
162:                 String queryParameter3 = uri.getQueryParameter("code");
163:                 if (queryParameter3 == null || qa90.l0(queryParameter3)) {
164:                     txb0Var = new txb0(new AuthError.MissingResponse(o6f0Var.c()));
```

### `sources/defpackage/ru2.java:25`
```text
23:         pluginGeneratedSerialDescriptor.k("oneliner", false);
24:         pluginGeneratedSerialDescriptor.k("prompt", false);
25:         pluginGeneratedSerialDescriptor.k("autoSend", true);
26:         pluginGeneratedSerialDescriptor.k("hideFirstMessage", true);
27:         pluginGeneratedSerialDescriptor.k("category", false);
```

### `sources/defpackage/s7j.java:106`
```text
104:         if (i2 == 0) {
105:             ct40.j(obj);
106:             if (szv.y(uri) && !wnm.k(uri.getQueryParameter("noauth"), "true") && (queryParameter = (uriI = szv.I(uri, "temporary_audio")).getQueryParameter("conversation_id")) != null) {
107:                 fnc0 fnc0VarH = ix40.h(uriI.toString());
108:                 r7jVar.n = queryParameter;
```

### `sources/defpackage/siw.java:5`
```text
3: @ii60(with = riw.class)
4: public final class siw {
5:     AutoSend("auto_send"),
6:     TargetedReply("targeted_reply"),
7:     FillComposer("fill_composer"),
```

### `sources/defpackage/xb70.java:14`
```text
12:         xb70 xb70Var = new xb70("PrefillOnly", 0);
13:         b = xb70Var;
14:         xb70 xb70Var2 = new xb70("AutoSend", 1);
15:         c = xb70Var2;
16:         d = new xb70[]{xb70Var, xb70Var2};
```

### `sources/protobuf_analytics_events/v1/ChatgptFileLibraryAction.java:14`
```text
12: import kotlin.jvm.internal.DefaultConstructorMarker;
13: 
14: @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\u0010\b\n\u0002\b\f\b\u0086\u0081\u0002\u0018\u0000 \n2\u00020\u00012\b\u0012\u0004\u0012\u00020\u00000\u0002:\u0001\nB\u0011\b\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0003¢\u0006\u0004\b\u0005\u0010\u0006R\u001a\u0010\u0004\u001a\u00020\u00038\u0016X\u0096\u0004¢\u0006\f\n\u0004\b\u0004\u0010\u0007\u001a\u0004\b\b\u0010\tj\u0002\b\u000bj\u0002\b\fj\u0002\b\rj\u0002\b\u000e¨\u0006\u000f"}, d2 = 
15: public final class ChatgptFileLibraryAction implements ljf0 {
16:     CHATGPT_FILE_LIBRARY_ACTION_UNSPECIFIED(0),
```

### `sources/protobuf_analytics_events/v1/ChatgptFileLibraryAction.java:19`
```text
17:     CHATGPT_FILE_LIBRARY_ACTION_SHOWN(1),
18:     CHATGPT_FILE_LIBRARY_ACTION_DISMISSED(2),
19:     CHATGPT_FILE_LIBRARY_ACTION_VIEW_CHANGED(3);
20: 
21:     public static final ProtoAdapter<ChatgptFileLibraryAction> ADAPTER;
```

### `sources/protobuf_analytics_events/v1/ChatgptFileLibraryAction.java:75`
```text
73:                 return null;
74:             }
75:             return ChatgptFileLibraryAction.CHATGPT_FILE_LIBRARY_ACTION_VIEW_CHANGED;
76:         }
77: 
```

_Hits captured: 41 (cap 180)_

## CONVERSATION_ID_STATE

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:7`
```text
5: import android.graphics.Bitmap;
6: import android.net.Uri;
7: import android.service.notification.StatusBarNotification;
8: import androidx.work.CoroutineWorker;
9: import androidx.work.WorkerParameters;
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:58`
```text
56:             return false;
57:         }
58:         List<StatusBarNotification> listC = new w1z(getApplicationContext()).c();
59:         if ((listC instanceof Collection) && listC.isEmpty()) {
60:             return false;
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:62`
```text
60:             return false;
61:         }
62:         for (StatusBarNotification statusBarNotification : listC) {
63:             if (wnm.k(statusBarNotification.getTag(), str) && statusBarNotification.getId() == z3z.f) {
64:                 if (wnm.k(statusBarNotification.getNotification().extras.getString("com.openai.feature.notification.MEDIA_UPDATE_TOKEN"), payload.c)) {
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:63`
```text
61:         }
62:         for (StatusBarNotification statusBarNotification : listC) {
63:             if (wnm.k(statusBarNotification.getTag(), str) && statusBarNotification.getId() == z3z.f) {
64:                 if (wnm.k(statusBarNotification.getNotification().extras.getString("com.openai.feature.notification.MEDIA_UPDATE_TOKEN"), payload.c)) {
65:                     return true;
```

### `sources/com/openai/feature/notification/impl/NotificationMediaFetchWorker.java:64`
```text
62:         for (StatusBarNotification statusBarNotification : listC) {
63:             if (wnm.k(statusBarNotification.getTag(), str) && statusBarNotification.getId() == z3z.f) {
64:                 if (wnm.k(statusBarNotification.getNotification().extras.getString("com.openai.feature.notification.MEDIA_UPDATE_TOKEN"), payload.c)) {
65:                     return true;
66:                 }
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'messageId':s,'conversationId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'messageId':s,'conversationId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
10:     private String _conversationId;
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001d\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006
9: public final class FinanceTransactionsRequestContext extends b {
10:     private String _conversationId;
11:     private String _messageId;
12: 
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:15`
```text
13:     public FinanceTransactionsRequestContext(String str) {
14:         this._messageId = str;
15:         this._conversationId = null;
16:     }
17: 
```

### `sources/com/openai/valdi/chatgpt/finance/transactions/FinanceTransactionsRequestContext.java:20`
```text
18:     public FinanceTransactionsRequestContext(String str, String str2) {
19:         this._messageId = str;
20:         this._conversationId = str2;
21:     }
22: }
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?,'turnOrdinal':d@?,'contentReferenceStartIndex':d@?,'isModelWrittenDil':b,'isReadOnly':b@?,'widgetType':s?,'widgetName':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0014\b\u0007\u0018\u00002\u00020\u0001Bq\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\b\u001a\u0004\u0018\u0001
9: public final class DILMessageMetadata extends b {
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?,'turnOrdinal':d@?,'contentReferenceStartIndex':d@?,'isModelWrittenDil':b,'isReadOnly':b@?,'widgetType':s?,'widgetName':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0014\b\u0007\u0018\u00002\u00020\u0001Bq\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\b\u001a\u0004\u0018\u0001
9: public final class DILMessageMetadata extends b {
10:     private Double _contentReferenceIndex;
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:12`
```text
10:     private Double _contentReferenceIndex;
11:     private Double _contentReferenceStartIndex;
12:     private String _conversationId;
13:     private boolean _isModelWrittenDil;
14:     private Boolean _isReadOnly;
```

### `sources/com/openai/valdi/dil/DILMessageMetadata.java:21`
```text
19: 
20:     public DILMessageMetadata(String str, String str2, Double d, Double d2, Double d3, boolean z, Boolean bool, String str3, String str4) {
21:         this._conversationId = str;
22:         this._messageId = str2;
23:         this._contentReferenceIndex = d;
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @o2d0(propertyReplacements = "", schema = "'accountId':s,'accessToken':s,'baseUrl':s,'conversationId':s?,'parentMessageId':s", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u000e\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002¢\u0006\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\u0
8: public final class DeviceIntegrityRequest extends com.snap.valdi.utils.b {
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:7`
```text
5: 
6: @o2d0(propertyReplacements = "", schema = "'accountId':s,'accessToken':s,'baseUrl':s,'conversationId':s?,'parentMessageId':s", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u000e\b\u0007\u0018\u00002\u00020\u0001B5\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0002\u0012\u0006\u0010\u0007\u001a\u00020\u0002¢\u0006\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\u0
8: public final class DeviceIntegrityRequest extends com.snap.valdi.utils.b {
9:     private String _accessToken;
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:12`
```text
10:     private String _accountId;
11:     private String _baseUrl;
12:     private String _conversationId;
13:     private String _parentMessageId;
14: 
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:19`
```text
17:         this._accessToken = str2;
18:         this._baseUrl = str3;
19:         this._conversationId = str4;
20:         this._parentMessageId = str5;
21:     }
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:35`
```text
33:     }
34: 
35:     public final String get_conversationId() {
36:         return this._conversationId;
37:     }
```

### `sources/com/openai/valdi/integrity/DeviceIntegrityRequest.java:36`
```text
34: 
35:     public final String get_conversationId() {
36:         return this._conversationId;
37:     }
38: 
```

### `sources/com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java:190`
```text
188:         if (i3 == 0) {
189:             ct40.j(objB);
190:             String strA2 = getInputData().a("conversation_id");
191:             if (strA2 == null) {
192:                 return new yyu();
```

### `sources/defpackage/a300.java:20`
```text
18:         a = a300Var;
19:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("X0_gf-W53LWIM8rFdjb1wYY4iDmjygcA6GolQZQJt1o=", a300Var, 10);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("userPromptMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("displayedMessageIds", false);
```

### `sources/defpackage/ap80.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("spawnId", false);
20:         pluginGeneratedSerialDescriptor.k("text", true);
21:         pluginGeneratedSerialDescriptor.k("delegateConversationId", true);
22:         pluginGeneratedSerialDescriptor.k("metadata", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ar2.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("saveId", true);
18:         pluginGeneratedSerialDescriptor.k("projectId", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationTitle", true);
21:         pluginGeneratedSerialDescriptor.k("title", true);
```

### `sources/defpackage/av1.java:23`
```text
21:         pluginGeneratedSerialDescriptor.k("instruction", false);
22:         pluginGeneratedSerialDescriptor.k("numVariations", true);
23:         pluginGeneratedSerialDescriptor.k("conversationId", false);
24:         pluginGeneratedSerialDescriptor.k("mode", true);
25:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ayy.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("OmZev71Y156-8Lp3Bp-DY_oGdf_tcScWr8A2H_Fl1gY=", ayyVar, 4);
18:         pluginGeneratedSerialDescriptor.k("type", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("imageFileId", true);
21:         pluginGeneratedSerialDescriptor.k("actions", false);
```

### `sources/defpackage/b1i.java:18`
```text
16:         a = b1iVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("ml0VAl8FtX41xNs-nAcNn3TXL4a_fasVVnef-ip6xdA=", b1iVar, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("token", false);
20:         pluginGeneratedSerialDescriptor.k("parentMessageId", false);
```

### `sources/defpackage/bc80.java:33`
```text
31:         pluginGeneratedSerialDescriptor.k("userId", true);
32:         pluginGeneratedSerialDescriptor.k("accountId", true);
33:         pluginGeneratedSerialDescriptor.k("conversationId", true);
34:         pluginGeneratedSerialDescriptor.k("isSharedConversation", true);
35:         pluginGeneratedSerialDescriptor.k("original_message_id", true);
```

### `sources/defpackage/bh50.java:17`
```text
15:         a = bh50Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("3BJgFpD7vT27iKkDRs2EDx9O7VKUihnwurcEJcOWB2g=", bh50Var, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/bqk.java:71`
```text
69:             case 11:
70:                 super(mwjVar2);
71:                 this.e = Collections.singletonList("s/c_{conversationId}");
72:                 this.f = Collections.singletonList("s/c_sample-shared-conversation-id");
73:                 break;
```

### `sources/defpackage/bs20.java:19`
```text
17:         a = bs20Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("VY8aRV82L6lNZ5jDkd37OyLd-QtBGRs2daJ8lyhMqYY=", bs20Var, 6);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("supportedEncodings", true);
```

### `sources/defpackage/bs6.java:18`
```text
16:         a = bs6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("GHhDRE8Va8_Y_YothYADtLEluA_tAVnF2_AQcn-bX7o=", bs6Var, 4);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("challengeId", false);
20:         pluginGeneratedSerialDescriptor.k("selectedOption", true);
```

### `sources/defpackage/btg.java:28`
```text
26:         pluginGeneratedSerialDescriptor.k("moderationResults", true);
27:         pluginGeneratedSerialDescriptor.k("safeUrlMap", true);
28:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
29:         pluginGeneratedSerialDescriptor.k("defaultModelSlug", true);
30:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
```

### `sources/defpackage/bx2.java:17`
```text
15:         a = bx2Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("HhZ9kaHD6KMeWrvaLww8EzXdD722nnSVXfMzAHzWF7c=", bx2Var, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/cdi.java:18`
```text
16:         a = cdiVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("od7nq0-KubJImC08uRSeG8iE3oCQxyYXCMP92pxAjXo=", cdiVar, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("turnExchangeId", false);
20:         pluginGeneratedSerialDescriptor.k("options", true);
```

### `sources/defpackage/cjx.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("X0FymQwhYMehsMeKDIwRmnj4-5AZS3M2iCZe-StpYhM=", cjxVar, 5);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("feedback", false);
21:         pluginGeneratedSerialDescriptor.k("checkedReasons", true);
```

### `sources/defpackage/ck6.java:18`
```text
16:         a = ck6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("yh6ic6Q5rfOe5DDIRCoeg9IHs3MLxUXv6Ft6aT8clts=", ck6Var, 9);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("rating", true);
```

### `sources/defpackage/crk.java:17`
```text
15:         a = crkVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("JpL5cmQFiuYOA3ypncFb-UwfEP7qWa9cNeM8LQw62W4=", crkVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("remainingAttachmentSlots", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/czk.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("allowLibraryDelete", true);
20:         pluginGeneratedSerialDescriptor.k("allowFileExport", true);
21:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
23:     }
```

### `sources/defpackage/d63.java:17`
```text
15:         a = d63Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("reY0PReImFGQSIO-JHYtc7XophsR2t1KTrasmbiw__M=", d63Var, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/dh40.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("contentId", false);
18:         pluginGeneratedSerialDescriptor.k("productArea", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("userMessageId", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dk2.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("xZGh3OKrPqPJdbkDaGZYwXghYFDA3Fv6WRZXnPyoaAg=", dk2Var, 3);
18:         pluginGeneratedSerialDescriptor.k("kind", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageIds", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dn5.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("correction", false);
20:         pluginGeneratedSerialDescriptor.k("targetAction", false);
21:         pluginGeneratedSerialDescriptor.k("conversationId", false);
22:         pluginGeneratedSerialDescriptor.k("contextualHintSource", false);
23:         pluginGeneratedSerialDescriptor.k("cachedGeneratedAtIso", false);
```

### `sources/defpackage/duw.java:18`
```text
16:         a = duwVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("d1vqAOst3f2MX_Xf2thiN5-vVcznFFXA_eY9bn8yOPQ=", duwVar, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("rating", false);
```

### `sources/defpackage/dv2.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("aZ_EqRTZPhz0lVm463cdfqK1463K5OwyKxo_n3Znh4g=", dv2Var, 3);
18:         pluginGeneratedSerialDescriptor.k("kind", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageIds", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/dvt.java:160`
```text
158:                                     if (((Boolean) dzn.p(dznVar, fmi.Z0, false, null, 14)).booleanValue()) {
159:                                         int iB = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
160:                                         gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB))), 10);
161:                                         this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB), null, 4, null));
162:                                         ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:167`
```text
165:                                 } else {
166:                                     int iB2 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
167:                                     gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB2))), 10);
168:                                     this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB2), null, 4, null));
169:                                     ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:251`
```text
249:                                         if (((Boolean) dzn.p(dznVar, fmi.Z0, false, null, 14)).booleanValue()) {
250:                                             int iB3 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
251:                                             gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB3))), 10);
252:                                             this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB3), null, 4, null));
253:                                             ((mk3) this.g).f(str, false);
```

### `sources/defpackage/dvt.java:258`
```text
256:                                     } else {
257:                                         int iB4 = (int) a4w.B(irm.u(jC, qrm.SECONDS), 0L, 2147483647L);
258:                                         gev.d(gevVar, "Navigating to last viewed conversation on cold start", null, dvv.D0(new g100("conversation_id", str), new g100("elapsed_seconds", new Integer(iB4))), 10);
259:                                         this.f.i(new ChatgptBackToLastViewedConversation(str, new Integer(iB4), null, 4, null));
260:                                         ((mk3) this.g).f(str, false);
```

### `sources/defpackage/e1i.java:17`
```text
15:         a = e1iVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("5kN3qJBQ0HzIX-wny6ClEEuY_3rPFeTgtsdZgA8rtbk=", e1iVar, 3);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("model", false);
19:         pluginGeneratedSerialDescriptor.k("offset", true);
```

### `sources/defpackage/e8u.java:31`
```text
29:         pluginGeneratedSerialDescriptor.k("userId", true);
30:         pluginGeneratedSerialDescriptor.k("accountId", true);
31:         pluginGeneratedSerialDescriptor.k("conversationId", true);
32:         pluginGeneratedSerialDescriptor.k("originalMessageId", false);
33:         pluginGeneratedSerialDescriptor.k("messages", true);
```

### `sources/defpackage/e9.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("status", false);
19:         pluginGeneratedSerialDescriptor.k("handoffId", false);
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
```

### `sources/defpackage/e9.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
23:         pluginGeneratedSerialDescriptor.k("destinationUserMessageId", false);
24:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/edc0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("xmZhMBoKPT6JLy3kQ-8oAvquiD_1oQYl5MI5iliJ-Ac=", edc0Var, 2);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
20:     }
```

### `sources/defpackage/edq.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("title", false);
21:         pluginGeneratedSerialDescriptor.k("snippet", false);
22:         pluginGeneratedSerialDescriptor.k("conversationId", false);
23:         pluginGeneratedSerialDescriptor.k("messageId", false);
24:         pluginGeneratedSerialDescriptor.k("isArchived", false);
```

### `sources/defpackage/ep6.java:18`
```text
16:         a = ep6Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("dC1TGvyVE4mVOhxGv-Ay9aFewKUBI3Six72HPXOc1RY=", ep6Var, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("products", false);
```

### `sources/defpackage/eq20.java:18`
```text
16:         a = eq20Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("R0kus8NLdn-rQ5FWLO4hMPKsJefJMgjBoDjKRiwh4gs=", eq20Var, 6);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("productQuery", false);
```

### `sources/defpackage/es20.java:19`
```text
17:         a = es20Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("TJGWkVNMjpkJRxoHV3JAxZ3g6osbD1s7LXEOAAsx4Ew=", es20Var, 6);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("supportedEncodings", true);
```

### `sources/defpackage/etg.java:18`
```text
16:         a = etgVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("orqmOZs-C-1F1zdO-PvZUCzK7iq4swHz7fFIBRvUjDI=", etgVar, 4);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("parentSnapshot", true);
```

### `sources/defpackage/evt.java:17`
```text
15:         a = evtVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("btBiFrvPkO1DFG9HWim_O9VYkuTw1RoEuKjLbx4lm3U=", evtVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("type", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ezg.java:11`
```text
9: import android.net.Uri;
10: import android.os.Build;
11: import android.service.notification.StatusBarNotification;
12: import com.openai.chatgpt.R;
13: import java.util.Collection;
```

### `sources/defpackage/ezg.java:97`
```text
95:         if (Build.VERSION.SDK_INT >= 26) {
96:             try {
97:                 List<StatusBarNotification> listC = this.f.c();
98:                 if (!(listC instanceof Collection) || !listC.isEmpty()) {
99:                     for (StatusBarNotification statusBarNotification : listC) {
```

### `sources/defpackage/ezg.java:99`
```text
97:                 List<StatusBarNotification> listC = this.f.c();
98:                 if (!(listC instanceof Collection) || !listC.isEmpty()) {
99:                     for (StatusBarNotification statusBarNotification : listC) {
100:                         if (wnm.k(statusBarNotification.getTag(), str) && wnm.k(statusBarNotification.getNotification().getChannelId(), "responses")) {
101:                             return true;
```

### `sources/defpackage/ezg.java:100`
```text
98:                 if (!(listC instanceof Collection) || !listC.isEmpty()) {
99:                     for (StatusBarNotification statusBarNotification : listC) {
100:                         if (wnm.k(statusBarNotification.getTag(), str) && wnm.k(statusBarNotification.getNotification().getChannelId(), "responses")) {
101:                             return true;
102:                         }
```

### `sources/defpackage/f53.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("7CbcfmK_DHcbhJX6su6kQZfUhLwnoJpfZFP2Pwzl8ZE=", f53Var, 4);
17:         pluginGeneratedSerialDescriptor.k("kind", true);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("contentReferenceIndex", false);
```

### `sources/defpackage/fda.java:132`
```text
130:                 s3b s3bVar7 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesNextAssistantTurnButtonClicked");
131:                 sj20 sj20Var4 = da90.b;
132:                 s3bVar7.a("conversationId", sj20Var4, (12 & 8) == 0);
133:                 s3bVar7.a("fullscreenSessionId", sj20Var4, (12 & 8) == 0);
134:                 s3bVar7.a("messageId", sj20Var4, (12 & 8) == 0);
```

### `sources/defpackage/fda.java:144`
```text
142:                 s3b s3bVar8 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesPreviousAssistantTurnButtonClicked");
143:                 sj20 sj20Var5 = da90.b;
144:                 s3bVar8.a("conversationId", sj20Var5, (12 & 8) == 0);
145:                 s3bVar8.a("fullscreenSessionId", sj20Var5, (12 & 8) == 0);
146:                 s3bVar8.a("messageId", sj20Var5, (12 & 8) == 0);
```

### `sources/defpackage/fda.java:156`
```text
154:                 s3b s3bVar9 = new s3b("protobuf_analytics_events.v1.ChatgptPlacesSearchHereButtonClicked");
155:                 sj20 sj20Var6 = da90.b;
156:                 s3bVar9.a("conversationId", sj20Var6, (12 & 8) == 0);
157:                 s3bVar9.a("fullscreenSessionId", sj20Var6, (12 & 8) == 0);
158:                 s3bVar9.a("messageId", sj20Var6, (12 & 8) == 0);
```

### `sources/defpackage/fei.java:18`
```text
16:         a = feiVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("BXFWgCbyfBzMa7ZfbGE5SPaWKIHlyKYIcGLFJ0bBnJw=", feiVar, 2);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("metadata", false);
20:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/fga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesNextAssistantTurnButtonClicked chatgptPlacesNextAssistantTurnButtonClicked = (ChatgptPlacesNextAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/fga.java:15`
```text
13:         ChatgptPlacesNextAssistantTurnButtonClicked chatgptPlacesNextAssistantTurnButtonClicked = (ChatgptPlacesNextAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesNextAssistantTurnButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesNextAssistantTurnButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/fha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductGroupClickedEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductGroupClickedEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupClickedEvent.getConversation_id());
22:         }
```

### `sources/defpackage/fha.java:21`
```text
19:         }
20:         if (chatgptProductGroupClickedEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupClickedEvent.getConversation_id());
22:         }
23:         if (chatgptProductGroupClickedEvent.getMessage_id() != null) {
```

### `sources/defpackage/fqk.java:23`
```text
21:         pluginGeneratedSerialDescriptor.l(new k3l());
22:         pluginGeneratedSerialDescriptor.k("allowLibraryDelete", true);
23:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
24:         descriptor = pluginGeneratedSerialDescriptor;
25:     }
```

### `sources/defpackage/frt.java:20`
```text
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("OiPgJ0kykXun48pr7VgqwTYZU73cU4_My6qlPFGjpxQ=", frtVar, 10);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("intent", false);
22:         pluginGeneratedSerialDescriptor.k("contentTextLength", false);
```

### `sources/defpackage/fvw.java:35`
```text
33: 
34:     public final Object a(String str, String str2, String str3, rsg rsgVar) {
35:         return f(dvv.D0(new g100("conversationId", str), new g100("messageId", str2)), new bvw(this, str, str2, str3, null, (byte) 0), rsgVar);
36:     }
37: 
```

### `sources/defpackage/fvw.java:81`
```text
79: 
80:     public final Object c(String str, String str2, String str3, rsg rsgVar) {
81:         return f(dvv.D0(new g100("sharedConversationId", str), new g100("messageId", str2)), new bvw(this, str, str2, str3, null, (byte) 1), rsgVar);
82:     }
83: 
```

### `sources/defpackage/g310.java:18`
```text
16:         a = g310Var;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Gq7RMTAf_AsRCLj0rT9b_g891O5i_e_X5urlzZYNzI0=", g310Var, 1);
18:         pluginGeneratedSerialDescriptor.k("recordsByConversationId", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
20:     }
```

### `sources/defpackage/ga5.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("id", false);
20:         pluginGeneratedSerialDescriptor.k("updatedAt", true);
21:         pluginGeneratedSerialDescriptor.k("conversationId", true);
22:         pluginGeneratedSerialDescriptor.k("sourceConversationIsWorkMode", true);
23:         pluginGeneratedSerialDescriptor.k("title", false);
```

### `sources/defpackage/gcu.java:17`
```text
15:         a = gcuVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("SahdpmD8LEk9GTF9L2hH5XKkC8uhaugQXfI588se-ng=", gcuVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/gga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesPreviousAssistantTurnButtonClicked chatgptPlacesPreviousAssistantTurnButtonClicked = (ChatgptPlacesPreviousAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/gga.java:15`
```text
13:         ChatgptPlacesPreviousAssistantTurnButtonClicked chatgptPlacesPreviousAssistantTurnButtonClicked = (ChatgptPlacesPreviousAssistantTurnButtonClicked) aVar;
14:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesPreviousAssistantTurnButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesPreviousAssistantTurnButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/gha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductGroupShownEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductGroupShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupShownEvent.getConversation_id());
22:         }
```

### `sources/defpackage/gha.java:21`
```text
19:         }
20:         if (chatgptProductGroupShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductGroupShownEvent.getConversation_id());
22:         }
23:         if (chatgptProductGroupShownEvent.getMessage_id() != null) {
```

### `sources/defpackage/go1.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("2Smk92UHZvzQ9Wvfuj2A4PjO7YMJD8wn0gYorEhxjYo=", go1Var, 6);
17:         pluginGeneratedSerialDescriptor.k("url", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("title", true);
20:         pluginGeneratedSerialDescriptor.k("preview", true);
```

### `sources/defpackage/gtw.java:17`
```text
15:         a = gtwVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("V9GeZRQL7IPP58Qe1RNpHLxiP5tdJA__gueyZsu58Lk=", gtwVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/guw.java:17`
```text
15:         a = guwVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("PaUo0MxLOPYmRKEc3l1YELKUJ6pDkMpsUqeL-7D67vo=", guwVar, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("id", false);
19:         pluginGeneratedSerialDescriptor.k("userId", false);
```

### `sources/defpackage/h9.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("status", false);
19:         pluginGeneratedSerialDescriptor.k("handoffId", false);
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
```

### `sources/defpackage/h9.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
21:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
22:         pluginGeneratedSerialDescriptor.k("destinationConversationId", false);
23:         pluginGeneratedSerialDescriptor.k("destinationUserMessageId", false);
24:         pluginGeneratedSerialDescriptor.k("restorationSnapshot", true);
```

### `sources/defpackage/hdc0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("nsTVr1i5xFN5Er6CXjDLrq11mpJYF_nKVrMcd1Dky5I=", hdc0Var, 5);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("workConversationId", false);
20:         pluginGeneratedSerialDescriptor.k("restoredUserMessageId", false);
```

### `sources/defpackage/hdc0.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("workConversationId", false);
20:         pluginGeneratedSerialDescriptor.k("restoredUserMessageId", false);
21:         pluginGeneratedSerialDescriptor.k("restoredModelSlug", false);
```

### `sources/defpackage/hga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesSearchHereButtonClicked chatgptPlacesSearchHereButtonClicked = (ChatgptPlacesSearchHereButtonClicked) aVar;
14:         if (chatgptPlacesSearchHereButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesSearchHereButtonClicked.getConversation_id());
16:         }
```

### `sources/defpackage/hga.java:15`
```text
13:         ChatgptPlacesSearchHereButtonClicked chatgptPlacesSearchHereButtonClicked = (ChatgptPlacesSearchHereButtonClicked) aVar;
14:         if (chatgptPlacesSearchHereButtonClicked.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesSearchHereButtonClicked.getConversation_id());
16:         }
17:         if (chatgptPlacesSearchHereButtonClicked.getFullscreen_session_id() != null) {
```

### `sources/defpackage/hij.java:6`
```text
4: import kotlin.Metadata;
5: 
6: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B-\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0018
8: public final class hij extends b {
```

### `sources/defpackage/hij.java:7`
```text
5: 
6: @o2d0(propertyReplacements = "", schema = "'conversationId':s?,'messageId':s?,'contentReferenceIndex':d@?", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u0006\n\u0002\b\t\b\u0007\u0018\u00002\u00020\u0001B-\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005¢\u0006\u0004\b\u0007\u0010\bR\u0018\u0010\t\u001a\u0004\u0018\u00010\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0018
8: public final class hij extends b {
9:     private Double _contentReferenceIndex;
```

### `sources/defpackage/hij.java:10`
```text
8: public final class hij extends b {
9:     private Double _contentReferenceIndex;
10:     private String _conversationId;
11:     private String _messageId;
12: 
```

### `sources/defpackage/hij.java:14`
```text
12: 
13:     public hij(String str, String str2, Double d) {
14:         this._conversationId = str;
15:         this._messageId = str2;
16:         this._contentReferenceIndex = d;
```

### `sources/defpackage/i1q.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("saveId", true);
18:         pluginGeneratedSerialDescriptor.k("projectId", true);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationTitle", true);
21:         pluginGeneratedSerialDescriptor.k("title", true);
```

### `sources/defpackage/i3i.java:187`
```text
185:         this.c.b(jygVar, stringExtra);
186:         if (jygVar == jyg.ScreenShare && stringExtra != null) {
187:             String stringExtra3 = intent.getStringExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID");
188:             String str = stringExtra3 != null ? stringExtra3 : null;
189:             n3i n3iVar = this.b;
```

### `sources/defpackage/i53.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("2RSRwgE7HSL3QFKJ45raMqqb0_5bsJ7GjneqHZr5fn4=", i53Var, 6);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("writingBlockId", false);
21:         pluginGeneratedSerialDescriptor.k("feedback", false);
```

### `sources/defpackage/idi.java:17`
```text
15:         a = idiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("swwt_wCse71rBTYUEnPQgLIGAC0MqiObKIjCBtzmra0=", idiVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("inputMessage", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/iga.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptPlacesTimeToFirstPin chatgptPlacesTimeToFirstPin = (ChatgptPlacesTimeToFirstPin) aVar;
14:         if (chatgptPlacesTimeToFirstPin.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesTimeToFirstPin.getConversation_id());
16:         }
```

### `sources/defpackage/iga.java:15`
```text
13:         ChatgptPlacesTimeToFirstPin chatgptPlacesTimeToFirstPin = (ChatgptPlacesTimeToFirstPin) aVar;
14:         if (chatgptPlacesTimeToFirstPin.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptPlacesTimeToFirstPin.getConversation_id());
16:         }
17:         if (chatgptPlacesTimeToFirstPin.getMessage_id() != null) {
```

### `sources/defpackage/ilh.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("continued_in_work_banner", ilhVar, 2);
17:         pluginGeneratedSerialDescriptor.k("sourceMessageId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.m(new v10(false, (byte) 16));
20:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/iqk.java:22`
```text
20:         pluginGeneratedSerialDescriptor.k("source", true);
21:         pluginGeneratedSerialDescriptor.k("allowFileExport", true);
22:         pluginGeneratedSerialDescriptor.k("viewOriginalChatConversationId", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
24:     }
```

### `sources/defpackage/j1l.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("referenceStartIdx", false);
20:         pluginGeneratedSerialDescriptor.k("referenceEndIdx", false);
21:         pluginGeneratedSerialDescriptor.k("sheetConversationId", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
23:     }
```

### `sources/defpackage/jhj.java:7`
```text
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'payload':m<s,u>,'conversationId':s?,'sourceMessageId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
```

### `sources/defpackage/jhj.java:8`
```text
6: 
7: @o2d0(propertyReplacements = "", schema = "'payload':m<s,u>,'conversationId':s?,'sourceMessageId':s?", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
10:     private String _conversationId;
```

### `sources/defpackage/jhj.java:10`
```text
8: @Metadata(d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\u0000\n\u0002\b\u000b\b\u0007\u0018\u00002\u00020\u0001B7\b\u0017\u0012\u0014\u0010\u0005\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0012\u0006\u0012\u0004\u0018\u00010\u00040\u0002\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003¢\u0006\u0004\b\b\u0010\tR$\u0010\n\u001a\u0010\u0012\u0004\u0012\u00020\u0003\u0
9: public final class jhj extends b {
10:     private String _conversationId;
11:     private Map<String, ? extends Object> _payload;
12:     private String _sourceMessageId;
```

### `sources/defpackage/jhj.java:16`
```text
14:     public jhj(Map<String, ? extends Object> map, String str, String str2) {
15:         this._payload = map;
16:         this._conversationId = str;
17:         this._sourceMessageId = str2;
18:     }
```

### `sources/defpackage/jsa.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoicePreFirstAssistantUserTurnFinished chatgptVoicePreFirstAssistantUserTurnFinished = (ChatgptVoicePreFirstAssistantUserTurnFinished) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id());
16:         }
```

### `sources/defpackage/jsa.java:15`
```text
13:         ChatgptVoicePreFirstAssistantUserTurnFinished chatgptVoicePreFirstAssistantUserTurnFinished = (ChatgptVoicePreFirstAssistantUserTurnFinished) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnFinished.getConversation_id());
16:         }
17:         if (chatgptVoicePreFirstAssistantUserTurnFinished.getDuration_ms() != null) {
```

### `sources/defpackage/jvt.java:19`
```text
17:         pluginGeneratedSerialDescriptor.k("conversation_reference", true);
18:         pluginGeneratedSerialDescriptor.k("localViewedAt", true);
19:         pluginGeneratedSerialDescriptor.k("remote_conversation_id", true);
20:         pluginGeneratedSerialDescriptor.k("local_conversation_id", true);
21:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
```

### `sources/defpackage/jvt.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("localViewedAt", true);
19:         pluginGeneratedSerialDescriptor.k("remote_conversation_id", true);
20:         pluginGeneratedSerialDescriptor.k("local_conversation_id", true);
21:         pluginGeneratedSerialDescriptor.k("conversationOrigin", true);
22:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/k1i.java:17`
```text
15:         a = k1iVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("IrZwQ8hG4GykRMAz22Z2TfE32CPdXV7OwuaJEfCtzf4=", k1iVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("token", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kc2.java:21`
```text
19:         pluginGeneratedSerialDescriptor.k("width", true);
20:         pluginGeneratedSerialDescriptor.k("height", true);
21:         pluginGeneratedSerialDescriptor.k("conversationId", true);
22:         pluginGeneratedSerialDescriptor.k("generatedWithThinkingModel", true);
23:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kcb0.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Ahgs58qTwF4L2qWhjLj-pliK2x4F_jdc_BimewMvc7M=", kcb0Var, 4);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("version", true);
```

### `sources/defpackage/kdh.java:17`
```text
15:         a = kdhVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("5-q4VkbWOt09LSFMpkdNDccgIYC8c1pB2UBQTvDpc_k=", kdhVar, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationOwnerId", false);
19:         pluginGeneratedSerialDescriptor.k("gizmoId", false);
```

### `sources/defpackage/kei.java:17`
```text
15:         a = keiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("a9RI58khYWjF-AxTRF6a31v0wslUMUdOXDwOv7brKc4=", keiVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("title", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kmi.java:4`
```text
2: 
3: public abstract class kmi {
4:     public static final vk30 a = new vk30("Conversations", dvv.D0(new g100(-2052184858, "MessageChunk.sq:saveMessageChunk"), new g100(-625220995, "MessageChunk.sq:deleteByMessageId"), new g100(-164501711, "Message.sq:delete"), new g100(-127674581, "Conversation.sq:delete"), new g100(-112721744, "Message.sq:deleteAll"), new g100(-102650410, "Conversation.sq:exists"), new g100(-81574436, "Conversation.sq:exists"), new g100(-41583637, "Conversation.sq:getAll"), new g100(23991353, "Conversation.sq:i
5: }
```

### `sources/defpackage/ksa.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoicePreFirstAssistantUserTurnStarted chatgptVoicePreFirstAssistantUserTurnStarted = (ChatgptVoicePreFirstAssistantUserTurnStarted) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id());
16:         }
```

### `sources/defpackage/ksa.java:15`
```text
13:         ChatgptVoicePreFirstAssistantUserTurnStarted chatgptVoicePreFirstAssistantUserTurnStarted = (ChatgptVoicePreFirstAssistantUserTurnStarted) aVar;
14:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoicePreFirstAssistantUserTurnStarted.getConversation_id());
16:         }
17:         if (chatgptVoicePreFirstAssistantUserTurnStarted.getUser_turn_index() != null) {
```

### `sources/defpackage/ku9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptAssistantResponseEndVisible.getAssistant_message_id());
16:         }
17:         if (chatgptAssistantResponseEndVisible.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptAssistantResponseEndVisible.getConversation_id());
19:         }
```

### `sources/defpackage/ku9.java:18`
```text
16:         }
17:         if (chatgptAssistantResponseEndVisible.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptAssistantResponseEndVisible.getConversation_id());
19:         }
20:         if (chatgptAssistantResponseEndVisible.getUser_prompt_message_id() != null) {
```

### `sources/defpackage/kx1.java:17`
```text
15:         a = kx1Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("conversation", kx1Var, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.m(new v10((byte) 3));
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/kze0.java:17`
```text
15:         a = kze0Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("h_nzZnyLXkgIUw8OtJV3zGyj8wO-k2_kJsBNHDtvwnU=", kze0Var, 7);
17:         pluginGeneratedSerialDescriptor.k("conversationId", true);
18:         pluginGeneratedSerialDescriptor.k("gizmoId", false);
19:         pluginGeneratedSerialDescriptor.k("nonce", false);
```

### `sources/defpackage/kzi.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("items", false);
19:         pluginGeneratedSerialDescriptor.k("shippingAddress", true);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
```

### `sources/defpackage/l7a.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptImageLightboxMetadata chatgptImageLightboxMetadata = (ChatgptImageLightboxMetadata) aVar;
14:         if (chatgptImageLightboxMetadata.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptImageLightboxMetadata.getConversation_id());
16:         }
```

### `sources/defpackage/l7a.java:15`
```text
13:         ChatgptImageLightboxMetadata chatgptImageLightboxMetadata = (ChatgptImageLightboxMetadata) aVar;
14:         if (chatgptImageLightboxMetadata.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptImageLightboxMetadata.getConversation_id());
16:         }
17:         if (chatgptImageLightboxMetadata.getFile_id() != null) {
```

### `sources/defpackage/ldz.java:23`
```text
21:         pluginGeneratedSerialDescriptor.k("url", true);
22:         pluginGeneratedSerialDescriptor.k("urls", true);
23:         pluginGeneratedSerialDescriptor.k("conversationId", true);
24:         pluginGeneratedSerialDescriptor.k("assetId", true);
25:         pluginGeneratedSerialDescriptor.k("buttonType", true);
```

### `sources/defpackage/lt.java:62`
```text
60:         byte b = 2;
61:         yn ynVar = new yn(mz80VarM, mz80VarM3, new mm(3, psgVar, b), (byte) 2);
62:         asg asgVarD = vqi.d(asgVarA, "ActivelyStreamingConversationRepository/conversationIds");
63:         g6h g6hVar = zc70.a;
64:         this.t = cea0.R(ynVar, asgVarD, g6hVar, ggnVar);
```

### `sources/defpackage/m56.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("eventType", false);
19:         pluginGeneratedSerialDescriptor.k("eventCtaId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationId", false);
21:         pluginGeneratedSerialDescriptor.k("messageId", false);
22:         pluginGeneratedSerialDescriptor.k("benefitId", true);
```

### `sources/defpackage/m6w.java:30`
```text
28:         pluginGeneratedSerialDescriptor.k("isArchived", true);
29:         pluginGeneratedSerialDescriptor.k("assetPointer", true);
30:         pluginGeneratedSerialDescriptor.k("conversationId", true);
31:         pluginGeneratedSerialDescriptor.k("createdAt", true);
32:         pluginGeneratedSerialDescriptor.k("prompt", true);
```

### `sources/defpackage/m9l.java:17`
```text
15:         a = m9lVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("RNfkCBCzr-0bkiZfnW-Ms3CNyGVkTH2QHyOSMGNXna4=", m9lVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/mdi.java:17`
```text
15:         a = mdiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("BaUO8q-KuTCMTJqFmVaxoaAxdc0ZFSU-y0TNHGxPEPE=", mdiVar, 4);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("marker", false);
```

### `sources/defpackage/mk40.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("wc4pSfZn_zsPaKWjaWuu3OAHRSH4IsFQrOURBRbSaZk=", mk40Var, 4);
17:         pluginGeneratedSerialDescriptor.k("accountId", false);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("deviceId", false);
20:         pluginGeneratedSerialDescriptor.k("parentMessageId", false);
```

### `sources/defpackage/mnn.java:36`
```text
34:         ul0 ul0Var = ul0.h;
35:         g100 g100Var = new g100("message_id", str2);
36:         g100 g100Var2 = new g100("conversation_id", str);
37:         g100 g100Var3 = new g100("sidebar_session_id", this.c);
38:         g100 g100Var4 = new g100("entity_name", str3);
```

### `sources/defpackage/mnn.java:55`
```text
53:         ul0 ul0Var = ul0.g;
54:         g100 g100Var = new g100("message_id", str2);
55:         g100 g100Var2 = new g100("conversation_id", str);
56:         g100 g100Var3 = new g100("sidebar_session_id", this.c);
57:         g100 g100Var4 = new g100("entity_name", lnnVar.a);
```

### `sources/defpackage/mp9.java:18`
```text
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("accepted", mp9Var, 4);
17:         pluginGeneratedSerialDescriptor.k("handoffId", false);
18:         pluginGeneratedSerialDescriptor.k("sourceConversationId", false);
19:         pluginGeneratedSerialDescriptor.k("sourceUserMessageId", false);
20:         pluginGeneratedSerialDescriptor.k("canUndo", false);
```

### `sources/defpackage/mu9.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptBackToLastViewedConversation chatgptBackToLastViewedConversation = (ChatgptBackToLastViewedConversation) aVar;
14:         if (chatgptBackToLastViewedConversation.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptBackToLastViewedConversation.getConversation_id());
16:         }
```

### `sources/defpackage/mu9.java:15`
```text
13:         ChatgptBackToLastViewedConversation chatgptBackToLastViewedConversation = (ChatgptBackToLastViewedConversation) aVar;
14:         if (chatgptBackToLastViewedConversation.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptBackToLastViewedConversation.getConversation_id());
16:         }
17:         if (chatgptBackToLastViewedConversation.getLast_viewed_age_seconds() != null) {
```

### `sources/defpackage/mv1.java:17`
```text
15:         a = mv1Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("Ne8cMSk9rjMRAArnKtc-MKDhH0iCSDnudIs76e6MQ3o=", mv1Var, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/mw9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockEditButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockEditButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockEditButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/mw9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockEditButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockEditButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockEditButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/myr.java:18`
```text
16:         a = myrVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("nYw9PplnhJOmYiYc1VEeAFFFKFyAEHKOEV3guQKGp1Q=", myrVar, 7);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("count", false);
20:         pluginGeneratedSerialDescriptor.k("renderFormat", false);
```

### `sources/defpackage/n32.java:17`
```text
15:         a = n32Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("uBk-WFOqpx_gDP796Rs-Qeb6uEOVaHaVazZkpPk2hWQ=", n32Var, 3);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("currentNodeId", true);
19:         pluginGeneratedSerialDescriptor.k("isAnonymous", false);
```

### `sources/defpackage/nav.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("hasPin", true);
19:         pluginGeneratedSerialDescriptor.k("projectId", true);
20:         pluginGeneratedSerialDescriptor.k("conversationIds", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
```

### `sources/defpackage/ne90.java:99`
```text
97:             }
98:             if (str2 != null) {
99:                 intentPutExtra.putExtra("conversation_id", str2);
100:             }
101:         }
```

### `sources/defpackage/nhi.java:25`
```text
23:         dgt dgtVarC = dhtVar.c();
24:         c cVarL = jht.l(dhtVar.h());
25:         String str = ((zch) dgtVarC.a(zch.Companion.serializer(), (b) dvv.A0(cVarL, "conversation_id"))).a;
26:         b bVar = (b) cVarL.get("update_type");
27:         if (bVar == null || (strA = jht.m(bVar).a()) == null) {
```

### `sources/defpackage/no9.java:19`
```text
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("47mQTng_hDfBuFNNAWhQ9muqB1JXSGIws89ysRaZwcQ=", no9Var, 6);
18:         pluginGeneratedSerialDescriptor.k("id", false);
19:         pluginGeneratedSerialDescriptor.k("conversationId", true);
20:         pluginGeneratedSerialDescriptor.k("author", false);
21:         pluginGeneratedSerialDescriptor.k("recipient", true);
```

### `sources/defpackage/nph.java:17`
```text
15:         a = nphVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("L-3v4JYFDHblHYPrHGsLLYfF6KU-GKQ5ZQasXb3JW0w=", nphVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("turnExchangeId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/nra.java:14`
```text
12:     public final void a(tgf tgfVar, SerialDescriptor serialDescriptor, a aVar, int i) {
13:         ChatgptVoiceCotTap chatgptVoiceCotTap = (ChatgptVoiceCotTap) aVar;
14:         if (chatgptVoiceCotTap.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoiceCotTap.getConversation_id());
16:         }
```

### `sources/defpackage/nra.java:15`
```text
13:         ChatgptVoiceCotTap chatgptVoiceCotTap = (ChatgptVoiceCotTap) aVar;
14:         if (chatgptVoiceCotTap.getConversation_id() != null) {
15:             tgfVar.y(serialDescriptor, i, da90.a, chatgptVoiceCotTap.getConversation_id());
16:         }
17:         if (chatgptVoiceCotTap.getMessage_id() != null) {
```

### `sources/defpackage/nsh.java:17`
```text
15:         a = nshVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("qB5oUqtRHJmrMgXVDR1N-lb9TTstceCcPakaHFz1Teg=", nshVar, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         descriptor = pluginGeneratedSerialDescriptor;
19:     }
```

### `sources/defpackage/nw9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockFullScreenButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockFullScreenButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockFullScreenButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/nw9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockFullScreenButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockFullScreenButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockFullScreenButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/nyk.java:17`
```text
15:         a = nykVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("existing-conversation", nykVar, 1);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.m(new v10((byte) 21));
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/o210.java:17`
```text
15:         a = o210Var;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("F7tT5sfvHK8L6_SVEozg8ZEyBmfhrnzw5r-LzAs2lNU=", o210Var, 6);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/o48.java:210`
```text
208:         if (i2 == 0) {
209:             ct40.j(objA);
210:             ml30 ml30VarR2 = this.a.r2(new Integer(750218886), "DELETE\nFROM DBMessage\nWHERE conversationId = ?", 1, new l0x(this, str, (byte) 0));
211:             n0xVar.p = 1;
212:             objA = ml30VarR2.a(n0xVar);
```

### `sources/defpackage/o48.java:357`
```text
355:         if (i2 == 0) {
356:             ct40.j(objA);
357:             ml30 ml30VarR2 = this.a.r2(new Integer(1180159107), "INSERT OR REPLACE\nINTO DBMessage (id, conversationId)\nVALUES (?, ?)", 2, new svw(this, lgjVar, b));
358:             p0xVar.p = 1;
359:             objA = ml30VarR2.a(p0xVar);
```

### `sources/defpackage/oei.java:17`
```text
15:         a = oeiVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("3ojDDFJ742G6_C65HYW-_cHzBM03lkKeOAF22_7KdW0=", oeiVar, 4);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("numVariantsInStream", false);
19:         pluginGeneratedSerialDescriptor.k("displayTreatment", true);
```

### `sources/defpackage/oh40.java:24`
```text
22:         pluginGeneratedSerialDescriptor.k("calpicoRoomId", true);
23:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
24:         pluginGeneratedSerialDescriptor.k("conversationId", true);
25:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
26:         pluginGeneratedSerialDescriptor.k("shareId", true);
```

### `sources/defpackage/oh40.java:25`
```text
23:         pluginGeneratedSerialDescriptor.k("calpicoMessageId", true);
24:         pluginGeneratedSerialDescriptor.k("conversationId", true);
25:         pluginGeneratedSerialDescriptor.k("sharedConversationId", true);
26:         pluginGeneratedSerialDescriptor.k("shareId", true);
27:         pluginGeneratedSerialDescriptor.k("productId", true);
```

### `sources/defpackage/oha.java:20`
```text
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptProductOfferListShownEvent.getContent_reference_type());
19:         }
20:         if (chatgptProductOfferListShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductOfferListShownEvent.getConversation_id());
22:         }
```

### `sources/defpackage/oha.java:21`
```text
19:         }
20:         if (chatgptProductOfferListShownEvent.getConversation_id() != null) {
21:             tgfVar.y(serialDescriptor, i + 2, da90.a, chatgptProductOfferListShownEvent.getConversation_id());
22:         }
23:         if (chatgptProductOfferListShownEvent.getMessage_id() != null) {
```

### `sources/defpackage/oi60.java:19`
```text
17:         a = oi60Var;
18:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("l0fa4MYmh_C5r1ScAmZBEVikBeML7O6wOGl96O1bmVI=", oi60Var, 12);
19:         pluginGeneratedSerialDescriptor.k("conversationId", false);
20:         pluginGeneratedSerialDescriptor.k("messageId", false);
21:         pluginGeneratedSerialDescriptor.k("index", false);
```

### `sources/defpackage/okk.java:17`
```text
15:         a = okkVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("jmN2Wscrb0V9UllU--TXk-lckBxOlKGdDV8c0qL13o8=", okkVar, 2);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("messageId", false);
19:         descriptor = pluginGeneratedSerialDescriptor;
```

### `sources/defpackage/ot.java:89`
```text
87: 
88:     public static void G(NotificationChannel notificationChannel, String str, String str2) {
89:         notificationChannel.setConversationId(str, str2);
90:     }
91: 
```

### `sources/defpackage/ot.java:147`
```text
145:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_PARENT_CHANNEL_ID", str3);
146:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CHANNEL_ID", xxgVar.c);
147:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_TAG", xxgVar.d);
148:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_INT_ID", xxgVar.e);
149:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str4);
```

### `sources/defpackage/ot.java:150`
```text
148:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_INT_ID", xxgVar.e);
149:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str4);
150:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str);
151:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_NOTIFICATION_ID", str2);
152:         intent.putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
```

### `sources/defpackage/ot.java:161`
```text
159: 
160:     public static final PendingIntent d(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
161:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
162:         if (bundle != null) {
163:             intentPutExtra.putExtras(bundle);
```

### `sources/defpackage/ot.java:169`
```text
167: 
168:     public static final Intent e(Application application, Uri uri, String str, String str2, jyg jygVar, Bundle bundle) {
169:         Intent intentPutExtra = zc80.I(application, uri, true).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_CONVERSATION_ID", str).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SHORTCUT_ID", str2).putExtra("com.openai.feature.notification.CONVERSATION_BUBBLE_SOURCE", jygVar.a);
170:         if (bundle != null) {
171:             intentPutExtra.putExtras(bundle);
```

### `sources/defpackage/ot.java:186`
```text
184:         NotificationChannel notificationChannel2 = new NotificationChannel(str2, str4, notificationChannel.getImportance());
185:         if (i >= 30) {
186:             notificationChannel2.setConversationId(str, str3);
187:         }
188:         notificationChannel2.setAllowBubbles(true);
```

### `sources/defpackage/ot.java:326`
```text
324: 
325:     public static String q(NotificationChannel notificationChannel) {
326:         return notificationChannel.getConversationId();
327:     }
328: 
```

### `sources/defpackage/ow9.java:17`
```text
15:             tgfVar.y(serialDescriptor, i, wh6.a, chatgptCodeBlockPreviewButtonClicked.getClient_previewable());
16:         }
17:         if (chatgptCodeBlockPreviewButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockPreviewButtonClicked.getConversation_id());
19:         }
```

### `sources/defpackage/ow9.java:18`
```text
16:         }
17:         if (chatgptCodeBlockPreviewButtonClicked.getConversation_id() != null) {
18:             tgfVar.y(serialDescriptor, i + 1, da90.a, chatgptCodeBlockPreviewButtonClicked.getConversation_id());
19:         }
20:         if (chatgptCodeBlockPreviewButtonClicked.getLanguage() != null) {
```

### `sources/defpackage/p0h.java:18`
```text
16:         a = p0hVar;
17:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("f_XXtjAPVPPJG_9sQwjWWOKsSKIEwwJgCMnxyBSxrx0=", p0hVar, 3);
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationIds", false);
```

### `sources/defpackage/p0h.java:20`
```text
18:         pluginGeneratedSerialDescriptor.k("conversationId", false);
19:         pluginGeneratedSerialDescriptor.k("messageId", false);
20:         pluginGeneratedSerialDescriptor.k("conversationIds", false);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
```

### `sources/defpackage/p1i.java:17`
```text
15:         a = p1iVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("T9PfM963scTm2G9tXtvgDU1km74YM_YoPxahAog_iy8=", p1iVar, 5);
17:         pluginGeneratedSerialDescriptor.k("conversationId", false);
18:         pluginGeneratedSerialDescriptor.k("active", false);
19:         pluginGeneratedSerialDescriptor.k("protectionType", false);
```

### `sources/defpackage/p84.java:25`
```text
23:         pluginGeneratedSerialDescriptor.k("questions", false);
24:         pluginGeneratedSerialDescriptor.k("answersByQuestionIndex", false);
25:         pluginGeneratedSerialDescriptor.k("conversationId", true);
26:         descriptor = pluginGeneratedSerialDescriptor;
27:     }
```

_Hits captured: 180 (cap 180)_
