import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Three pillars of the portfolio.
const PILLARS = ['motion', 'visual', 'code'] as const;

// Google's supported app types for SoftwareApplication.applicationCategory (checked 2026-10-08,
// developers.google.com/search/docs/appearance/structured-data/software-app). There is no
// "Productivity" type — map store categories onto this list instead of inventing one.
const APP_CATEGORIES = [
  'GameApplication', 'SocialNetworkingApplication', 'TravelApplication', 'ShoppingApplication',
  'SportsApplication', 'LifestyleApplication', 'BusinessApplication', 'DesignApplication',
  'DeveloperApplication', 'DriverApplication', 'EducationalApplication', 'HealthApplication',
  'FinanceApplication', 'SecurityApplication', 'BrowserApplication', 'CommunicationApplication',
  'DesktopEnhancementApplication', 'EntertainmentApplication', 'MultimediaApplication',
  'HomeApplication', 'UtilitiesApplication', 'ReferenceApplication',
] as const;

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    summary: z.string().default(''),
    // One project can belong to several pillars.
    pillars: z.array(z.enum(PILLARS)).default(['visual']),
    cover: z.string(), // root-relative URL, e.g. /media/images/projects/<slug>/x.webp
    coverLarge: z.string().optional(), // hi-res source for the full-width featured card
    year: z.union([z.string(), z.number()]).optional(),
    role: z.string().optional(),
    // Display ordering on listing pages; lower = earlier.
    order: z.number().default(100),
    // External link (e.g. product page). The project still gets a light case
    // page; this powers the "View the product →" CTA on it.
    externalUrl: z.string().url().optional(),
    // Label for the external CTA button.
    externalLabel: z.string().default('View the product'),
    draft: z.boolean().default(false),
    // v2: the homepage Code section shows only featured entries (3-4 products). Motion and
    // Visual ignore this flag and show their first 5 by `order` (rule lives in pages/index.astro).
    featured: z.boolean().default(false),
    // 'product' = something people can install or use. Product pages get a row of link
    // buttons and SoftwareApplication JSON-LD; plain projects render exactly as before.
    kind: z.enum(['project', 'product']).default('project'),
    // Link buttons, rendered in this order (the first one is the accent button).
    // type feeds the JSON-LD: store -> installUrl, download -> downloadUrl; when neither
    // exists the first site/source link becomes installUrl.
    links: z
      .array(
        z.object({
          label: z.string(),
          url: z.string().url(),
          type: z.enum(['store', 'download', 'site', 'source']),
        }),
      )
      .optional(),
    // SoftwareApplication facts — only what the store page / README / live site states.
    app: z
      .object({
        category: z.enum(APP_CATEGORIES),
        os: z.string().optional(), // operatingSystem
        requirements: z.string().optional(), // softwareRequirements
        free: z.boolean().default(false), // true -> offers { price: "0" }; only if stated
      })
      .optional(),
  }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    cover: z.string(),
    excerpt: z.string().default(''),
    draft: z.boolean().default(false),
  }),
});

export const collections = { projects, blog };
