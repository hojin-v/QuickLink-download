# QuickLink

내 기기를 연결해 파일, 클립보드와 원격 화면을 공유합니다.

이 저장소는 **정식 PC 배포 파일과 업데이트 정보**를 제공합니다. 앱 소스와 베타 검증은 별도 비공개 저장소에서 관리합니다.

## 다운로드

- **Linux x64:** [Ubuntu·Debian 설치 파일(.deb)](https://github.com/hojin-v/QuickLink-download/releases/download/v0.8.10/QuickLink-0.8.10-linux-x64.deb) · [압축본·전체 파일](https://github.com/hojin-v/QuickLink-download/releases/latest)
- **Android:** [Google Play에서 다운로드](https://play.google.com/store/apps/details?id=com.hnode.quicklink) · 정식 `0.8.12`
- **Windows:** 호환성 검증 중입니다. 아직 정식 배포 파일을 제공하지 않습니다.

Ubuntu·Debian에서는 `.deb`만 받으면 됩니다. 대응 소스·라이선스 자료는 재빌드용이며 일반 설치에는 필요하지 않습니다.

## Linux 설치와 업데이트

Ubuntu·Debian에서는 `QuickLink-버전-linux-x64.deb`를 **소프트웨어 설치 앱**으로 열어 설치합니다. 시스템 인증을 마치면 앱 목록에서 실행하고, 소프트웨어 관리 앱 또는 **QuickLink → 설정 → 앱 정보 → 앱 제거**로 제거할 수 있습니다.

압축본은 `QuickLink-버전-linux-x64.tar.gz`를 풀고 **`quicklink-setup`을 더블클릭**하면 GUI로 설치·제거합니다. `quicklink`를 직접 실행하거나 기존 `./install.sh`를 사용할 수도 있습니다. 이전 압축 설치본은 기존 앱을 종료한 뒤 새 관리 창에서 제거하고 `.deb`로 전환하세요. 제거 시 받은 파일·연결 설정은 보존합니다. 실행 파일을 이미 삭제해 이전 아이콘만 남았다면 새 `quicklink-setup`의 **이전 바로가기 정리**를 사용합니다.

Linux x64·GTK 3·PulseAudio 환경이 필요하며 Wayland 원격 화면·입력은 데스크톱의 승인과 지원에 따라 동작합니다. 기본 검증 환경은 Ubuntu 26.04입니다.

다음 버전부터 **설정 → 앱 정보 → 업데이트 확인**에서 다운로드하고 적용할 수 있습니다. 시스템 패키지 설치본은 OS 인증창을 통해 적용합니다. 전송과 원격 세션을 마친 뒤 적용하면 앱이 다시 시작됩니다. 서명·해시를 검사하고 새 버전이 시작되지 않으면 이전 설치로 복구합니다. 기기 인증·설정·받은 파일은 설치 버전과 별도로 유지합니다.

정식 배포는 `0.8.3` 같은 **x.y.z**, 비공개 베타 수정본은 `0.8.3-20` 같은 **x.y.z-n**으로 구분합니다. 정식 수정은 패치 버전 자체를 올리며 기존 파일을 덮어쓰지 않습니다. 수동 다운로드는 함께 제공하는 `DESKTOP-SHA256SUMS.txt`로 검증할 수 있습니다. `updates.json`은 앱이 사용하는 서명된 정식 업데이트 정보입니다.

## 개인정보와 문의

- [개인정보처리방침](https://hnode.me/privacy/quicklink)
- 개발·운영: **hnode**
- 문의: **hnode.dev@gmail.com**

오픈소스 구성요소와 라이선스는 앱의 설정 → 앱 정보에서 확인할 수 있습니다.

이전 `0.8.3` Android 개발자 베타에 포함됐던 LGPL SPAKE2의 [Java/JNI/C 원본·독립 빌드 및 재결합 안내](third_party/spake2-android/UPSTREAM.md)를 보존합니다. 이후 버전의 공식 BoringSSL 기반 구현에서는 이 의존성을 사용하지 않습니다. 이 폴더는 구버전 배포에 필요한 원본이므로 삭제하지 않으며, QuickLink 전체 앱 소스와 분리됩니다. 현재 버전의 구성요소·라이선스는 해당 앱의 고지를 확인하세요.

## 저장소 구분과 배포 자동화

Android와 PC의 공통 앱 소스 및 개발자 베타는 **비공개 `hojin-v/QuickLink`**에서 관리합니다. 이 공개 저장소에는 앱 소스를 복제하지 않습니다. GitHub가 제공하는 `Source code` 압축 파일도 이 다운로드 저장소의 안내·배포 도구·제3자 자료만 포함합니다.

```text
.github/workflows/    공개 PC 릴리스의 검증·게시 작업
keys/                앱에 고정된 업데이트 검증용 공개 키
tool/               공개 산출물 검증 도구
third_party/         구버전 배포에 필요한 제3자 대응 소스 보존
GitHub Releases      정식 설치 파일, 서명된 업데이트, 버전별 제3자 고지·소스
```

`Publish signed PC release` 작업은 준비된 공개 초안 ID와 매니페스트 해시를 받아 설치 파일의 서명·해시, 업데이트 URL, 네이티브 라이브러리와 대응 소스의 일치를 확인한 뒤 게시합니다. 이 작업은 이 저장소의 `GITHUB_TOKEN`만 사용하며 비공개 앱 소스나 Play 서비스 계정 키에 접근하지 않습니다. 서명용 개인 키는 이 저장소에 두지 않습니다.

비공개 빌드에서 공개 초안으로 전달할 때는 배포 저장소에 한정된 쓰기 권한을 사용합니다. 최초 운영자 전달은 기존 GitHub 로그인으로 실행할 수 있으며, 이 로그인 토큰을 Actions Secret에 복사하지 않습니다. 공개한 설치 파일은 덮어쓰지 않고 다음 정식 버전으로 배포합니다.

## 네이티브 라이브러리 재빌드

Linux 릴리스에 첨부하는 `source-manifest.json`, `args.gn`, `revisions.txt`, `REBUILD.md`와 `THIRD-PARTY-SOURCES-WebRTC-linux.tar.xz.part-*`가 해당 라이브러리의 대응 자료입니다. 분할 파일을 숫자 순으로 합쳐 풀고, 기록된 버전의 depot_tools를 준비한 뒤 **`depot_tools/ensure_bootstrap`을 먼저 실행**하세요. `DEPOT_TOOLS_UPDATE=0`으로 도구 버전을 유지합니다. 패키지의 GN 설정과 컴파일러·sysroot 설치 스크립트로 재빌드할 수 있습니다.

빌드한 호환 `libwebrtc.so`는 앱 압축본의 `lib/libwebrtc.so`를 교체하여 사용할 수 있습니다. 이를 위해 QuickLink 앱 소스를 공개하거나 앱 전체를 다시 컴파일할 필요는 없습니다. 설치 관리자·자동 업데이트가 원본 파일을 복원할 수 있으므로 라이브러리를 바꾼 실험본은 사용자 압축본으로 별도 보관하세요.
