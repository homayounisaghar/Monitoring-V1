package com.homayoun.rotationtile;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class TileLongPressActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        RotationTileService.cancelPendingBatch(this);

        if (!RotationController.isEnabled(this)
                && !RotationController.hasRequiredPermissions(this)) {
            startActivity(new Intent(this, MainActivity.class)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP));
        } else {
            RotationController.toggleOverride(this);
            RotationTileService.requestTileRefresh(this);
        }

        finish();
        overridePendingTransition(0, 0);
    }
}
