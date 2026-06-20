if (!self.define) {
  let e,
    s = {};
  const c = (c, i) => (
    (c = new URL(c + '.js', i).href),
    s[c] ||
      new Promise((s) => {
        if ('document' in self) {
          const e = document.createElement('script');
          ((e.src = c), (e.onload = s), document.head.appendChild(e));
        } else ((e = c), importScripts(c), s());
      }).then(() => {
        let e = s[c];
        if (!e) throw new Error(`Module ${c} didn’t register its module`);
        return e;
      })
  );
  self.define = (i, t) => {
    const a = e || ('document' in self ? document.currentScript.src : '') || location.href;
    if (s[a]) return;
    let n = {};
    const f = (e) => c(e, a),
      d = { module: { uri: a }, exports: n, require: f };
    s[a] = Promise.all(i.map((e) => d[e] || f(e))).then((e) => (t(...e), n));
  };
}
define(['./workbox-f8dc152a'], function (e) {
  'use strict';
  (importScripts(),
    self.skipWaiting(),
    e.clientsClaim(),
    e.precacheAndRoute(
      [
        {
          url: '/_next/static/-nL1jQC3Zm5vDj0T_xLtT/_buildManifest.js',
          revision: '5a61c82a0fc442c1d5318824ccd36a8d',
        },
        {
          url: '/_next/static/-nL1jQC3Zm5vDj0T_xLtT/_ssgManifest.js',
          revision: 'b6652df95db52feb4daf4eca35380933',
        },
        { url: '/_next/static/chunks/198.3a1e8fc8e360f387.js', revision: '3a1e8fc8e360f387' },
        { url: '/_next/static/chunks/286.cecb5efa15a5d782.js', revision: 'cecb5efa15a5d782' },
        { url: '/_next/static/chunks/351-31a5108419766c7e.js', revision: '31a5108419766c7e' },
        { url: '/_next/static/chunks/594a7007-334b43fbe1002424.js', revision: '334b43fbe1002424' },
        { url: '/_next/static/chunks/626-1c62f154c871a081.js', revision: '1c62f154c871a081' },
        { url: '/_next/static/chunks/709-e9b499295f137a4c.js', revision: 'e9b499295f137a4c' },
        { url: '/_next/static/chunks/839.8f7fdd8ff1b64336.js', revision: '8f7fdd8ff1b64336' },
        { url: '/_next/static/chunks/950.f905d0faa532035c.js', revision: 'f905d0faa532035c' },
        { url: '/_next/static/chunks/987.defd0d4fd74d32b9.js', revision: 'defd0d4fd74d32b9' },
        {
          url: '/_next/static/chunks/app/_not-found/page-983eff2630e86754.js',
          revision: '983eff2630e86754',
        },
        {
          url: '/_next/static/chunks/app/api/search/route-1ecece577f39d077.js',
          revision: '1ecece577f39d077',
        },
        {
          url: '/_next/static/chunks/app/docs/%5B%5B...slug%5D%5D/page-c745876b4e9427b3.js',
          revision: 'c745876b4e9427b3',
        },
        {
          url: '/_next/static/chunks/app/docs/layout-ba6b678490f4736c.js',
          revision: 'ba6b678490f4736c',
        },
        {
          url: '/_next/static/chunks/app/layout-71d22e60e2f4dc08.js',
          revision: '71d22e60e2f4dc08',
        },
        { url: '/_next/static/chunks/app/page-d5d5e5495dee6a00.js', revision: 'd5d5e5495dee6a00' },
        { url: '/_next/static/chunks/main-716310e43d0389d4.js', revision: '716310e43d0389d4' },
        { url: '/_next/static/chunks/main-app-1504e977513adc95.js', revision: '1504e977513adc95' },
        {
          url: '/_next/static/chunks/pages/_app-c30c3d3c7f93912b.js',
          revision: 'c30c3d3c7f93912b',
        },
        {
          url: '/_next/static/chunks/pages/_error-ea86e197ecb5d085.js',
          revision: 'ea86e197ecb5d085',
        },
        {
          url: '/_next/static/chunks/polyfills-42372ed130431b0a.js',
          revision: '846118c33b2c0e922d7b3a7676f81f6f',
        },
        { url: '/_next/static/chunks/webpack-9e9f12d037f9f3c4.js', revision: '9e9f12d037f9f3c4' },
        { url: '/_next/static/css/3ada410c0d8a43b0.css', revision: '3ada410c0d8a43b0' },
        { url: '/_next/static/css/47ecc487b19f2441.css', revision: '47ecc487b19f2441' },
        {
          url: '/_next/static/media/19cfc7226ec3afaa-s.woff2',
          revision: '9dda5cfc9a46f256d0e131bb535e46f8',
        },
        {
          url: '/_next/static/media/21350d82a1f187e9-s.woff2',
          revision: '4e2553027f1d60eff32898367dd4d541',
        },
        {
          url: '/_next/static/media/8e9860b6e62d6359-s.woff2',
          revision: '01ba6c2a184b8cba08b0d57167664d75',
        },
        {
          url: '/_next/static/media/ba9851c3c22cd980-s.woff2',
          revision: '9e494903d6b0ffec1a1e14d34427d44d',
        },
        {
          url: '/_next/static/media/c5fe6dc8356a8c31-s.woff2',
          revision: '027a89e9ab733a145db70f09b8a18b42',
        },
        {
          url: '/_next/static/media/df0a9ae256c0569c-s.woff2',
          revision: 'd54db44de5ccb18886ece2fda72bdfe0',
        },
        {
          url: '/_next/static/media/e4af272ccee01ff0-s.p.woff2',
          revision: '65850a373e258f1c897a2b3d75eb74de',
        },
        { url: '/manifest.json', revision: 'd83ff983243718695fe7417e7b97736a' },
        { url: '/search-index.json', revision: '50912e2345708e7b6f814ad6e6bf3e0a' },
        { url: '/swe-worker-5c72df51bb1f6ee0.js', revision: '76fdd3369f623a3edcf74ce2200bfdd0' },
      ],
      { ignoreURLParametersMatching: [/^utm_/, /^fbclid$/] },
    ),
    e.cleanupOutdatedCaches(),
    e.registerRoute(
      '/',
      new e.NetworkFirst({
        cacheName: 'start-url',
        plugins: [
          {
            cacheWillUpdate: async ({ response: e }) =>
              e && 'opaqueredirect' === e.type
                ? new Response(e.body, { status: 200, statusText: 'OK', headers: e.headers })
                : e,
          },
        ],
      }),
      'GET',
    ),
    e.registerRoute(
      /^https?.*/,
      new e.NetworkFirst({
        cacheName: 'offlineCache',
        plugins: [new e.ExpirationPlugin({ maxAgeSeconds: 86400, maxEntries: 200 })],
      }),
      'GET',
    ),
    (self.__WB_DISABLE_DEV_LOGS = !0));
});
