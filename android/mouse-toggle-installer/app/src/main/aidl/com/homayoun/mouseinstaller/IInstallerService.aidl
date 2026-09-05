package com.homayoun.mouseinstaller;

interface IInstallerService {
    String installApk(in byte[] apkBytes);
    String probe();
}
