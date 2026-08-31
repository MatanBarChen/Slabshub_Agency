// SlabsHub storefront chat — Supabase Edge Function.
//
// The cloud version of prototype/sales-agent/server.py. Same agent loop, same
// three tools, same truth rules; the differences are all about being reachable
// from the open internet instead of from localhost:
//
//   * the catalog and the system prompt live in Postgres, so refreshing either
//     is a data update rather than a redeploy;
//   * conversation history is server-owned. The browser sends one message and a
//     conversation id, never the transcript, so a visitor cannot forge assistant
//     turns or smuggle instructions into the history;
//   * every request is throttled per IP. This endpoint spends money on each
//     call, so the rate limit is the tap, not a nicety.
//
// Deployed with verify_jwt = false: storefront visitors are anonymous by
// definition. Origin allowlist + rate limit are the access control.
import { createClient } from "jsr:@supabase/supabase-js@2";

const MODEL = Deno.env.get("AGENT_MODEL") ?? "claude-sonnet-5";
const ANTHROPIC_KEY = Deno.env.get("ANTHROPIC_API_KEY");

const MAX_TOOL_ROUNDS = 6;
const MAX_INPUT_CHARS = 2000;
const MAX_TURNS_PER_CONVERSATION = 60;
const HISTORY_LIMIT = 40;
const RATE_LIMIT_PER_HOUR = 40;
const CATALOG_TTL_MS = 60_000;

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

// ---------------------------------------------------------------- origins

const EXTRA_ORIGINS = (Deno.env.get("ALLOWED_ORIGINS") ?? "")
  .split(",").map((o) => o.trim()).filter(Boolean);

// The origin check keeps the widget from being casually re-embedded elsewhere;
// it is not the security boundary, since any client can set the header to
// whatever it likes. The rate limit is what actually protects the bill.
// "null" is what a page opened from file:// sends — that is the debug UI.
function originAllowed(origin: string | null): boolean {
  if (!origin || origin === "null") return true;
  if (EXTRA_ORIGINS.includes(origin)) return true;
  let host: string;
  try {
    host = new URL(origin).hostname;
  } catch {
    return false;
  }
  return host === "slabshub.com" || host.endsWith(".slabshub.com") ||
    host.endsWith(".myshopify.com") ||
    host === "localhost" || host === "127.0.0.1";
}

function cors(origin: string | null): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": origin ?? "*",
    "Access-Control-Allow-Headers": "content-type, authorization, apikey",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Vary": "Origin",
  };
}

function json(body: unknown, status: number, origin: string | null): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin) },
  });
}

// ---------------------------------------------------------------- identity

// Visitor IPs are only ever stored hashed: the throttle needs to tell requesters
// apart, it does not need to know who they are.
async function hashIp(req: Request): Promise<string> {
  const raw = (req.headers.get("x-forwarded-for") ?? "unknown").split(",")[0].trim();
  const bytes = new TextEncoder().encode("slabshub-chat:" + raw);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].slice(0, 16)
    .map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function overRateLimit(ipHash: string): Promise<boolean> {
  const windowStart = new Date(Math.floor(Date.now() / 3_600_000) * 3_600_000).toISOString();
  const { data } = await supabase.rpc("bump_rate_limit", {
    p_ip_hash: ipHash,
    p_window_start: windowStart,
  });
  return typeof data === "number" && data > RATE_LIMIT_PER_HOUR;
}

// ---------------------------------------------------------------- catalog

type Product = {
  handle: string; title: string; status: string | null; type: string | null;
  vendor: string | null; inventory: number; price: number | null;
  price_max: number | null; url: string | null; image: string | null;
  description: string | null;
};

let catalogCache: { at: number; rows: Product[] } | null = null;

async function catalog(): Promise<Product[]> {
  if (catalogCache && Date.now() - catalogCache.at < CATALOG_TTL_MS) return catalogCache.rows;
  const { data, error } = await supabase.from("products").select("*");
  if (error) throw error;
  catalogCache = { at: Date.now(), rows: (data ?? []) as Product[] };
  return catalogCache.rows;
}

let promptCache: { at: number; text: string } | null = null;

async function systemPrompt(): Promise<string> {
  if (promptCache && Date.now() - promptCache.at < CATALOG_TTL_MS) return promptCache.text;
  const { data, error } = await supabase.from("config").select("value").eq("key", "system_prompt").single();
  if (error) throw error;
  promptCache = { at: Date.now(), text: data.value as string };
  return promptCache.text;
}

const GRADE_RE = /^(PSA|CGC|BGS)\s*(\d+)/i;
const WORD_RE = /[^0-9a-zA-Z֐-׿]+/;

function gradeOf(p: Product): string | null {
  const m = GRADE_RE.exec(p.title);
  if (m) return m[1].toUpperCase() + " " + m[2];
  return p.title.startsWith("RAW") ? "RAW" : null;
}

type SearchArgs = {
  query?: string; min_price?: number; max_price?: number; grade?: string;
  product_type?: string; in_stock_only?: boolean; limit?: number;
};

async function searchCatalog(a: SearchArgs, conversationId: string) {
  const products = await catalog();
  const inStockOnly = a.in_stock_only !== false;
  const limit = Math.min(Math.max(Number(a.limit ?? 6) || 6, 1), 12);
  const terms = (a.query ?? "").toLowerCase().split(WORD_RE).filter((t) => t.length > 1);

  const scored: Array<{ score: number; price: number; p: Product }> = [];
  let textMatches = 0;
  let outOfStockHits = 0;

  for (const p of products) {
    const title = p.title.toLowerCase();
    const hay = title + " " + (p.description ?? "").toLowerCase() + " " + (p.vendor ?? "").toLowerCase();
    let score = 0;
    for (const t of terms) {
      if (title.includes(t)) score += 3;
      else if (hay.includes(t)) score += 1;
    }
    if (terms.length && score === 0) continue;
    textMatches++;

    const price = Number(p.price ?? 0);
    if (a.min_price != null && price < Number(a.min_price)) continue;
    if (a.max_price != null && price > Number(a.max_price)) continue;

    const g = gradeOf(p) ?? "";
    if (a.grade && !g.replace(/\s/g, "").includes(a.grade.toUpperCase().replace(/\s/g, ""))) continue;
    if (a.product_type && !(p.type ?? "").toLowerCase().includes(a.product_type.toLowerCase())) continue;
    if (inStockOnly && p.inventory <= 0) { outOfStockHits++; continue; }

    scored.push({ score, price, p });
  }

  scored.sort((x, y) => y.score - x.score || y.price - x.price);

  // A search that found nothing is the purest demand signal we get: someone
  // wanted something specific and we had none of it.
  if (terms.length && scored.length === 0) {
    await supabase.from("demand").insert({
      event: outOfStockHits ? "out_of_stock" : (textMatches ? "filtered_out" : "no_match"),
      query: a.query ?? null,
      grade: a.grade ?? null,
      min_price: a.min_price ?? null,
      max_price: a.max_price ?? null,
      conversation_id: conversationId,
    });
  }

  const out = scored.slice(0, limit).map(({ p }) => ({
    title: p.title,
    grade: gradeOf(p),
    price_ils: p.price,
    price_max_ils: p.price_max !== p.price ? p.price_max : null,
    in_stock: p.inventory,
    url: p.url,
    type: p.type,
    description: (p.description ?? "").slice(0, 400) || null,
  }));

  const resp: Record<string, unknown> = { matches: scored.length, showing: out.length, products: out };
  if (terms.length) {
    resp.reminder = "If the exact card the customer asked about is NOT in 'products', " +
      "call record_wishlist for it now, before replying.";
  }
  return resp;
}

async function recordWishlist(
  a: { card: string; contact?: string; notes?: string },
  conversationId: string,
) {
  await supabase.from("wishlist").insert({
    card: a.card, contact: a.contact ?? null, notes: a.notes ?? null,
    conversation_id: conversationId,
  });
  return {
    status: "saved",
    note: "Recorded for Matan's daily sourcing review. Do not promise the card will be found, a timeframe, or a price.",
  };
}

// Word overlap, so a reworded repeat of the same ask still counts as one.
function sameRequest(a: string | null, b: string): boolean {
  const wa = new Set((a ?? "").toLowerCase().match(/[\p{L}\p{N}']+/gu) ?? []);
  const wb = new Set(b.toLowerCase().match(/[\p{L}\p{N}']+/gu) ?? []);
  if (!wa.size || !wb.size) return false;
  let shared = 0;
  for (const w of wa) if (wb.has(w)) shared++;
  return shared / (wa.size + wb.size - shared) >= 0.45;
}

async function requestHuman(
  a: { reason: string; summary: string; contact?: string },
  conversationId: string,
) {
  // Backstop for the prompt rule: one handoff per conversation. The model has
  // escalated the same request several times in a row before, which reaches
  // Matan as several separate interruptions about one customer.
  const cutoff = new Date(Date.now() - 15 * 60_000).toISOString();
  const { data: recent } = await supabase.from("handoffs")
    .select("summary, contact").gte("at", cutoff).order("at", { ascending: false }).limit(20);

  for (const prev of recent ?? []) {
    if (sameRequest(prev.summary, a.summary) || (a.contact && prev.contact === a.contact)) {
      return {
        status: "already_open",
        note: "This request is already with Matan - not logged again. Tell the customer it is " +
          "already passed on, and carry on helping them. If the card is one we do not stock, " +
          "the right tool is record_wishlist, not request_human.",
      };
    }
  }

  await supabase.from("handoffs").insert({
    reason: a.reason, summary: a.summary, contact: a.contact ?? null,
    conversation_id: conversationId,
  });
  return { status: "logged", note: "Matan has been notified. Do not promise a response time." };
}

const TOOLS = [
  {
    name: "search_catalog",
    description: "Search live SlabsHub inventory. English keywords only. Returns only real " +
      "products. Call this before naming any product, price or stock level.",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "English keywords: pokemon name, set, card number" },
        min_price: { type: "number", description: "Minimum price in ILS" },
        max_price: { type: "number", description: "Maximum price in ILS" },
        grade: { type: "string", description: "e.g. 'PSA 9', 'PSA 10', 'CGC 9', 'RAW'" },
        product_type: { type: "string", description: "'Pokemon TCG' or 'Accessories'" },
        in_stock_only: { type: "boolean", default: true },
        limit: { type: "integer", default: 6 },
      },
    },
  },
  {
    name: "record_wishlist",
    description: "Record a card the customer wants but the shop does not have right now, so Matan " +
      "can try to source it. Call after search_catalog came up empty for a specific card " +
      "and the customer confirmed interest. Include contact details only if the customer " +
      "gave them for this purpose.",
    input_schema: {
      type: "object",
      properties: {
        card: { type: "string", description: "English card description: name, set, number, grade if given. e.g. 'Charizard Base Set PSA 8'" },
        contact: { type: "string", description: "Email or WhatsApp the customer left for a restock heads-up, if any" },
        notes: { type: "string", description: "Budget, condition preference, or other context, in English" },
      },
      required: ["card"],
    },
  },
  {
    name: "request_human",
    description: "Last resort. Hand the conversation to Matan for a discount request, an existing " +
      "order, extra photos, an unhappy customer, or a purchase over 1,000 ILS of an item we stock. " +
      "Ask for the customer's contact details first. NEVER use this for a card we do not stock or a " +
      "restock heads-up - that is record_wishlist. Never call it twice in one conversation.",
    input_schema: {
      type: "object",
      properties: {
        reason: { type: "string", description: "discount | photos | order | high_value | unknown | unhappy" },
        summary: { type: "string", description: "What the customer wants, in one or two sentences" },
        contact: { type: "string", description: "Email or phone the customer gave, if any" },
      },
      required: ["reason", "summary"],
    },
  },
];

// ---------------------------------------------------------------- agent loop

// deno-lint-ignore no-explicit-any
type Msg = { role: string; content: any };

async function callAnthropic(system: string, messages: Msg[]) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": ANTHROPIC_KEY!,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({ model: MODEL, max_tokens: 1200, system, tools: TOOLS, messages }),
  });
  if (!r.ok) throw new Error("anthropic " + r.status + ": " + (await r.text()).slice(0, 400));
  return await r.json();
}

async function dispatch(name: string, input: Record<string, unknown>, conversationId: string) {
  // deno-lint-ignore no-explicit-any
  const a = input as any;
  if (name === "search_catalog") return await searchCatalog(a, conversationId);
  if (name === "record_wishlist") return await recordWishlist(a, conversationId);
  if (name === "request_human") return await requestHuman(a, conversationId);
  return { error: "unknown tool" };
}

async function runTurn(system: string, messages: Msg[], conversationId: string) {
  const trace: unknown[] = [];
  for (let round = 0; round < MAX_TOOL_ROUNDS; round++) {
    const resp = await callAnthropic(system, messages);
    const blocks = resp.content ?? [];
    messages.push({ role: "assistant", content: blocks });

    // deno-lint-ignore no-explicit-any
    const toolUses = blocks.filter((b: any) => b.type === "tool_use");
    if (toolUses.length === 0) {
      // deno-lint-ignore no-explicit-any
      const text = blocks.filter((b: any) => b.type === "text").map((b: any) => b.text).join("");
      return { reply: text.trim(), messages, trace };
    }

    const results = [];
    for (const tu of toolUses) {
      let out: unknown;
      try {
        out = await dispatch(tu.name, tu.input ?? {}, conversationId);
      } catch (e) {
        out = { error: String(e) };
      }
      trace.push({ tool: tu.name, input: tu.input ?? {}, output: out });
      results.push({ type: "tool_result", tool_use_id: tu.id, content: JSON.stringify(out) });
    }
    messages.push({ role: "user", content: results });
  }
  return { reply: "Sorry, I got stuck there. Can you rephrase?", messages, trace };
}

// Trim from the front, but never leave a tool_result as the first message —
// Anthropic rejects a history whose opening turn answers a tool call that is no
// longer there.
function trimHistory(messages: Msg[]): Msg[] {
  if (messages.length <= HISTORY_LIMIT) return messages;
  let out = messages.slice(-HISTORY_LIMIT);
  while (out.length) {
    const m = out[0];
    const plainUser = m.role === "user" &&
      // deno-lint-ignore no-explicit-any
      (typeof m.content === "string" || !(m.content as any[]).some((b) => b.type === "tool_result"));
    if (plainUser) break;
    out = out.slice(1);
  }
  return out.length ? out : messages.slice(-2);
}

// ---------------------------------------------------------------- handler

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

Deno.serve(async (req: Request) => {
  const origin = req.headers.get("origin");

  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
  if (!originAllowed(origin)) return json({ error: "origin not allowed" }, 403, origin);

  const url = new URL(req.url);

  if (req.method === "GET") {
    const products = await catalog().catch(() => [] as Product[]);
    return json({
      ok: true,
      model: MODEL,
      key: Boolean(ANTHROPIC_KEY),
      products: products.length,
      in_stock: products.filter((p) => p.inventory > 0).length,
    }, 200, origin);
  }

  if (req.method !== "POST") return json({ error: "not found" }, 404, origin);

  if (!ANTHROPIC_KEY) {
    return json({
      reply: "The chat is not configured yet - ANTHROPIC_API_KEY is missing.",
      trace: [],
    }, 200, origin);
  }

  const ipHash = await hashIp(req);
  if (await overRateLimit(ipHash)) {
    return json({
      reply: "You've sent a lot of messages in a short time. Give it a few minutes and try again.",
      trace: [], rate_limited: true,
    }, 429, origin);
  }

  let payload: { conversation_id?: string; message?: string };
  try {
    payload = await req.json();
  } catch {
    return json({ error: "bad json" }, 400, origin);
  }

  const message = (payload.message ?? "").toString().trim();
  if (!message) return json({ error: "message is required" }, 400, origin);
  if (message.length > MAX_INPUT_CHARS) {
    return json({ reply: "That message is a bit long for the chat - can you shorten it?", trace: [] }, 200, origin);
  }

  // Load or open a conversation. History is read from our side only; whatever
  // the browser thinks was said earlier is irrelevant.
  let conversationId = payload.conversation_id ?? "";
  let messages: Msg[] = [];
  let turns = 0;

  if (conversationId && UUID_RE.test(conversationId)) {
    const { data } = await supabase.from("conversations")
      .select("id, messages, turns").eq("id", conversationId).single();
    if (data) {
      messages = (data.messages ?? []) as Msg[];
      turns = data.turns ?? 0;
    } else {
      conversationId = "";
    }
  } else {
    conversationId = "";
  }

  if (!conversationId) {
    const { data, error } = await supabase.from("conversations")
      .insert({ origin, ip_hash: ipHash }).select("id").single();
    if (error) return json({ error: "could not start conversation" }, 500, origin);
    conversationId = data.id as string;
  }

  if (turns >= MAX_TURNS_PER_CONVERSATION) {
    return json({
      reply: "This chat has gone on a while - refresh the page to start a fresh one and I'll pick it back up.",
      conversation_id: conversationId, trace: [],
    }, 200, origin);
  }

  messages = trimHistory(messages);
  messages.push({ role: "user", content: message });

  try {
    const system = await systemPrompt();
    const result = await runTurn(system, messages, conversationId);
    await supabase.from("conversations").update({
      messages: result.messages, turns: turns + 1, updated_at: new Date().toISOString(),
    }).eq("id", conversationId);
    return json({ reply: result.reply, conversation_id: conversationId, trace: result.trace }, 200, origin);
  } catch (e) {
    console.error("chat turn failed", e);
    return json({
      reply: "Something went wrong on our side. Try again in a moment.",
      conversation_id: conversationId, trace: [],
    }, 200, origin);
  }
});
