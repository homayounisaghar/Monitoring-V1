plugins {
    id("com.android.application")
}

android {
    namespace = "com.onshape.mousebridge.poc"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.onshape.mousebridge.poc.test"
        minSdk = 34
        targetSdk = 35
        versionCode = 2
        versionName = "0.3.2-test"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
