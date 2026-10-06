// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import vercel from '@astrojs/vercel';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Canonical origin — used for the sitemap, canonical URLs and absolute OG links.
  site: 'https://zosc.com',

  // /blog/* only 301s to the external blog now — keep redirecting pages out of
  // the sitemap so Search Console doesn't flag "page with redirect".
  integrations: [sitemap({ filter: (page) => !page.includes('/blog/') })],

  vite: {
    plugins: [tailwindcss()],
    // Load the shared repo-root .env (R2 + AI keys) in local dev.
    envDir: '..'
  },

  // Legacy URL redirects migrated from the old static site (redirects.json /
  // vercel.json) so old WordPress links keep working after cutover.
  redirects: {
    // /resume/ was renamed to /about/ (2026-07-05).
    '/resume/': '/about/',
    '/resume-2/': '/about/',
    '/project/': '/works/',
    '/project/page/2/': '/works/',
    '/project/page/3/': '/works/',
    '/project/page/4/': '/works/',
    '/portfolio/': '/works/',
    '/portfolio/nfts/': '/works/',
    '/portfolio/projects/': '/works/',
    '/portfolio/projects/page/2/': '/works/',
    '/portfolio/projects/page/3/': '/works/',
    '/portfolio/works/': '/works/',
    '/project/xr/': '/project/vivo-xr/',
    '/project/open-title/': '/project/talos-principle/',
    '/project/luna-os-ar-3d主题设定/': '/project/luna-os-ar-theme/',
    '/project/nft空投与铸造-蝴蝶大胡子/': '/project/nft-asset-design/',
    '/project/三维ui可视化探索/': '/project/3d-ui-exploration/',
    '/project/中国移动cave空间/': '/project/china-mobile-cave/',
    '/project/时间花园/': '/project/time-garden/',
    '/project/星球鲸鱼太阳系两个diy/': '/project/wallpaper-universal-design/',
    '/project/艺术氛围天气壁纸/': '/project/dynamic-weather-art/',
    '/project/霓虹主题天气元素生日模板/': '/project/diy-motion-elements/',
    // Old WordPress blog permalinks — straight to the standalone blog (avoids
    // a hop through /blog/<slug>).
    '/2017/06/06/18/28/29/2831/wind/uncategorized/zosc/':
      'https://blog.zosc.com/',
    '/2017/07/01/02/28/51/6714/silence-is-a-eternal-theme/uncategorized/zosc/':
      'https://blog.zosc.com/',
  },

  adapter: vercel()
});