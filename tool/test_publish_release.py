import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import publish_release as release


class SignedReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory()
        cls.private = Path(cls.keys.name) / 'private.pem'
        cls.public = Path(cls.keys.name) / 'public.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', str(cls.private)], check=True, capture_output=True)
        subprocess.run(['openssl', 'pkey', '-in', str(cls.private), '-pubout', '-out', str(cls.public)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def sign(self, data):
        return subprocess.check_output(['openssl', 'dgst', '-sha256', '-sign', str(self.private)], input=data)

    def fixture(self, directory):
        version = '1.2.3'
        library = b'synthetic replaceable library\n'
        archive = directory / f'QuickLink-{version}-linux-x64.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            info = tarfile.TarInfo('./lib/libwebrtc.so')
            info.size = len(library)
            tar.addfile(info, io.BytesIO(library))
        deb = directory / f'QuickLink-{version}-linux-x64.deb'
        deb.write_bytes(b'synthetic installer')
        def info(path):
            return {'sha256': release.sha(path), 'bytes': path.stat().st_size}
        def update_info(path):
            return {'file': path.name, 'url': f'https://github.com/{release.REPOSITORY}/releases/download/v{version}/{path.name}', **info(path)}
        payload = json.dumps({'release': version, 'build_number': 100, 'channel': 'stable',
                              'platforms': {'linux-x64': update_info(archive)}, 'installers': {'linux-x64-deb': update_info(deb)}}).encode()
        update = directory / 'updates.json'
        update.write_text(json.dumps({'payload': base64.b64encode(payload).decode(), 'signature': base64.b64encode(self.sign(payload)).decode()}))
        (directory / 'DESKTOP-SHA256SUMS.txt').write_text(''.join(f'{release.sha(p)}  {p.name}\n' for p in [archive, deb, update]))
        for name in ['args.gn', 'revisions.txt', 'REBUILD.md', 'THIRD-PARTY-SOURCES-WebRTC-linux.tar.xz.part-000', 'licenses-LGPL.txt']:
            (directory / name).write_text('synthetic vendor source fixture\n')
        proof = {'library_sha256': hashlib.sha256(library).hexdigest(), 'files': {p.name: info(p) for p in directory.iterdir() if not p.name.startswith(('QuickLink-', 'updates', 'DESKTOP-'))}}
        (directory / 'source-manifest.json').write_text(json.dumps(proof))
        self.seal(directory)

    def seal(self, directory):
        manifest = {'schema': 1, 'release': '1.2.3', 'channel': 'stable', 'build_number': 100,
                    'files': {p.name: {'sha256': release.sha(p), 'bytes': p.stat().st_size} for p in directory.iterdir() if not p.name.startswith('desktop-release.')}}
        path = directory / 'desktop-release.json'
        path.write_text(json.dumps(manifest))
        (directory / 'desktop-release.json.sig').write_bytes(self.sign(path.read_bytes()))
        return release.sha(path)

    def test_valid_signed_release(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(release, 'KEY', self.public):
            directory = Path(temp); self.fixture(directory)
            self.assertEqual(release.verify(directory, release.sha(directory / 'desktop-release.json'))['release'], '1.2.3')

    def test_changed_installer_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(release, 'KEY', self.public):
            directory = Path(temp); self.fixture(directory)
            (directory / 'QuickLink-1.2.3-linux-x64.deb').write_bytes(b'changed installer')
            with self.assertRaisesRegex(ValueError, 'Changed or missing asset'):
                release.verify(directory, release.sha(directory / 'desktop-release.json'))

    def test_unrelated_vendor_sources_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(release, 'KEY', self.public):
            directory = Path(temp); self.fixture(directory)
            proof = directory / 'source-manifest.json'
            data = json.loads(proof.read_text()); data['library_sha256'] = '0' * 64; proof.write_text(json.dumps(data))
            digest = self.seal(directory)
            with self.assertRaisesRegex(ValueError, 'do not match the shipped native library'):
                release.verify(directory, digest)

    def test_untrusted_manifest_signature_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(release, 'KEY', self.public):
            directory = Path(temp); self.fixture(directory)
            (directory / 'desktop-release.json.sig').write_bytes(b'not a signature')
            with self.assertRaises(subprocess.CalledProcessError):
                release.verify(directory, release.sha(directory / 'desktop-release.json'))


if __name__ == '__main__':
    unittest.main()
