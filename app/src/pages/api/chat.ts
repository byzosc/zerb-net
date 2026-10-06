import type { APIRoute } from 'astro';
import { buildSystemPrompt } from '../../lib/knowledge';
import { resolveProvider, modelFor, streamChat, type ChatMsg } from '../../lib/providers';
import { checkRateLimit } from '../../lib/ratelimit';

export const prerender = false;

const env = (k: string): string | undefined =>
  process.env[k] ?? (import.meta.env as Record<string, string>)[k];

const num = (k: string, d: number) => {
  const n = parseInt(env(k) || '', 10);
  return Number.isFinite(n) ? n : d;
};

const txt = (s: string, status: number) =>
  new Response(s, { status, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });

export const POST: APIRoute = async ({ request, clientAddress }) => {
  const provider = resolveProvider();
  if (!provider) {
    return txt('AI is not configured yet. Set GEMINI_API_KEY (or another provider key).', 503);
  }

  const ip = clientAddress || 'unknown';
  const limit = await checkRateLimit(ip);
  if (!limit.ok) {
    const msg =
      limit.reason === 'minute'
        ? 'Slow down a moment — too many questions in a short time.'
        : limit.reason === 'day'
        ? "You've hit today's question limit. Try again tomorrow, or email zcbgood@gmail.com."
        : 'The assistant is busy right now. Please try again later.';
    return txt(msg, 429);
  }

  let payload: { messages?: ChatMsg[] };
  try {
    payload = await request.json();
  } catch {
    return txt('Bad request.', 400);
  }

  const maxInput = num('AI_MAX_INPUT_CHARS', 500);
  const history = Array.isArray(payload.messages) ? payload.messages : [];
  // keep the last few turns, validate + clamp
  const messages: ChatMsg[] = history
    .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .slice(-8)
    .map((m) => ({ role: m.role, content: m.content.slice(0, maxInput) }));

  if (!messages.length || messages[messages.length - 1].role !== 'user') {
    return txt('No question provided.', 400);
  }

  const system = await buildSystemPrompt();
  const model = modelFor(provider.provider);
  const maxOutputTokens = num('AI_MAX_OUTPUT_TOKENS', 600);

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        for await (const chunk of streamChat(provider.provider, provider.key, {
          system,
          messages,
          model,
          maxOutputTokens,
        })) {
          controller.enqueue(encoder.encode(chunk));
        }
      } catch (e) {
        controller.enqueue(
          encoder.encode('\n\n(Sorry — the assistant hit an error. Try again or email zcbgood@gmail.com.)')
        );
        console.error('chat error', e);
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Accel-Buffering': 'no',
    },
  });
};
