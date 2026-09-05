package com.samsung.android.gtscell;

import android.os.Binder;
import android.os.Bundle;
import android.os.IBinder;
import android.os.IInterface;
import android.os.Parcel;
import android.os.RemoteException;

public interface IRemoteCallback extends IInterface {
    void sendResult(Bundle bundle) throws RemoteException;

    abstract class Stub extends Binder implements IRemoteCallback {
        private static final String DESCRIPTOR = "com.samsung.android.gtscell.IRemoteCallback";
        private static final int TRANSACTION_SEND_RESULT = 1;

        public Stub() {
            attachInterface(this, DESCRIPTOR);
        }

        public static IRemoteCallback asInterface(IBinder binder) {
            if (binder == null) return null;
            IInterface local = binder.queryLocalInterface(DESCRIPTOR);
            if (local instanceof IRemoteCallback) return (IRemoteCallback) local;
            return new Proxy(binder);
        }

        @Override
        public IBinder asBinder() {
            return this;
        }

        @Override
        protected boolean onTransact(int code, Parcel data, Parcel reply, int flags)
                throws RemoteException {
            if (code == INTERFACE_TRANSACTION) {
                reply.writeString(DESCRIPTOR);
                return true;
            }
            if (code == TRANSACTION_SEND_RESULT) {
                data.enforceInterface(DESCRIPTOR);
                Bundle bundle = data.readInt() != 0
                        ? Bundle.CREATOR.createFromParcel(data)
                        : null;
                sendResult(bundle);
                reply.writeNoException();
                return true;
            }
            return super.onTransact(code, data, reply, flags);
        }

        private static final class Proxy implements IRemoteCallback {
            private final IBinder remote;

            Proxy(IBinder remote) {
                this.remote = remote;
            }

            @Override
            public IBinder asBinder() {
                return remote;
            }

            @Override
            public void sendResult(Bundle bundle) throws RemoteException {
                Parcel data = Parcel.obtain();
                Parcel reply = Parcel.obtain();
                try {
                    data.writeInterfaceToken(DESCRIPTOR);
                    if (bundle != null) {
                        data.writeInt(1);
                        bundle.writeToParcel(data, 0);
                    } else {
                        data.writeInt(0);
                    }
                    remote.transact(TRANSACTION_SEND_RESULT, data, reply, 0);
                    reply.readException();
                } finally {
                    reply.recycle();
                    data.recycle();
                }
            }
        }
    }
}
