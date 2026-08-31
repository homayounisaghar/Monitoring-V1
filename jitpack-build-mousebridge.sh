#!/usr/bin/env bash
set -euo pipefail

if [ -f "$HOME/.sdkman/bin/sdkman-init.sh" ]; then
  source "$HOME/.sdkman/bin/sdkman-init.sh"
fi

if command -v sdk >/dev/null 2>&1; then
  sdk install gradle 8.9 >/dev/null 2>&1 || true
  sdk use gradle 8.9
fi

if command -v sdkmanager >/dev/null 2>&1; then
  yes | sdkmanager --licenses >/dev/null 2>&1 || true
  sdkmanager "platforms;android-35" "build-tools;35.0.0"
fi

gradle --version
gradle -p mousebridge-build :app:assembleDebug --stacktrace

APK="mousebridge-build/app/build/outputs/apk/debug/app-debug.apk"
test -f "$APK"

GROUP_PATH="${GROUP//./\/}"
OUT="$HOME/.m2/repository/$GROUP_PATH/$ARTIFACT/$VERSION"
mkdir -p "$OUT"
cp "$APK" "$OUT/$ARTIFACT-$VERSION.apk"
cat > "$OUT/$ARTIFACT-$VERSION.pom" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>$GROUP</groupId>
  <artifactId>$ARTIFACT</artifactId>
  <version>$VERSION</version>
  <packaging>apk</packaging>
  <name>Onshape MouseBridge test APK</name>
</project>
EOF

ls -lh "$OUT"
