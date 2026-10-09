#!/usr/bin/env bash
# Is Google still showing the old Astro favicon for zosc.com?  (2026-10-09)
#
# Google Search / Search Console draw site icons from Google's own favicon service, keyed by host.
# Its record for https://zosc.com was taken on 2026-10-06, when the declared PNG icons 404'd and the
# fallback /favicon.svg was still Astro's default logo. The site has served the Z since then
# (verified as Googlebot through Cloudflare, every entry point, identical md5), and the icon URLs
# were renamed to zosc-mark-* on 10-08 so Google must refetch them. There is no manual purge;
# Google's doc: "several days to several weeks". The record for https://www.zosc.com, fetched
# later, already holds the Z — so the moment the zosc.com record flips, search results follow.
#
#   tools/check-google-favicon.sh        → prints ASTRO (still old) or Z (updated) or OTHER
ASTRO_MD5=a4330b7d42cb   # first 12 hex of Google's 128px PNG of the Astro logo (2026-10-09)
Z_MD5=48e649239f22       # same service, www.zosc.com, already the Z (2026-10-09)
u="https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://zosc.com&size=128"
h=$(curl -s "$u" | md5sum | cut -c1-12)
case "$h" in
  "$ASTRO_MD5") echo "ASTRO — Google's zosc.com icon record not refreshed yet ($h)";;
  "$Z_MD5")     echo "Z — updated; search results will show the Z ($h)";;
  *)            echo "OTHER ($h) — changed; open the URL to look: $u";;
esac
