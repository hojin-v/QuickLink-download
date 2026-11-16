#!/usr/bin/env python3
"""Verify signed desktop assets in a public draft, then publish that exact draft."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

REPOSITORY = 'hojin-v/QuickLink-download'
ROOT = Path(__file__).resolve().parents[1]
KEY = ROOT / 'keys/updates.pem'


def api(path, method=None, data=None):
    args = ['gh', 'api', path]
    if method:
        args += ['--method', method]
    if data is not None:
        args += ['--input', '-']
    return json.loads(subprocess.check_output(args, input=json.dumps(data).encode() if data is not None else None))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_signature(data, signature, directory):
    message, sig = directory / 'message', directory / 'signature'
    message.write_bytes(data)
    sig.write_bytes(signature)
    subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(KEY), '-signature', str(sig), str(message)], check=True)


def verify(directory, expected_hash):
    manifest_path = directory / 'desktop-release.json'
    if sha(manifest_path) != expected_hash:
        raise ValueError('The draft differs from the explicitly selected manifest.')
    with tempfile.TemporaryDirectory() as temporary:
        verify_signature(manifest_path.read_bytes(), (directory / 'desktop-release.json.sig').read_bytes(), Path(temporary))
    manifest = json.loads(manifest_path.read_text())
    version = manifest['release']
    if manifest.get('schema') != 1 or manifest.get('channel') != 'stable' or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('A suffix-free stable desktop version is required.')
    files = manifest['files']
    required = {f'QuickLink-{version}-linux-x64.deb', f'QuickLink-{version}-linux-x64.tar.gz',
                'updates.json', 'DESKTOP-SHA256SUMS.txt', 'source-manifest.json', 'args.gn', 'revisions.txt', 'REBUILD.md'}
    if not required <= files.keys() or not any(name.startswith('THIRD-PARTY-SOURCES-') for name in files):
        raise ValueError('Installers, update metadata or corresponding vendor sources are missing.')
    for name, item in files.items():
        allowed = name in required or name.startswith(('THIRD-PARTY-SOURCES-WebRTC-linux.tar.xz.part-', 'licenses-')) or name == 'libwebrtc-linux-x64-pinned.zip'
        if not allowed or Path(name).name != name:
            raise ValueError('Unexpected public file: ' + name)
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('Changed or missing asset: ' + name)
    envelope = json.loads((directory / 'updates.json').read_text())
    payload_bytes = base64.b64decode(envelope['payload'], validate=True)
    with tempfile.TemporaryDirectory() as temporary:
        verify_signature(payload_bytes, base64.b64decode(envelope['signature'], validate=True), Path(temporary))
    payload = json.loads(payload_bytes)
    if (payload['release'], payload['build_number'], payload['channel']) != (version, manifest['build_number'], 'stable'):
        raise ValueError('Signed update identity differs.')
    for group, platform in [('platforms', 'linux-x64'), ('installers', 'linux-x64-deb')]:
        item = payload[group][platform]
        expected = files[item['file']]
        if any(item[k] != expected[k] for k in ['sha256', 'bytes']) or item['url'] != f'https://github.com/{REPOSITORY}/releases/download/v{version}/{item["file"]}':
            raise ValueError('Signed update asset differs.')
    proof = json.loads((directory / 'source-manifest.json').read_text())
    for relative, item in proof['files'].items():
        flat = relative.replace('/', '-')
        if flat not in files or files[flat] != item:
            raise ValueError('Incomplete vendor-source package: ' + relative)
    with tarfile.open(directory / f'QuickLink-{version}-linux-x64.tar.gz', 'r:gz') as archive:
        libraries = [m for m in archive.getmembers() if m.name.endswith('/lib/libwebrtc.so') and m.isfile()]
        if len(libraries) != 1:
            raise ValueError('Expected one replaceable WebRTC shared library.')
        with archive.extractfile(libraries[0]) as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != proof['library_sha256']:
                raise ValueError('Vendor sources do not match the shipped native library.')
    checksums = ''.join(f'{files[name]["sha256"]}  {name}\n' for name in required if name.startswith('QuickLink-') or name == 'updates.json')
    actual = set((directory / 'DESKTOP-SHA256SUMS.txt').read_text().splitlines())
    if actual != set(checksums.splitlines()):
        raise ValueError('Installer checksum list differs.')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-id', required=True, type=int)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.manifest_sha256):
        raise ValueError('Invalid manifest digest.')
    if os.environ.get('GITHUB_REPOSITORY', REPOSITORY) != REPOSITORY or api(f'repos/{REPOSITORY}')['private']:
        raise ValueError('Run in the public distribution repository only.')
    release = api(f'repos/{REPOSITORY}/releases/{args.release_id}')
    if not release['draft'] or release['prerelease']:
        raise ValueError('Only an unpublished stable draft may be processed.')
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        assets = {a['name']: a for a in release['assets']}
        if len(assets) != len(release['assets']):
            raise ValueError('Duplicate asset names.')
        for name, asset in assets.items():
            if Path(name).name != name:
                raise ValueError('Invalid asset name.')
            with (directory / name).open('wb') as stream:
                subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/releases/assets/{asset["id"]}', '-H', 'Accept: application/octet-stream'], stdout=stream, check=True)
            if (directory / name).stat().st_size != asset['size']:
                raise ValueError('Incomplete download.')
        manifest = verify(directory, args.manifest_sha256)
        if set(assets) != set(manifest['files']) | {'desktop-release.json', 'desktop-release.json.sig'}:
            raise ValueError('Unreviewed assets exist in the draft.')
    version, number = manifest['release'], manifest['build_number']
    reservation = {'release': version, 'build_number': number, 'channel': 'stable'}
    for previous in api(f'repos/{REPOSITORY}/releases?per_page=100'):
        if previous['draft'] or previous['prerelease']:
            continue
        match = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', previous['tag_name'])
        if match and tuple(map(int, match.groups())) >= tuple(map(int, version.split('.'))):
            raise ValueError('This version or a newer version is already public.')
    print(f'Verified QuickLink {version}, build {number}; {len(assets)} immutable public assets.')
    if args.publish:
        body = ('Linux x64 정식 배포입니다. Ubuntu·Debian에서는 `.deb` 파일을 소프트웨어 설치 앱으로 열어 설치하세요. '
                '압축본은 `quicklink-setup`으로 GUI 설치·제거할 수 있습니다. 설치 후 다운로드 파일은 삭제해도 됩니다.\n\n'
                '이후 업데이트는 QuickLink 설정 → 앱 정보 → 업데이트 확인에서 적용합니다. 기기 설정과 받은 파일은 유지됩니다.\n\n'
                'Android는 Google Play에서 별도 배포합니다. Windows 설치 파일은 아직 제공하지 않습니다. '
                '제3자 고지·대응 소스·재빌드 안내는 아래 첨부 파일에 포함되어 있습니다.\n\n'
                '<!-- quicklink-reservation: ' + json.dumps(reservation) + ' -->\n')
        result = api(f'repos/{REPOSITORY}/releases/{args.release_id}', 'PATCH',
                     {'draft': False, 'prerelease': False, 'tag_name': 'v' + version, 'name': 'QuickLink ' + version,
                      'make_latest': 'true', 'body': body})
        if result['draft'] or result['tag_name'] != 'v' + version:
            raise ValueError('Publication could not be verified.')
        print('PUBLISHED ' + result['html_url'])


if __name__ == '__main__':
    main()
