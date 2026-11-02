# SPAKE2 Android build

Java/JNI source: https://github.com/MuntashirAkon/spake2-java/tree/7615ddd680b990e14513ebb66eac4cb0dbf82464 (tag 2.2.1).
C source: https://github.com/MuntashirAkon/spake2-c/tree/0d15933e5ba3e662cb01245a7ac0dc9fca3eac31.

Sources are unchanged. Local CMake and Gradle files rebuild the same implementation with NDK 28.2.13676358 and 16 KB maximum/common page sizes, including RELRO alignment. All QuickLink Android builds use this module instead of the published AAR. LGPL-3.0 notices and source licenses are retained. This directory contains the corresponding Java, JNI, C source and build scripts.

## Standalone rebuild

Install JDK 21, Android SDK platform 36, NDK 28.2.13676358 and CMake 3.22.1. Set `JAVA_HOME` and `ANDROID_HOME` to those installations, accept their SDK licenses, and run:

```sh
cd standalone
./gradlew :spake2:assembleRelease --no-daemon
```

The AAR is written under `../build/outputs/aar/`. Its `classes.jar` contains the Java API, and `jni/<ABI>/libspake2.so` contains the native implementation. No QuickLink source, signing credentials or Flutter SDK are required to rebuild this library. `SOURCE-SHA256SUMS.txt` in the public mirror identifies the provided files. Formal release Git tags preserve their corresponding source trees.

## Modifying and relinking

QuickLink does not prohibit modifying this LGPL component or reverse engineering the application for debugging those modifications. The library's Java API is kept out of R8 obfuscation and cross-library optimization. Keep its public package, class and JNI interface compatible when replacing it.

The distributed APK provides the application's compiled DEX/native code. On a separate test device, an APK can be decoded with apktool, the `io/github/muntashirakon/crypto/spake2` smali classes replaced with those compiled from the rebuilt `classes.jar`, and `lib/<ABI>/libspake2.so` replaced with the rebuilt native library. Rebuild the APK, align it with Android `zipalign`, and sign it with your own `apksigner` key. Preserve the non-library application code and other licenses. A Play installation's signing key is not needed to create a separately signed modified APK; Android requires a different-key installation to be handled separately from the original installation. These instructions do not remove or replace an existing user's app automatically.
