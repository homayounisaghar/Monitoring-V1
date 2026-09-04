# ROUTE_ATTACHMENTS

## `defpackage/fyk.java`
### line 17
```java
5: import kotlinx.serialization.encoding.Decoder;
6: import kotlinx.serialization.encoding.Encoder;
7: import kotlinx.serialization.internal.PluginGeneratedSerialDescriptor;
8: 
9: public final class fyk implements dxp {
10:     public static final fyk a;
11:     private static final SerialDescriptor descriptor;
12: 
13:     static {
14:         fyk fykVar = new fyk();
15:         a = fykVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("IiDhd-FkyOiWjSD10dGGI7wTZOC1MgO371lS_ZWYa4c=", fykVar, 3);
17:         pluginGeneratedSerialDescriptor.k("attachmentUri", true);
18:         pluginGeneratedSerialDescriptor.l(new k3l());
19:         pluginGeneratedSerialDescriptor.k("attachmentAssetPointer", true);
20:         pluginGeneratedSerialDescriptor.k("focusKeyboard", true);
21:         descriptor = pluginGeneratedSerialDescriptor;
22:     }
23: 
24:     @Override
25:     public final KSerializer[] childSerializers() {
26:         return new KSerializer[]{q2v.r0(da90.a), q2v.r0(pmr.a), wh6.a};
27:     }
28: 
29:     @Override
```

## `defpackage/qzk.java`
### line 25
```java
13:     static {
14:         qzk qzkVar = new qzk();
15:         a = qzkVar;
16:         PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("mqEWH1fxzh5QgGGJd5i5c8f9mwyLv-Uq7u6jIxQzbzE=", qzkVar, 9);
17:         pluginGeneratedSerialDescriptor.k("imageId", false);
18:         pluginGeneratedSerialDescriptor.l(new k3l());
19:         pluginGeneratedSerialDescriptor.k("fromImageHome", true);
20:         pluginGeneratedSerialDescriptor.k("localImageUri", true);
21:         pluginGeneratedSerialDescriptor.l(new k3l());
22:         pluginGeneratedSerialDescriptor.k("newConversationOnSend", true);
23:         pluginGeneratedSerialDescriptor.k("sideConversationId", true);
24:         pluginGeneratedSerialDescriptor.k("sideConversationRoomId", true);
25:         pluginGeneratedSerialDescriptor.k("focusKeyboard", true);
26:         pluginGeneratedSerialDescriptor.k("localImageMode", true);
27:         pluginGeneratedSerialDescriptor.k("fromDeepLink", true);
28:         descriptor = pluginGeneratedSerialDescriptor;
29:     }
30: 
31:     @Override
32:     public final KSerializer[] childSerializers() {
33:         uzt[] uztVarArr = szk.j;
34:         da90 da90Var = da90.a;
35:         wh6 wh6Var = wh6.a;
36:         return new KSerializer[]{da90Var, wh6Var, q2v.r0(da90Var), wh6Var, q2v.r0(xch.a), q2v.r0(vf7.a), wh6Var, uztVarArr[7].getValue(), wh6Var};
37:     }
```

_files=2; excerpts=2_