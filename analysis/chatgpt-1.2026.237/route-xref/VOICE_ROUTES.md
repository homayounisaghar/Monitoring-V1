# VOICE_ROUTES

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
1: package com.openai.valdi.oai.platform;
2: 
3: import com.openai.valdi.filepicker.FilePickerService;
4: import com.openai.valdi.integrity.DeviceIntegrityService;
5: import com.openai.valdi.location.LocationService;
6: import com.openai.valdi.voice.VoiceService;
7: import com.snap.valdi.utils.b;
8: import defpackage.o2d0;
9: import kotlin.Metadata;
10: 
11: @o2d0(propertyReplacements = "", schema = "'experimentService':r?:'[0]','apiService':r?:'[1]','loggingService':r?:'[2]','accountScope':r?:'[3]','analyticsService':r?:'[4]','authenticationService':r?:'[5]','accountFeatureService':r?:'[6]','accountSettingsService':r?:'[7]','accountCustomizationsService':r?:'[8]','petCatalogDataSource':r?:'[9]','voiceService':r?:'[10]','filePickerService':r?:'[11]','locationService':r?:'[12]','deviceIntegrityService':r?:'[13]'", typeReferences = {OAIExperimentService.class, OAIAPIService.class, OAILoggingService.class, OAIAccountScope.class, OAIAnalyticsService.class, OAIAuthenticationService.class, OAIAccountFeatureService.class, OAIAccountSettingsService.class, OAIAccountCustomizationsService.class, OAIPetCatalogDataSource.class, VoiceService.class, FilePickerService.class, LocationService.class, DeviceIntegrityService.class})
12: @Metadata(d1 = {"\u0000^\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b \b\u0007\u0018\u00002\u00020\u0001B±\u0001\b\u0017\u0012\n\b\u0002\u0010\u0003\u001a\u0004\u0018\u00010\u0002\u0012\n\b\u0002\u0010\u0005\u001a\u0004\u0018\u00010\u0004\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0006\u0012\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\b\u0012\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\n\u0012\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\f\u0012\n\b\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u000e\u0012\n\b\u0002\u0010\u0011\u001a\u0004\u0018\u00010\u0010\u0012\n\b\u0002\u0010\u0013\u001a\u000
13: public final class OAIPlatformServices extends b {
14:     private OAIAccountCustomizationsService _accountCustomizationsService;
15:     private OAIAccountFeatureService _accountFeatureService;
16:     private OAIAccountScope _accountScope;
17:     private OAIAccountSettingsService _accountSettingsService;
18:     private OAIAnalyticsService _analyticsService;
19:     private OAIAPIService _apiService;
20:     private OAIAuthenticationService _authenticationService;
21:     private DeviceIntegrityService _deviceIntegrityService;
22:     private OAIExperimentService _experimentService;
23:     private FilePickerService _filePickerService;
24:     private LocationService _locationService;
```

## `com/openai/valdi/voice/VoiceCapabilities.java`
### line 8
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.b;
4: import defpackage.o2d0;
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'advancedVoice':b,'dictation':b", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0004\u001a\u00020\u0002¢\u0006\u0004\b\u0005\u0010\u0006R\u0016\u0010\u0007\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\b¨\u0006\n"}, d2 = {"Lcom/openai/valdi/voice/VoiceCapabilities;", "Lcom/snap/valdi/utils/b;", "", "advancedVoice", "dictation", "<init>", "(ZZ)V", "_advancedVoice", "Z", "_dictation", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceCapabilities extends b {
10:     private boolean _advancedVoice;
11:     private boolean _dictation;
12: 
13:     public VoiceCapabilities(boolean z, boolean z2) {
14:         this._advancedVoice = z;
15:         this._dictation = z2;
16:     }
17: }
```

## `com/openai/valdi/voice/VoiceFailure.java`
### line 8
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.b;
4: import defpackage.o2d0;
5: import kotlin.Metadata;
6: 
7: @o2d0(propertyReplacements = "", schema = "'message':s", typeReferences = {})
8: @Metadata(d1 = {"\u0000\u0010\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001B\u0011\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002¢\u0006\u0004\b\u0004\u0010\u0005R\u0016\u0010\u0006\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u0006\u0010\u0007¨\u0006\b"}, d2 = {"Lcom/openai/valdi/voice/VoiceFailure;", "Lcom/snap/valdi/utils/b;", "", "message", "<init>", "(Ljava/lang/String;)V", "_message", "Ljava/lang/String;", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceFailure extends b {
10:     private String _message;
11: 
12:     public VoiceFailure(String str) {
13:         this._message = str;
14:     }
15: }
```

## `com/openai/valdi/voice/VoiceService.java`
### line 9
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.ValdiMarshallable;
4: import com.snap.valdi.utils.ValdiMarshaller;
5: import defpackage.t5d0;
6: import defpackage.uqe0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\bg\u0018\u00002\u00020\u0001J\b\u0010\u0002\u001a\u00020\u0003H&J\u0010\u0010\u0004\u001a\u00020\u00052\u0006\u0010\u0006\u001a\u00020\u0007H\u0016J\u0018\u0010\b\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000b2\u0006\u0010\f\u001a\u00020\rH&¨\u0006\u000e"}, d2 = {"Lcom/openai/valdi/voice/VoiceService;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "getCapabilities", "Lcom/openai/valdi/voice/VoiceCapabilities;", "pushToMarshaller", "", "marshaller", "Lcom/snap/valdi/utils/ValdiMarshaller;", "start", "Lcom/openai/valdi/voice/VoiceSession;", "input", "Lcom/openai/valdi/voice/VoiceSessionInput;", "listener", "Lcom/openai/valdi/voice/VoiceSessionListener;", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
10: @t5d0(propertyReplacements = "", proxyClass = uqe0.class, schema = "'getCapabilities':f|m|(): r:'[0]','start':f|m|(r:'[1]', r:'[2]'): r:'[3]'", typeReferences = {VoiceCapabilities.class, VoiceSessionInput.class, VoiceSessionListener.class, VoiceSession.class})
11: public interface VoiceService extends ValdiMarshallable {
12:     VoiceCapabilities getCapabilities();
13: 
14:     @Override
15:     int pushToMarshaller(ValdiMarshaller marshaller);
16: 
17:     VoiceSession start(VoiceSessionInput input, VoiceSessionListener listener);
18: }
```

## `com/openai/valdi/voice/VoiceServiceConfiguration.java`
### line 10
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.b;
4: import defpackage.lpe0;
5: import defpackage.o2d0;
6: import java.util.List;
7: import kotlin.Metadata;
8: 
9: @o2d0(propertyReplacements = "", schema = "'baseUrl':s,'requestHeaders':a<r:'[0]'>", typeReferences = {lpe0.class})
10: @Metadata(d1 = {"\u0000\u001a\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001f\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004¢\u0006\u0004\b\u0007\u0010\bR\u0016\u0010\t\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u001c\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00050\u00048\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u000b\u0010\f¨\u0006\r"}, d2 = {"Lcom/openai/valdi/voice/VoiceServiceConfiguration;", "Lcom/snap/valdi/utils/b;", "", "baseUrl", "", "Llpe0;", "requestHeaders", "<init>", "(Ljava/lang/String;Ljava/util/List;)V", "_baseUrl", "Ljava/lang/String;", "_requestHeaders", "Ljava/util/List;", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
11: public final class VoiceServiceConfiguration extends b {
12:     private String _baseUrl;
13:     private List<lpe0> _requestHeaders;
14: 
15:     public VoiceServiceConfiguration(String str, List<lpe0> list) {
16:         this._baseUrl = str;
17:         this._requestHeaders = list;
18:     }
19: 
20:     public final String get_baseUrl() {
21:         return this._baseUrl;
22:     }
```

## `com/openai/valdi/voice/VoiceServiceNativeModuleFactoryImpl.java`
### line 8
```java
1: package com.openai.valdi.voice;
2: 
3: import defpackage.my0;
4: import defpackage.w6y;
5: import defpackage.x6y;
6: import kotlin.Metadata;
7: 
8: @Metadata(d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\b\u0007\u0018\u00002\u00020\u0001B\u0007¢\u0006\u0004\b\u0002\u0010\u0003J\u000f\u0010\u0005\u001a\u00020\u0004H\u0016¢\u0006\u0004\b\u0005\u0010\u0006¨\u0006\u0007"}, d2 = {"Lcom/openai/valdi/voice/VoiceServiceNativeModuleFactoryImpl;", "Lx6y;", "<init>", "()V", "Lw6y;", "onLoadModule", "()Lw6y;", "modules_oai_voice_service-oai_voice_service_android_impl_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceServiceNativeModuleFactoryImpl extends x6y {
10:     @Override
11:     public w6y onLoadModule() {
12:         return new my0();
13:     }
14: }
```

## `com/openai/valdi/voice/VoiceSession.java`
### line 9
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.ValdiMarshallable;
4: import com.snap.valdi.utils.ValdiMarshaller;
5: import defpackage.ose0;
6: import defpackage.t5d0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u000f\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0003\u0010\u0004J\u0017\u0010\u0007\u001a\u00020\u00022\u0006\u0010\u0006\u001a\u00020\u0005H&¢\u0006\u0004\b\u0007\u0010\bJ\u000f\u0010\t\u001a\u00020\u0002H&¢\u0006\u0004\b\t\u0010\u0004J\u0017\u0010\r\u001a\u00020\f2\u0006\u0010\u000b\u001a\u00020\nH\u0016¢\u0006\u0004\b\r\u0010\u000e¨\u0006\u000f"}, d2 = {"Lcom/openai/valdi/voice/VoiceSession;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "Lwec0;", "finish", "()V", "", "muted", "setMuted", "(Z)V", "stop", "Lcom/snap/valdi/utils/ValdiMarshaller;", "marshaller", "", "pushToMarshaller", "(Lcom/snap/valdi/utils/ValdiMarshaller;)I", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
10: @t5d0(propertyReplacements = "", proxyClass = ose0.class, schema = "'finish':f|m|(),'setMuted':f|m|(b),'stop':f|m|()", typeReferences = {})
11: public interface VoiceSession extends ValdiMarshallable {
12:     void finish();
13: 
14:     @Override
15:     int pushToMarshaller(ValdiMarshaller marshaller);
16: 
17:     void setMuted(boolean muted);
18: 
19:     void stop();
20: }
```

## `com/openai/valdi/voice/VoiceSessionInput.java`
### line 10
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.b;
4: import defpackage.j3e0;
5: import defpackage.o2d0;
6: import java.util.List;
7: import kotlin.Metadata;
8: 
9: @o2d0(propertyReplacements = "", schema = "'messages':a<r:'[0]'>,'mode':r<e>:'[1]'", typeReferences = {j3e0.class, VoiceSessionMode.class})
10: @Metadata(d1 = {"\u0000\u001a\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u001f\b\u0017\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00030\u0002\u0012\u0006\u0010\u0006\u001a\u00020\u0005¢\u0006\u0004\b\u0007\u0010\bR\u001c\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u00030\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\t\u0010\nR\u0016\u0010\u000b\u001a\u00020\u00058\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\u000b\u0010\f¨\u0006\r"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionInput;", "Lcom/snap/valdi/utils/b;", "", "Lj3e0;", "messages", "Lcom/openai/valdi/voice/VoiceSessionMode;", "mode", "<init>", "(Ljava/util/List;Lcom/openai/valdi/voice/VoiceSessionMode;)V", "_messages", "Ljava/util/List;", "_mode", "Lcom/openai/valdi/voice/VoiceSessionMode;", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
11: public final class VoiceSessionInput extends b {
12:     private List<j3e0> _messages;
13:     private VoiceSessionMode _mode;
14: 
15:     public VoiceSessionInput(List<j3e0> list, VoiceSessionMode voiceSessionMode) {
16:         this._messages = list;
17:         this._mode = voiceSessionMode;
18:     }
19: 
20:     public final VoiceSessionMode get_mode() {
21:         return this._mode;
22:     }
```

## `com/openai/valdi/voice/VoiceSessionListener.java`
### line 9
```java
1: package com.openai.valdi.voice;
2: 
3: import com.snap.valdi.utils.ValdiMarshallable;
4: import com.snap.valdi.utils.ValdiMarshaller;
5: import defpackage.gre0;
6: import defpackage.t5d0;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000<\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0006\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u000f\u0010\u0007\u001a\u00020\u0004H&¢\u0006\u0004\b\u0007\u0010\bJ\u0017\u0010\u000b\u001a\u00020\u00042\u0006\u0010\n\u001a\u00020\tH&¢\u0006\u0004\b\u000b\u0010\fJ\u000f\u0010\r\u001a\u00020\u0004H&¢\u0006\u0004\b\r\u0010\bJ\u0017\u0010\u0010\u001a\u00020\u00042\u0006\u0010\u000f\u001a\u00020\u000eH&¢\u0006\u0004\b\u0010\u0010\u0011J\u0017\u0010\u0014\u001a\u00020\u00042\u0006\u0010\u0013\u001a\u00020\u0012H&¢\u0006\u0004\b\u0014\u0010\u0015J\u0017\u0010\u0017\u001a\u00020\u00042\u0006\u0010\u0016\u001a\u00020\tH&¢\u0006\u0004\b\u0017\u0010\fJ\u0017\u0
10: @t5d0(propertyReplacements = "", proxyClass = gre0.class, schema = "'onAudioLevel':f|m|(d),'onAssistantTranscriptComplete':f|m|(),'onAssistantTranscriptDelta':f|m|(s),'onEnded':f|m|(),'onError':f|m|(r:'[0]'),'onStatusChange':f|m|(r<e>:'[1]'),'onUserTranscript':f|m|(s),'onUserTranscriptDelta':f|m|(s)", typeReferences = {VoiceFailure.class, VoiceSessionStatus.class})
11: public interface VoiceSessionListener extends ValdiMarshallable {
12:     void onAssistantTranscriptComplete();
13: 
14:     void onAssistantTranscriptDelta(String delta);
15: 
16:     void onAudioLevel(double level);
17: 
18:     void onEnded();
19: 
20:     void onError(VoiceFailure error);
21: 
```

## `com/openai/valdi/voice/VoiceSessionMode.java`
### line 8
```java
1: package com.openai.valdi.voice;
2: 
3: import defpackage.q4d0;
4: import defpackage.r4d0;
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Dictation':0,'Advanced':1", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0003\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003¨\u0006\u0004"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionMode;", "", "Dictation", "Advanced", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceSessionMode {
10:     public static final VoiceSessionMode Advanced;
11:     public static final VoiceSessionMode Dictation;
12:     public static final VoiceSessionMode[] a;
13: 
14:     static {
15:         VoiceSessionMode voiceSessionMode = new VoiceSessionMode("Dictation", 0);
16:         Dictation = voiceSessionMode;
17:         VoiceSessionMode voiceSessionMode2 = new VoiceSessionMode("Advanced", 1);
18:         Advanced = voiceSessionMode2;
19:         a = new VoiceSessionMode[]{voiceSessionMode, voiceSessionMode2};
20:     }
```

## `com/openai/valdi/voice/VoiceSessionStatus.java`
### line 8
```java
1: package com.openai.valdi.voice;
2: 
3: import defpackage.q4d0;
4: import defpackage.r4d0;
5: import kotlin.Metadata;
6: 
7: @q4d0(propertyReplacements = "", schema = "'Connecting':0,'Listening':1,'Thinking':2,'Speaking':3", type = r4d0.a)
8: @Metadata(d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0005\b\u0087\u0001\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001j\u0002\b\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005¨\u0006\u0006"}, d2 = {"Lcom/openai/valdi/voice/VoiceSessionStatus;", "", "Connecting", "Listening", "Thinking", "Speaking", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
9: public final class VoiceSessionStatus {
10:     public static final VoiceSessionStatus Connecting;
11:     public static final VoiceSessionStatus Listening;
12:     public static final VoiceSessionStatus Speaking;
13:     public static final VoiceSessionStatus Thinking;
14:     public static final VoiceSessionStatus[] a;
15: 
16:     static {
17:         VoiceSessionStatus voiceSessionStatus = new VoiceSessionStatus("Connecting", 0);
18:         Connecting = voiceSessionStatus;
19:         VoiceSessionStatus voiceSessionStatus2 = new VoiceSessionStatus("Listening", 1);
20:         Listening = voiceSessionStatus2;
```

## `com/openai/voice/recording/VoiceAudioRecordingUploadWorker.java`
### line 55
```java
43: import defpackage.wqi;
44: import defpackage.xyd0;
45: import defpackage.y8e0;
46: import defpackage.yyd0;
47: import defpackage.yyu;
48: import defpackage.zyu;
49: import java.util.Collections;
50: import java.util.HashMap;
51: import java.util.Iterator;
52: import java.util.List;
53: import kotlin.Metadata;
54: 
55: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001:\u0002\b\tB\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007¨\u0006\n"}, d2 = {"Lcom/openai/voice/recording/VoiceAudioRecordingUploadWorker;", "Landroidx/work/CoroutineWorker;", "Landroid/content/Context;", "context", "Landroidx/work/WorkerParameters;", "params", "<init>", "(Landroid/content/Context;Landroidx/work/WorkerParameters;)V", "qg3", "d480", "impl"}, k = 1, mv = {2, 4, 0}, xi = 48)
56: public final class VoiceAudioRecordingUploadWorker extends CoroutineWorker {
57:     public static final long f;
58:     public static final int g = 0;
59:     public xyd0 a;
60:     public hzd0 b;
61:     public txd0 c;
62:     public w9e0 d;
63:     public final uee0 e;
64: 
65:     static {
66:         g6h g6hVar = irm.b;
67:         f = kfr.r0(10, qrm.SECONDS);
```

## `defpackage/bqk.java`
### line 96
```java
84:             case 14:
85:                 super(mwjVar);
86:                 this.e = bvj.T("share/{sharedId}", "share/{sharedId}/continue", "share/e/{sharedId}", "share/e/{sharedId}/continue");
87:                 this.f = bvj.T("share/6fc2aac8-1625-412e-b9aa-3d65545198da", "share/e/6fc2aac8-1625-412e-b9aa-3d65545198da");
88:                 break;
89:             case 15:
90:                 super(mwjVar);
91:                 this.e = Collections.singletonList("trusted-contact/nominee?token={token}&name={name}&account_id={contact}&deadline={deadline}");
92:                 this.f = Collections.singletonList("trusted-contact/nominee?token=test-token&name=tester&account_id=testing@gmail.com&deadline=2026-05-20");
93:                 break;
94:             case 16:
95:                 super(mwjVar3);
96:                 this.e = Collections.singletonList("settings/voice/default-assistant");
97:                 this.f = new heh0((Object) y440.a(odl.class), (Object) new nii((byte) 20), (byte) 19);
98:                 break;
99:             default:
100:                 super(mwjVar3);
101:                 this.e = Collections.singletonList("apps/{appSlug}/{id}");
102:                 lrf.Companion.getClass();
103:                 this.f = Collections.singletonList("apps/gmail/connector_2128aebfecb84f64a069897515042a44");
104:                 break;
105:         }
106:     }
107: 
108:     @Override
```

## `defpackage/j3e0.java`
### line 6
```java
1: package defpackage;
2: 
3: import com.snap.valdi.utils.b;
4: import kotlin.Metadata;
5: 
6: @o2d0(propertyReplacements = "", schema = "'content':s,'isAssistant':b", typeReferences = {})
7: @Metadata(d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0002\u0012\u0006\u0010\u0005\u001a\u00020\u0004¢\u0006\u0004\b\u0006\u0010\u0007R\u0016\u0010\b\u001a\u00020\u00028\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\b\u0010\tR\u0016\u0010\n\u001a\u00020\u00048\u0002@\u0002X\u0083\u000e¢\u0006\u0006\n\u0004\b\n\u0010\u000b¨\u0006\f"}, d2 = {"Lj3e0;", "Lcom/snap/valdi/utils/b;", "", "content", "", "isAssistant", "<init>", "(Ljava/lang/String;Z)V", "_content", "Ljava/lang/String;", "_isAssistant", "Z", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
8: public final class j3e0 extends b {
9:     private String _content;
10:     private boolean _isAssistant;
11: 
12:     public j3e0(String str, boolean z) {
13:         this._content = str;
14:         this._isAssistant = z;
15:     }
16: }
```

## `defpackage/lbe0.java`
### line 162
```java
150:             kbe0Var = new kbe0(this, psgVar);
151:         }
152:         Object objQ = kbe0Var.n;
153:         wqi wqiVar = wqi.a;
154:         int i2 = kbe0Var.p;
155:         if (i2 == 0) {
156:             ct40.j(objQ);
157:             mz80 mz80Var = this.c;
158:             if (z) {
159:                 do {
160:                     value = mz80Var.getValue();
161:                 } while (!mz80Var.l(value, ibe0.b((ibe0) value, null, null, null, false, true, false, 43)));
162:                 if (!wnm.k(this.p.a("isAssistant"), Boolean.TRUE) && this.l.d.getValue() == ife0.Advanced && !this.h.w() && !((fxd0) this.g.f()).s) {
163:                     qo qoVar = this.j.c;
164:                     kbe0Var.p = 1;
165:                     objQ = vq30.q(qoVar, kbe0Var);
166:                     if (objQ == wqiVar) {
167:                         return wqiVar;
168:                     }
169:                 }
170:             } else {
171:                 do {
172:                     value2 = mz80Var.getValue();
173:                 } while (!mz80Var.l(value2, ibe0.b((ibe0) value2, null, null, null, false, false, false, 107)));
174:             }
```

## `defpackage/tqe0.java`
### line 28
```java
16:         super(yrd0Var, new pqe0((eu20) null, (bxd0) (0 == true ? 1 : 0), 7));
17:         Object[] objArr = 0;
18:         Object[] objArr2 = 0;
19:         Object[] objArr3 = 0;
20:         this.Q0 = application;
21:         this.R0 = fue0Var;
22:         this.S0 = ud40Var;
23:         zwk zwkVar = m350Var instanceof zwk ? (zwk) m350Var : null;
24:         this.T0 = (zwkVar == null || (ldlVarB0 = zwkVar.b0()) == null || (str = ldlVarB0.a) == null) ? null : str;
25:         lap lapVarE = p0d0.E(new yn(fue0Var.q, ud40Var.j, new acv(this, objArr3 == true ? 1 : 0, (byte) 17), (byte) 2));
26:         this.U0 = lapVarE;
27:         C(qcp.d(lapVarE, new jxd0((byte) 1, objArr2 == true ? 1 : 0, fue0Var)), new pp0((Object) this, (psg) (objArr == true ? 1 : 0), (byte) 26));
28:         bvj.u(lapVarE, this.X, new xr3(2, this, tqe0.class, "refreshOptions", "refreshOptions(Lcom/openai/voice/api/VoiceOptionsKey;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", 0, (byte) 14));
29:     }
30: 
31:     @Override
32:     public final void A(i4t i4tVar) {
33:         Object value;
34:         nqe0 nqe0Var = (nqe0) i4tVar;
35:         byte b = 5;
36:         psg psgVar = null;
37:         if (!(nqe0Var instanceof mqe0)) {
38:             if (nqe0Var.equals(jqe0.a)) {
39:                 this.T0 = null;
40:                 return;
```

## `defpackage/tw9.java`
### line 23
```java
11:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_UNSPECIFIED.ordinal()] = 1;
12:         } catch (NoSuchFieldError unused) {
13:         }
14:         try {
15:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_NEW_CONVERSATION.ordinal()] = 2;
16:         } catch (NoSuchFieldError unused2) {
17:         }
18:         try {
19:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_EXISTING_CONVERSATION.ordinal()] = 3;
20:         } catch (NoSuchFieldError unused3) {
21:         }
22:         try {
23:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_VOICE_MODE.ordinal()] = 4;
24:         } catch (NoSuchFieldError unused4) {
25:         }
26:         try {
27:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_LOGIN_SCREEN.ordinal()] = 5;
28:         } catch (NoSuchFieldError unused5) {
29:         }
30:         try {
31:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_QUICK_TILE_SERVICE.ordinal()] = 6;
32:         } catch (NoSuchFieldError unused6) {
33:         }
34:         try {
35:             iArr[ChatgptColdStartDestination.CHATGPT_COLD_START_DESTINATION_BACKGROUND_PROCESS.ordinal()] = 7;
```

## `defpackage/uw9.java`
### line 30
```java
18:         String str;
19:         switch (tw9.a[((ChatgptColdStartDestination) obj).ordinal()]) {
20:             case 1:
21:                 str = "CHATGPT_COLD_START_DESTINATION_UNSPECIFIED";
22:                 break;
23:             case 2:
24:                 str = "CHATGPT_COLD_START_DESTINATION_NEW_CONVERSATION";
25:                 break;
26:             case 3:
27:                 str = "CHATGPT_COLD_START_DESTINATION_EXISTING_CONVERSATION";
28:                 break;
29:             case 4:
30:                 str = "CHATGPT_COLD_START_DESTINATION_VOICE_MODE";
31:                 break;
32:             case 5:
33:                 str = "CHATGPT_COLD_START_DESTINATION_LOGIN_SCREEN";
34:                 break;
35:             case 6:
36:                 str = "CHATGPT_COLD_START_DESTINATION_QUICK_TILE_SERVICE";
37:                 break;
38:             case 7:
39:                 str = "CHATGPT_COLD_START_DESTINATION_BACKGROUND_PROCESS";
40:                 break;
41:             case 8:
42:                 str = "CHATGPT_COLD_START_DESTINATION_IMAGES_HOME";
```

## `defpackage/w6y.java`
### line 9
```java
1: package defpackage;
2: 
3: import com.openai.valdi.voice.VoiceService;
4: import com.openai.valdi.voice.VoiceServiceConfiguration;
5: import com.snap.valdi.utils.ValdiMarshallable;
6: import com.snap.valdi.utils.ValdiMarshaller;
7: import kotlin.Metadata;
8: 
9: @Metadata(d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\bg\u0018\u00002\u00020\u0001J\u0017\u0010\u0005\u001a\u00020\u00042\u0006\u0010\u0003\u001a\u00020\u0002H&¢\u0006\u0004\b\u0005\u0010\u0006J\u0017\u0010\n\u001a\u00020\t2\u0006\u0010\b\u001a\u00020\u0007H\u0016¢\u0006\u0004\b\n\u0010\u000b¨\u0006\f"}, d2 = {"Lw6y;", "Lcom/snap/valdi/utils/ValdiMarshallable;", "Lcom/openai/valdi/voice/VoiceServiceConfiguration;", "configuration", "Lcom/openai/valdi/voice/VoiceService;", "createVoiceService", "(Lcom/openai/valdi/voice/VoiceServiceConfiguration;)Lcom/openai/valdi/voice/VoiceService;", "Lcom/snap/valdi/utils/ValdiMarshaller;", "marshaller", "", "pushToMarshaller", "(Lcom/snap/valdi/utils/ValdiMarshaller;)I", "modules_oai_voice_service-oai_voice_service_api_kt_kt"}, k = 1, mv = {1, 8, 0}, xi = 48)
10: @t5d0(propertyReplacements = "", proxyClass = y6y.class, schema = "'createVoiceService':f|m|(r:'[0]'): r:'[1]'", typeReferences = {VoiceServiceConfiguration.class, VoiceService.class})
11: public interface w6y extends ValdiMarshallable {
12:     VoiceService createVoiceService(VoiceServiceConfiguration configuration);
13: 
14:     @Override
15:     int pushToMarshaller(ValdiMarshaller marshaller);
16: }
```

## `defpackage/xc4.java`
### line 83
```java
71:             return;
72:         }
73:         gd4 gd4Var = this.b;
74:         if (gd4Var == null) {
75:             gd4Var = null;
76:         }
77:         gd4Var.b = new q8(0, this, xc4.class, "finish", "finish()V", 0, (byte) 7);
78:         try {
79:             vxd0 vxd0Var = this.c;
80:             vxd0 vxd0Var2 = vxd0Var != null ? vxd0Var : null;
81:             Context context = getContext();
82:             vxd0Var2.getClass();
83:             startAssistantActivity(new Intent(context, (Class<?>) AssistantActivity.class).putExtra("isAssistant", true));
84:         } catch (Exception e) {
85:             Toast.makeText(getContext(), R.string._10d_res_0x7f140117, 0).show();
86:             w4.c(e);
87:         }
88:     }
89: }
```

## `defpackage/yli.java`
### line 41
```java
29:         yli yliVar = new yli();
30:         f = yliVar;
31:         g = yliVar.f("2900425578");
32:         h = yliVar.c("sketch_enabled", 32, false);
33:         i = yliVar.c("android_rate_limit_upsell_requested_plan_enabled", 17, false);
34:         j = yliVar.c("file_upload_rate_limit_banner", 39, true);
35:         k = yliVar.c("back_handler_navigates_to_new_conversation", 76, false);
36:         l = yliVar.c("new_conversation_back_stack_enabled", 76, false);
37:         m = yliVar.c("android_conversation_login_cta_show_interstitial", 97, false);
38:         n = yliVar.e("model_picker_label", wli.Intelligence, 40, wli.d);
39:         o = yliVar.c("is_chat_intelligence_picker_slider_enabled", 40, false);
40:         p = yliVar.e("android_voice_entry_temporary_chat_location", xli.Header, 7, xli.g);
41:         q = yliVar.e("android_voice_entry_existing_chat_action", uli.Default, 7, uli.f);
42:         r = yliVar.e("android_voice_entry_header_icon", vli.Phone, 7, vli.d);
43:         s = yliVar.f("1970395505");
44:         t = yliVar.f("1708410805");
45:         u = yliVar.c("show_upsell_in_memory_settings", 119, false);
46:         v = yliVar.c("show_persistent_memory_almost_full_upgrade_pill", 119, false);
47:         w = yliVar.c("show_persistent_memory_full_upgrade_pill", 119, true);
48:         x = yliVar.f("1431663914");
49:         y = yliVar.c("skip_init_conversation_persistence", 136, false);
50:         z = yliVar.f("780162561");
51:         A = yliVar.f("2806707835");
52:         B = yliVar.f("2995333001");
53:     }
```

_files=23; excerpts=23_