# VOICE_ENTRY

## `com/openai/feature/codexremote/impl/voice/CodexVoiceSdpExchangeException.java`
### line 5
```java
1: package com.openai.feature.codexremote.impl.voice;
2: 
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0001\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/codexremote/impl/voice/CodexVoiceSdpExchangeException;", "Ljava/lang/IllegalStateException;", "Lkotlin/IllegalStateException;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: public final class CodexVoiceSdpExchangeException extends IllegalStateException {
7: }
```

## `com/openai/feature/codexremote/impl/voice/CodexVoiceStartException.java`
### line 5
```java
1: package com.openai.feature.codexremote.impl.voice;
2: 
3: import kotlin.Metadata;
4: 
5: @Metadata(d1 = {"\u0000\u000e\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002¨\u0006\u0003"}, d2 = {"Lcom/openai/feature/codexremote/impl/voice/CodexVoiceStartException;", "Ljava/lang/IllegalStateException;", "Lkotlin/IllegalStateException;", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
6: final class CodexVoiceStartException extends IllegalStateException {
7: }
```

## `com/openai/valdi/oai/platform/OAIPlatformServices.java`
### line 12
```java
8: import defpackage.o2d0;
9: import kotlin.Metadata;
10: 
11: @o2d0(propertyReplacements = "", schema = "'experimentService':r?:'[0]','apiService':r?:'[1]','loggingService':r?:'[2]','accountScope':r?:'[3]','analyticsService':r?:'[4]','authenticationService':r?:'[5]','accountFeatureService':r?:'[6]','accountSettingsService':r?:'[7]','accountCustomizationsService':r?:'[8]','petCatalogDataSource':r?:'[9]','voiceService':r?:'[10]','filePickerService':r?:'[11]','locationService':r?:'[12]','deviceIntegrityService':r?:'[13]'", typeReferences = {OAIExperimentService.class, OAIAPIService.class, OAILoggingService.class, OAIAccountScope.class, OAIAnalyticsService.class, OAIAuthenticationService.class, OAIAccountFeatureService.class, OAIAccountSettingsService.clas
12: @Metadata(d1 = {"\u0000^\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b \b\u0007\u0018\u00002\u00020\u0001B±\u0001\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0005\u001a\u0004\u0018\u00010\u0004\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0006\u0012\n\b\u00
13: public final class OAIPlatformServices extends b {
14:     private OAIAccountCustomizationsService _accountCustomizationsService;
15:     private OAIAccountFeatureService _accountFeatureService;
16:     private OAIAccountScope _accountScope;
```

## `com/openai/valdi/voice/VoiceCapabilities.java`
### line 8
```java
4: import defpackage.o2d0;
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'advancedVoice':b,'dictation':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/valdi/voice/VoiceCapabilities;", "Lcom/snap/valdi/utils/b;", "", "advancedVoice", "dictation", "<init>", "(ZZ)V", "_advancedVoice", "Z", "_dictation", "modules_oai_voice_service-oai_voice_service_api_kt_
9: public final class VoiceCapabilities extends b {
10:     private boolean _advancedVoice;
11:     private boolean _dictation;
12: 
```

## `com/openai/valdi/voice/VoiceFailure.java`
### line 8
```java
4: import defpackage.o2d0;
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'message':s", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001B\u0011\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002¢\u0006\u0004\b\u0004\u0010\u0005R\u0016\u0010\u0006\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0006\u0010\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/voice/VoiceFailure;", "Lcom/snap/valdi/utils/b;", "", "message", "<init>", "(Ljava/lang/String;)V", "_message", "Ljava/lang/String;", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceFailure extends b {
10:     private String _message;
11: 
12:     public VoiceFailure(String str) {
```

## `com/openai/valdi/voice/VoiceService.java`
### line 9
```java
5: import defpackage.t5d0;
6: import defpackage.uqe0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\bg\u0018\u00002\u00020\u0001J\b\u0010\u0002\u001a\u00020\u0003H&J\u0010\u0010\u0004\u001a\u00020\u00052\u0006\u0010\u0006\u001a\u00020\u0007H\u0016J\u0018\u0010\b\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000b2\u0006\u0010\f\u001a\u00020\rH&¨\u0006\u000e"}, d2 = {"Lcom/openai/valdi/voice/VoiceService;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "getCapabilities", "Lcom/openai/valdi/voice/VoiceCapabilities;", "pushToMarshaller", "", "marshaller", "Lcom/sna
10: @t5d0(propertyReplacements = "", proxyClass = uqe0.class, schema = "'getCapabilities':f|m|(): r:'[0]','start':f|m|(r:'[1]', r:'[2]'): r:'[3]'", typeReferences = {VoiceCapabilities.class, VoiceSessionInput.class, VoiceSessionListener.class, VoiceSession.class})
11: public interface VoiceService extends ValdiMarshallable {
12:     VoiceCapabilities getCapabilities();
13: 
```

## `com/openai/valdi/voice/VoiceServiceConfiguration.java`
### line 10
```java
6: import java.util.List;
7: import kotlin.Metadata;
8: 
9: @o2d0(propertyReplacements = "", schema = "'baseUrl':s,'requestHeaders':a<r:'[0]'>", typeReferences = {lpe0.class})
10: @Metadata(d1 = {"\u0000\u001a\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001f\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004¢\u0006\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u001c\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00050\u00048\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u000b\u0010\f¨\u0006\r"}, d2 = {"Lcom/openai/valdi/voice/VoiceServiceConfiguration;", "Lcom/snap/valdi/utils/b;", "", "baseUrl", "", "Llpe0;", "requestHeaders"
11: public final class VoiceServiceConfiguration extends b {
12:     private String _baseUrl;
13:     private List<lpe0> _requestHeaders;
14: 
```

## `com/openai/valdi/voice/VoiceServiceNativeModuleFactoryImpl.java`
### line 8
```java
4: import defpackage.w6y;
5: import defpackage.x6y;
6: import kotlin.Metadata;
7: 
8: @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\u0007¢\u0006\u0004\b\u0002\u0010\u0003J\u000f\u0010\u0005\u001a\u00020\u0004H\u0016¢\u0006\u0004\b\u0005\u0010\u0006¨\u0006\u0007"}, d2 = {"Lcom/openai/valdi/voice/VoiceServiceNativeModuleFactoryImpl;", "Lx6y;", "<init>", "()V", "Lw6y;", "onLoadModule", "()Lw6y;", "modules_oai_voice_service-oai_voice_service_android_impl_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceServiceNativeModuleFactoryImpl extends x6y {
10:     @Override
11:     public w6y onLoadModule() {
12:         return new my0();
```

## `com/openai/valdi/voice/VoiceSession.java`
### line 9
```java
5: import defpackage.ose0;
6: import defpackage.t5d0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u000f\u0010\t\u001a\u00020\u0002H&¢\u0006\u0004\b\t\u0010\u0004J\u0017\u0010\r\u001a\u00020\f2\u0006\u0010\u000b\u001a\u00020\nH\u0016¢\u0006\u0004\b\r\u0010\u000e¨\u0006\u000f"}, d2 = {"Lcom/openai/valdi/voice/VoiceSession;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "Lwec0;", "finish", "(
10: @t5d0(propertyReplacements = "", proxyClass = ose0.class, schema = "'finish':f|m|(),'setMuted':f|m|(b),'stop':f|m|()", typeReferences = {})
11: public interface VoiceSession extends ValdiMarshallable {
12:     void finish();
13: 
```

## `com/openai/valdi/voice/VoiceSessionInput.java`
### line 10
```java
6: import java.util.List;
7: import kotlin.Metadata;
8: 
9: @o2d0(propertyReplacements = "", schema = "'messages':a<r:'[0]'>,'mode':r<e>:'[1]'", typeReferences = {j3e0.class, VoiceSessionMode.class})
10: @Metadata(d1 = {"\u0000\u001a\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001f\b\u0017\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005¢\u0006\u0004\b\u0007\u0010\bR\u001c\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u00030\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00058\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u000b\u0010\f¨\u0006\r"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionInput;", "Lcom/snap/valdi/utils/b;", "", "Lj3e0;", "messages", "Lcom/openai/valdi/voice/Vo
11: public final class VoiceSessionInput extends b {
12:     private List<j3e0> _messages;
13:     private VoiceSessionMode _mode;
14: 
```

## `com/openai/valdi/voice/VoiceSessionListener.java`
### line 9
```java
5: import defpackage.gre0;
6: import defpackage.t5d0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000<\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0006\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u000f\u0010\u0007\u001a\u00020\u0004H&¢\u0006\u0004\b\u0007\u0010\bJ\u0017\u0010\u000b\u001a\u00020\u00042\u0006\u0010\n\u001a\u00020\tH&¢\u0006\u0004\b\u000b\u0010\fJ\u000f\u0010\r\u001a\u00020\u0004H&¢\u0006\u0004\b\r\u0010\bJ\u0017\u0010\u0010\u001a\u00020\u0
10: @t5d0(propertyReplacements = "", proxyClass = gre0.class, schema = "'onAudioLevel':f|m|(d),'onAssistantTranscriptComplete':f|m|(),'onAssistantTranscriptDelta':f|m|(s),'onEnded':f|m|(),'onError':f|m|(r:'[0]'),'onStatusChange':f|m|(r<e>:'[1]'),'onUserTranscript':f|m|(s),'onUserTranscriptDelta':f|m|(s)", typeReferences = {VoiceFailure.class, VoiceSessionStatus.class})
11: public interface VoiceSessionListener extends ValdiMarshallable {
12:     void onAssistantTranscriptComplete();
13: 
```

## `com/openai/valdi/voice/VoiceSessionMode.java`
### line 8
```java
4: import defpackage.r4d0;
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Dictation':0,'Advanced':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionMode;", "", "Dictation", "Advanced", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceSessionMode {
10:     public static final VoiceSessionMode Advanced;
11:     public static final VoiceSessionMode Dictation;
12:     public static final VoiceSessionMode[] a;
```

## `com/openai/valdi/voice/VoiceSessionStatus.java`
### line 8
```java
4: import defpackage.r4d0;
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Connecting':0,'Listening':1,'Thinking':2,'Speaking':3", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0005\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005¨\u0006\u0006"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionStatus;", "", "Connecting", "Listening", "Thinking", "Speaking", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceSessionStatus {
10:     public static final VoiceSessionStatus Connecting;
11:     public static final VoiceSessionStatus Listening;
12:     public static final VoiceSessionStatus Speaking;
```

## `com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java`
### line 55
```java
51: import java.util.Iterator;
52: import java.util.List;
53: import kotlin.Metadata;
54: 
55: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/voice/recording/VoiceAudioRecordingUploadWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerParameters;", "params", "<init>", "(Landroid/content/Context;Landroidx/work/WorkerParameters;)V", "qg3", "d480", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
56: public final class VoiceAudioRecordingUploadWorker extends CoroutineWorker {
57:     public static final long f;
58:     public static final int g = 0;
59:     public xyd0 a;
```

## `defpackage/bqk.java`
### line 96
```java
92:                 this.f = Collections.singletonList("trusted-contact/nominee?token=test-token&name=tester&account_id=testing@gmail.com&deadline=2026-05-20");
93:                 break;
94:             case 16:
95:                 super(mwjVar3);
96:                 this.e = Collections.singletonList("settings/voice/default-assistant");
97:                 this.f = new heh0((Object) y440.a(odl.class), (Object) new nii((byte) 20), (byte) 19);
98:                 break;
99:             default:
100:                 super(mwjVar3);
```

## `defpackage/f17.java`
### line 130
```java
126:             sj40 sj40Var = tj40.Companion;
127:             l640 l640Var = d9w.e;
128:             d9w d9wVarL = p0d0.L("audio/mp4");
129:             sj40Var.getClass();
130:             return m("/api/voice/transcribe", new pj40(d9wVarL, file, b));
131:         }
132:         String string = UUID.randomUUID().toString();
133:         l37 l37Var = new l37(string.getBytes(ci9.a));
134:         l37Var.c = string;
```

## `defpackage/sm6.java`
### line 28
```java
24:                 return "AppBackgrounded";
25:             case 2:
26:                 return "exception_while_adding_extras";
27:             case 3:
28:                 return "QuickTileServiceBound";
29:             case 4:
30:                 return "RestartedEvent";
31:             case 5:
32:                 return "Unknown";
```

## `defpackage/tqe0.java`
### line 28
```java
24:         this.T0 = (zwkVar == null || (ldlVarB0 = zwkVar.b0()) == null || (str = ldlVarB0.a) == null) ? null : str;
25:         lap lapVarE = p0d0.E(new yn(fue0Var.q, ud40Var.j, new acv(this, objArr3 == true ? 1 : 0, (byte) 17), (byte) 2));
26:         this.U0 = lapVarE;
27:         C(qcp.d(lapVarE, new jxd0((byte) 1, objArr2 == true ? 1 : 0, fue0Var)), new pp0((Object) this, (psg) (objArr == true ? 1 : 0), (byte) 26));
28:         bvj.u(lapVarE, this.X, new xr3(2, this, tqe0.class, "refreshOptions", "refreshOptions(Lcom/openai/voice/api/VoiceOptionsKey;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", 0, (byte) 14));
29:     }
30: 
31:     @Override
32:     public final void A(i4t i4tVar) {
```

## `defpackage/tw9.java`
### line 23
```java
19:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_EXISTING_CONVERSATION.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_VOICE_MODE.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_LOGIN_SCREEN.ordinal()] = 5;
```

## `defpackage/uw9.java`
### line 30
```java
26:             case 3:
27:                 str = "CHATGPT_COLD_START_DESTINATION_EXISTING_CONVERSATION";
28:                 break;
29:             case 4:
30:                 str = "CHATGPT_COLD_START_DESTINATION_VOICE_MODE";
31:                 break;
32:             case 5:
33:                 str = "CHATGPT_COLD_START_DESTINATION_LOGIN_SCREEN";
34:                 break;
```

## `defpackage/vue0.java`
### line 218
```java
214:             }
215:         });
216:         final byte b4 = 3;
217:         final byte b5 = 4;
218:         this.Z0 = new fa50(this.X, new xr3(2, fue0Var, fue0.class, "setVoiceIntelligenceSelection", "setVoiceIntelligenceSelection(Lcom/openai/user/model/VoiceIntelligenceSelection;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", 0, (byte) 15), new Function1(this) {
219:             public final vue0 b;
220: 
221:             {
222:                 this.b = this;
```

## `defpackage/w6y.java`
### line 9
```java
5: import com.snap.valdi.utils.ValdiMarshallable;
6: import com.snap.valdi.utils.ValdiMarshaller;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u0017\u0010\n\u001a\u00020\t2\u0006\u0010\b\u001a\u00020\u0007H\u0016¢\u0006\u0004\b\n\u0010\u000b¨\u0006\f"}, d2 = {"Lw6y;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "Lcom/openai/valdi/voice/VoiceServiceConfiguration;", "configuration", "Lcom/openai/valdi/voice/VoiceService;", "createVoiceService", "(Lcom/openai/valdi/voice/VoiceServiceConfiguration;)Lcom/openai/v
10: @t5d0(propertyReplacements = "", proxyClass = y6y.class, schema = "'createVoiceService':f|m|(r:'[0]'): r:'[1]'", typeReferences = {VoiceServiceConfiguration.class, VoiceService.class})
11: public interface w6y extends ValdiMarshallable {
12:     VoiceService createVoiceService(VoiceServiceConfiguration configuration);
13: 
```

## `defpackage/xc4.java`
### line 11
```java
7: import android.service.voice.VoiceInteractionSession;
8: import android.widget.Toast;
9: import com.openai.chatgpt.R;
10: import com.openai.feature.assistant.impl.AssistantVoiceInteractionSessionService;
11: import com.openai.voice.assistant.AssistantActivity;
12: import io.sentry.w4;
13: 
14: public final class xc4 extends VoiceInteractionSession {
15:     public final gev a;
```

### line 83
```java
79:             vxd0 vxd0Var = this.c;
80:             vxd0 vxd0Var2 = vxd0Var != null ? vxd0Var : null;
81:             Context context = getContext();
82:             vxd0Var2.getClass();
83:             startAssistantActivity(new Intent(context, (Class<?>) AssistantActivity.class).putExtra("isAssistant", true));
84:         } catch (Exception e) {
85:             Toast.makeText(getContext(), R.string._10d_res_0x7f140117, 0).show();
86:             w4.c(e);
87:         }
```

## `defpackage/yli.java`
### line 41
```java
37:         m = yliVar.c("android_conversation_login_cta_show_interstitial", 97, false);
38:         n = yliVar.e("model_picker_label", wli.Intelligence, 40, wli.d);
39:         o = yliVar.c("is_chat_intelligence_picker_slider_enabled", 40, false);
40:         p = yliVar.e("android_voice_entry_temporary_chat_location", xli.Header, 7, xli.g);
41:         q = yliVar.e("android_voice_entry_existing_chat_action", uli.Default, 7, uli.f);
42:         r = yliVar.e("android_voice_entry_header_icon", vli.Phone, 7, vli.d);
43:         s = yliVar.f("1970395505");
44:         t = yliVar.f("1708410805");
45:         u = yliVar.c("show_upsell_in_memory_settings", 119, false);
```

_files_with_hits=24; excerpts=25_
