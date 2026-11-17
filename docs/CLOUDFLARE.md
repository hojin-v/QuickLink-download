# Download website hosting

The website is hosted on **Cloudflare Workers Static Assets**, with the hostname **quicklink.hnode.me**. Source files remain in `website/` in this repository. Installers, update metadata, signatures and vendor source archives remain in GitHub Releases. Android distribution remains on Google Play. The previous GitHub Pages address redirects visitors after the new HTTPS page has passed verification.

This is an asset-only deployment: no application Worker script, database, paid plan or server build is required. Wrangler is pinned in `package-lock.json` and used only for deployment. Uploads include only `website/`; repository keys, tools and Git history are not served as website assets.

## Connect the Cloudflare account once

In [repository Actions secrets](https://github.com/hojin-v/QuickLink-download/settings/secrets/actions), add:

| Name | Value |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | A Cloudflare API token authorized to deploy Workers in the selected account and manage the custom domain in the `hnode.me` zone. |
| `CLOUDFLARE_ACCOUNT_ID` | The account ID of the account that manages `hnode.me`. The workflow also accepts this ID as an Actions variable. |

Create the token at [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens). Select the account that contains `hnode.me`, with **Account → Workers Scripts → Edit** (or Workers product Admin in the granular permission interface, required for the first Worker creation). Include **Zone → Workers Routes → Edit/Write** and **Zone → Zone → Read**, limited to **hnode.me**. No access to unrelated zones, storage, billing or Play credentials is needed. Never use the Global API Key or commit the token. Once the Worker exists, its account permission can be narrowed to that Worker's Editor scope.

The account ID appears in the Cloudflare dashboard URL or in Workers & Pages → account details. The ID identifies the account and does not itself authorize changes.

## Deployment

1. Add the two values above.
2. Open **Actions → Publish download website to Cloudflare → Run workflow** on `main`.
3. Wrangler uploads `website/` and creates the **quicklink.hnode.me** custom domain and its managed DNS/certificate. `hnode.me` must be active in that account. There must not be an unrelated DNS record or Worker occupying `quicklink.hnode.me`; review any conflict rather than deleting other services.
4. The workflow confirms the public HTTPS page. Initial certificate issuance can take longer than an upload. If it reports DNS/TLS still pending, wait for Cloudflare's Domains & Routes status before rerunning.

Subsequent changes to website or deployment inputs on `main` deploy automatically. The same workflow can be rerun manually. No new API token is needed for each release. The landing page reads the latest stable PC installer from the public GitHub Releases API, so publishing a new installer does not require a website rebuild.

Local preparation (no Cloudflare login required):

```sh
npm ci
npm run check
npm run deploy:check
```

Local publication, if needed, uses an authenticated Wrangler session or the same two environment variables:

```sh
npm run deploy
```

## Move the public address

The Cloudflare workflow confirms the new HTTPS page before invoking the legacy Pages workflow. That second job replaces the old GitHub Pages content with `legacy-pages/`, a redirect to **https://quicklink.hnode.me/** that preserves section anchors. It has a second independent HTTPS/content check; a failed Cloudflare deployment cannot replace the existing working page with a broken redirect. GitHub Pages no longer deploys product content or runs on website pushes on its own.

The Cloudflare website already declares the new domain in its canonical/Open Graph URLs. After the first successful deployment, update the repository homepage, README and hnode article to the new domain. The existing hnode article's old Pages link also continues to work through the redirect.

References: [static asset configuration](https://developers.cloudflare.com/workers/static-assets/get-started/), [custom domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/), [Workers permissions](https://developers.cloudflare.com/workers/authorization/workers/).
