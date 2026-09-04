# Rotation Tile

Android Quick Settings tile cycling through five states:

1. Off (restore previous rotation settings)
2. Portrait / 0°
3. Landscape / 90° clockwise
4. Reverse portrait / 180°
5. Reverse landscape / 270°

The forcing mechanism deliberately combines `Settings.System` rotation locking with a tiny transparent `TYPE_APPLICATION_OVERLAY` window whose `screenOrientation` is set to the requested absolute orientation. The app requires user-granted **Display over other apps** and **Modify system settings** permissions.

Package: `com.homayoun.rotationtile`
Version: `1.0.0` / versionCode `1`
