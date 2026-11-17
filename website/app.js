// No analytics, cookies, account sign-in or download proxy.
const english = {
  skip:'Skip to content',navFeatures:'Features',navStart:'Get started',download:'Download ↗',platforms:'ANDROID + LINUX',
  headline:'Two devices.<br><em>One flow.</em>',intro:'A copied thought. A photo you just took.<br class="wide-only"> A file on your PC. Bring your devices together.',getStarted:'Get QuickLink ↗',explore:'See what connects ↓',heroNote:'Free · Connect with device approval',clipboard:'Clipboard',myDevices:'Your devices, connected',
  featuresEyebrow:'KEEP YOUR DAY MOVING',featuresTitle:'Move a file. Paste a thought.<br>Reach your desktop.',featuresIntro:'Keep going across your devices<br class="wide-only"> without sending everything to yourself.',filesTitle:'Files go both ways.<br>Everything in one place.',filesBody:'Send files and folders, then find received files and transfer history together. Choose a list or grid view.',demoComplete:'Transfer complete · Example',clipTitle:'What you copied.<br>What you just captured.',clipBody:'Share text with your connected devices. Enable photo sync to send new photos to your PC, with permissions you choose.',clipLimit:'Android clipboard limitations ↗',remoteTitle:'See your PC.<br>Control it from your phone.',remoteBody:'Continue a task with remote desktop, or use your phone as a trackpad. Connect with a device you have approved.',remoteNote:'Remote screen and input require operating system permission.',
  appEyebrow:'A PLACE FOR YOUR DEVICES',appTitle:'See your connections.<br>Choose what to share.',appBody:'Manage connections and clipboard sharing in My Devices, and find your files in Transfers. Keep the controls you need close at hand.',detailOne:'Connection approval and clipboard controls per device',detailTwo:'Received and sent files, together',detailThree:'List and grid views with file search',readStory:'Read the QuickLink story ↗',devicesScreen:'My Devices · Korean interface',transfersScreen:'Transfers · Korean interface',
  startEyebrow:'YOUR FIRST CONNECTION',startTitle:'Install on both devices.<br>Then bring them together.',stepOneTitle:'Install on your phone and PC',stepOne:'Get the Android app on Google Play and the Linux installer below.',stepTwoTitle:'Connect on the same network',stepTwo:'Open the app and select your device. For remote networks, a reachable VPN connection can provide a route.',stepThreeTitle:'Approve and start sharing',stepThree:'Approve the connection on your device. Turn on clipboard and photo sync only when you need them.',
  downloadEyebrow:'READY FOR YOUR DEVICES',downloadTitle:'Download QuickLink',releaseNotes:'Release history ↗',androidDesc:'Stable release on Google Play<br>Android 8.0 or later',playDownload:'Install from Google Play ↗',androidNote:'Install and update through Google Play',linuxDesc:'Installer for Ubuntu and Debian<br>Use the archive on other distributions.',debDownload:'Download .deb ↓',tarDownload:'Archive (.tar.gz) ↗',windowsDesc:'A Windows release is in preparation.<br>No stable installer is available yet.',comingSoon:'Coming later',checkReleases:'Check releases ↗',installNote:'On Ubuntu or Debian, you only need the .deb file. Open it with your software installer and authenticate. You can delete the download after installation. For the archive, extract it and launch quicklink-setup.',systemNote:'Linux x64 · GTK 3 · PulseAudio required. Primary validation: Ubuntu 26.04. Wayland remote screen and input depend on your desktop’s support and approval.',
  faqTitle:'Before you<br>connect.',faqOneTitle:'Can I connect across different networks?',faqOne:'The devices must be able to reach one another. Outside the same network, provide a route such as a VPN. QuickLink is not tied to a particular VPN brand; connectivity depends on your network configuration.',faqTwoTitle:'Will copying on Android automatically send to my PC?',faqTwo:'Android restricts background clipboard reading by ordinary apps. In-app sharing and the Android share menu are available, but automatic background forwarding with your existing keyboard may require an additional helper connection. PC-to-phone sharing and new photo sync are separate features.',faqThreeTitle:'Will it send my entire photo library?',faqThree:'Photo sync forwards newly captured photos while enabled and connected. It does not automatically transfer your existing library. You control photo permissions and whether synchronization is on.',faqFourTitle:'How do I update or uninstall on my PC?',faqFour:'Use Settings → App information → Check for updates in the app. A .deb installation uses operating system authentication. Uninstall through your software manager or the app’s installation manager; received files and connection settings are preserved.',faqFiveTitle:'Where are the source code and license notices?',faqFive:'Application source and developer betas are managed privately. The public download repository provides stable PC installers and update metadata. Open-source component notices and required corresponding sources are available in App information and the release attachments.',licenseLink:'Licenses and rebuild instructions ↗',footerText:'Connecting your devices. Made by hnode.',privacy:'Privacy policy',github:'Download repository ↗',contact:'Contact ↗'
};
const original = new Map([...document.querySelectorAll('[data-i18n]')].map(el => [el,el.innerHTML]));
let language='ko';
function setLanguage(next) {
  language=next; document.documentElement.lang=next;
  for(const [el,content] of original) el.innerHTML=next==='en' ? (english[el.dataset.i18n] ?? content) : content;
  const button=document.querySelector('#language'); button.textContent=next==='en'?'한국어':'EN';
  button.setAttribute('aria-label',next==='en'?'한국어로 보기':'Switch to English');
  document.title=next==='en'?'QuickLink — Two devices. One flow.':'QuickLink — 휴대폰과 PC, 하던 일을 그대로';
  try {localStorage.setItem('quicklink-language',next);} catch {}
}
document.querySelector('#language').addEventListener('click',()=>setLanguage(language==='ko'?'en':'ko'));
try { if(localStorage.getItem('quicklink-language')==='en' || (!localStorage.getItem('quicklink-language') && !navigator.language.startsWith('ko'))) setLanguage('en'); } catch {}

// The installers keep working without JavaScript or if GitHub's public API is unavailable.
// Only HTTPS assets in this repository's stable release namespace can replace the fallbacks.
async function refreshRelease() {
  try {
    const response=await fetch('https://api.github.com/repos/hojin-v/QuickLink-download/releases/latest',{signal:AbortSignal.timeout(6000),headers:{Accept:'application/vnd.github+json'}});
    if(!response.ok) return;
    const release=await response.json();
    if(release.draft || release.prerelease || !/^v\d+\.\d+\.\d+$/.test(release.tag_name)) return;
    const version=release.tag_name.slice(1);
    const allowed=`https://github.com/hojin-v/QuickLink-download/releases/download/${release.tag_name}/`;
    for(const [id,suffix] of [['deb-download','deb'],['tar-download','tar.gz']]) {
      const name=`QuickLink-${version}-linux-x64.${suffix}`;
      const asset=release.assets?.find(item=>item.name===name && item.browser_download_url===allowed+name);
      if(!asset) continue;
      document.getElementById(id).href=asset.browser_download_url;
      if(suffix==='deb') {
        document.getElementById('linux-version').textContent=`${release.tag_name} · x64`;
        if(asset.size>0) document.getElementById('deb-size').textContent=`${(asset.size/1024/1024).toFixed(1)} MB`;
      }
    }
  } catch { /* Published fallback links remain usable offline or under API rate limits. */ }
}
refreshRelease();
