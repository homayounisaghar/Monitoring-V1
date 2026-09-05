package com.samsung.android.gtscell;

import android.os.Bundle;
import android.os.Parcel;
import android.os.Parcelable;
import android.os.RemoteException;

public final class RemoteCallback implements Parcelable {
    public interface OnResultListener {
        void onResult(Bundle result);
    }

    private final IRemoteCallback callback;
    private final OnResultListener listener;

    public RemoteCallback(OnResultListener listener) {
        if (listener == null) throw new NullPointerException("listener");
        this.listener = listener;
        this.callback = new IRemoteCallback.Stub() {
            @Override
            public void sendResult(Bundle bundle) {
                RemoteCallback.this.listener.onResult(bundle);
            }
        };
    }

    private RemoteCallback(Parcel parcel) {
        this.listener = null;
        this.callback = IRemoteCallback.Stub.asInterface(parcel.readStrongBinder());
    }

    public void sendResult(Bundle result) {
        if (listener != null) {
            listener.onResult(result);
            return;
        }
        try {
            if (callback != null) callback.sendResult(result);
        } catch (RemoteException ignored) {
        }
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeStrongBinder(callback == null ? null : callback.asBinder());
    }

    public static final Creator<RemoteCallback> CREATOR = new Creator<RemoteCallback>() {
        @Override
        public RemoteCallback createFromParcel(Parcel source) {
            return new RemoteCallback(source);
        }

        @Override
        public RemoteCallback[] newArray(int size) {
            return new RemoteCallback[size];
        }
    };
}
