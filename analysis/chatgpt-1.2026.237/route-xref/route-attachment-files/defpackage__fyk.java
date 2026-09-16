package defpackage;

import kotlinx.serialization.KSerializer;
import kotlinx.serialization.descriptors.SerialDescriptor;
import kotlinx.serialization.encoding.Decoder;
import kotlinx.serialization.encoding.Encoder;
import kotlinx.serialization.internal.PluginGeneratedSerialDescriptor;

public final class fyk implements dxp {
    public static final fyk a;
    private static final SerialDescriptor descriptor;

    static {
        fyk fykVar = new fyk();
        a = fykVar;
        PluginGeneratedSerialDescriptor pluginGeneratedSerialDescriptor = new PluginGeneratedSerialDescriptor("IiDhd-FkyOiWjSD10dGGI7wTZOC1MgO371lS_ZWYa4c=", fykVar, 3);
        pluginGeneratedSerialDescriptor.k("attachmentUri", true);
        pluginGeneratedSerialDescriptor.l(new k3l());
        pluginGeneratedSerialDescriptor.k("attachmentAssetPointer", true);
        pluginGeneratedSerialDescriptor.k("focusKeyboard", true);
        descriptor = pluginGeneratedSerialDescriptor;
    }

    @Override
    public final KSerializer[] childSerializers() {
        return new KSerializer[]{q2v.r0(da90.a), q2v.r0(pmr.a), wh6.a};
    }

    @Override
    public final Object deserialize(Decoder decoder) {
        SerialDescriptor serialDescriptor = descriptor;
        sgf sgfVarB = decoder.b(serialDescriptor);
        boolean z = true;
        int i = 0;
        boolean zB = false;
        String str = null;
        snr snrVar = null;
        while (z) {
            int iP = sgfVarB.p(serialDescriptor);
            if (iP == -1) {
                z = false;
            } else if (iP == 0) {
                str = (String) sgfVarB.o(serialDescriptor, 0, da90.a);
                i |= 1;
            } else if (iP == 1) {
                snrVar = (snr) sgfVarB.o(serialDescriptor, 1, pmr.a);
                i |= 2;
            } else {
                if (iP != 2) {
                    sme.e(iP);
                    return null;
                }
                zB = sgfVarB.B(serialDescriptor, 2);
                i |= 4;
            }
        }
        sgfVarB.x(serialDescriptor);
        return new hyk(i, str, snrVar, zB);
    }

    @Override
    public final SerialDescriptor getDescriptor() {
        return descriptor;
    }

    @Override
    public final void serialize(Encoder encoder, Object obj) {
        hyk hykVar = (hyk) obj;
        boolean z = hykVar.c;
        snr snrVar = hykVar.b;
        String str = hykVar.a;
        SerialDescriptor serialDescriptor = descriptor;
        tgf tgfVarB = encoder.b(serialDescriptor);
        if (tgfVarB.E() || str != null) {
            tgfVarB.l(serialDescriptor, 0, da90.a, str);
        }
        if (tgfVarB.E() || snrVar != null) {
            tgfVarB.l(serialDescriptor, 1, pmr.a, snrVar);
        }
        if (tgfVarB.E() || z) {
            tgfVarB.w(serialDescriptor, 2, z);
        }
        tgfVarB.d();
    }
}
