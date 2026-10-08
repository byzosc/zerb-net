// JSON-LD node ids (v3, 2026-10-08). Layout.astro emits the Organization, Person and WebSite
// blocks on every page; product pages point their SoftwareApplication's author / publisher at the
// same nodes. One definition so the references can never drift apart: a reference to an @id that
// no block on the page defines is a dangling entity, not a link.
//
// zosc as Organization = the label things ship under (出品人), not a company or a lab. The Person
// stays the main entity; the two are tied by founder (Organization → Person) and worksFor /
// affiliation (Person → Organization).
export const SITE = 'https://zosc.com';
export const PERSON_ID = `${SITE}/#person`;
export const ORG_ID = `${SITE}/#organization`;
export const WEBSITE_ID = `${SITE}/#website`;
