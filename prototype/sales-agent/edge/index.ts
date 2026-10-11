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

// A rejected key is not a transient fault, so it gets its own type: telling a
// customer "try again in a moment" when the key is revoked sends them in a loop
// against something only Matan can fix.
class AuthError extends Error {}

async function callAnthropic(system: string, messages: Msg[]) {
  if (!ANTHROPIC_KEY) throw new AuthError("ANTHROPIC_API_KEY missing");
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({ model: MODEL, max_tokens: 1200, system, tools: TOOLS, messages }),
  });
  if (!r.ok) {
    const body = (await r.text()).slice(0, 400);
    if (r.status === 401 || r.status === 403) {
      authCache = { at: Date.now(), ok: false, detail: "anthropic " + r.status };
      throw new AuthError("anthropic " + r.status + ": " + body);
    }
    throw new Error("anthropic " + r.status + ": " + body);
  }
  return await r.json();
}

// The old health check reported `key: Boolean(ANTHROPIC_KEY)` — presence, not
// validity — so a revoked key read as healthy and the chat sat dead for eleven
// days with `ok: true`. This asks Anthropic whether the key still works, cached
// so a monitoring ping costs one token per instance per five minutes.
let authCache: { at: number; ok: boolean; detail: string } | null = null;
const AUTH_TTL_MS = 5 * 60_000;

async function authHealthy(force = false): Promise<{ ok: boolean; detail: string }> {
  if (!ANTHROPIC_KEY) return { ok: false, detail: "ANTHROPIC_API_KEY missing" };
  if (!force && authCache && Date.now() - authCache.at < AUTH_TTL_MS) {
    return { ok: authCache.ok, detail: authCache.detail };
  }
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1,
        messages: [{ role: "user", content: "." }],
      }),
    });
    // 400 means the key authenticated and the request itself was rejected —
    // that is still a healthy key, so only 401/403 count as a failure.
    const ok = r.ok || r.status === 400;
    const detail = ok ? "ok" : "anthropic " + r.status;
    authCache = { at: Date.now(), ok, detail };
    return { ok, detail };
  } catch (e) {
    const detail = "unreachable: " + String(e).slice(0, 120);
    authCache = { at: Date.now(), ok: false, detail };
    return { ok: false, detail };
  }
}

// ------------------------------------------------- degraded mode (no model)

// When Anthropic will not answer, the chat does not have to be dead. This is a
// deliberately dumb search assistant: it reads a budget, a grade and any card
// name out of the message, runs the same catalog search the model would have
// called, and prints real rows. It invents nothing — every line comes from the
// products table — and it says plainly that the smart assistant is out, so a
// customer is never misled about what is answering them.
//
// It still feeds the demand loop: searchCatalog logs the miss, and a named card
// we do not stock is written to the wishlist exactly as the model would have.

// Catalog titles are English, so a Hebrew card name finds nothing without this.
const HE_NAMES: Array<[RegExp, string]> = [
  [/פיקאצ['׳]?ו/, "pikachu"],
  [/צ['׳]ארי?זארד|צ['׳]ריזארד/, "charizard"],
  [/מיוטו|מיו-?טו/, "mewtwo"],
  [/\bמיו\b/, "mew"],
  [/איווי|אייווי/, "eevee"],
  [/אמבריון|אמברון/, "umbreon"],
  [/סילביון/, "sylveon"],
  [/לוגיה/, "lugia"],
  [/רייקוואזה|רייקוזה/, "rayquaza"],
  [/גיאראדוס|גיירדוס/, "gyarados"],
  [/סנורלקס|סניורלקס/, "snorlax"],
  [/דרגונייט/, "dragonite"],
  [/בלסטויז/, "blastoise"],
  [/ונוסאור|ויננוסאור/, "venusaur"],
  [/גנגר/, "gengar"],
  [/טיראניטר/, "tyranitar"],
  [/לוקריו/, "lucario"],
  [/גרניה/, "greninja"],
];

// Words that match half the catalog and so only blur the search.
const STOP = new Set([
  "psa", "cgc", "bgs", "raw", "the", "and", "for", "you", "have", "any", "all",
  "ils", "nis", "card", "cards", "slab", "slabs", "pokemon", "pokémon", "shekel",
  "please", "want", "looking", "need", "some", "something", "with", "under",
]);

function parseBudget(m: string): { min?: number; max?: number } {
  const range = /(\d{2,5})\s*(?:-|–|עד|to)\s*(\d{2,5})/.exec(m);
  if (range) {
    const a = Number(range[1]), b = Number(range[2]);
    return { min: Math.min(a, b), max: Math.max(a, b) };
  }
  const cap = /(?:עד|מתחת\s*ל?|under|below|max)\s*(\d{2,5})/i.exec(m);
  if (cap) return { max: Number(cap[1]) };
  const floor = /(?:מעל|מ-?\s*|above|over|from)\s*(\d{2,5})\s*(?:\+|ומעלה)/i.exec(m);
  if (floor) return { min: Number(floor[1]) };
  return {};
}

function parseGrade(m: string): string | undefined {
  const g = /\b(PSA|CGC|BGS)\s*(10|[1-9])\b/i.exec(m);
  if (g) return g[1].toUpperCase() + " " + g[2];
  if (/\braw\b|גולמי|לא\s*מדורג/i.test(m)) return "RAW";
  return undefined;
}

function parseTerms(m: string): string {
  const out = new Set<string>();
  for (const [re, en] of HE_NAMES) if (re.test(m)) out.add(en);
  for (const w of m.match(/[a-zA-Z]{3,}/g) ?? []) {
    const lw = w.toLowerCase();
    if (!STOP.has(lw)) out.add(lw);
  }
  return [...out].join(" ");
}

const FALLBACK_HEAD =
  "העוזר החכם שלנו בתחזוקה קצרה, אז אני עונה כאן בחיפוש ישיר במלאי.";
const FALLBACK_FOOT =
  "לכל שאלה אחרת אפשר לכתוב למתן דרך עמוד צור קשר ונחזור אליכם.";

const FALLBACK_ASK = "לא הצלחתי לזהות מה לחפש. אפשר לכתוב שם קלף באנגלית, " +
  "דירוג (למשל PSA 9) או תקציב (למשל \"עד 300\").";

async function fallbackReply(message: string, conversationId: string): Promise<string> {
  const budget = parseBudget(message);
  const grade = parseGrade(message);
  const query = parseTerms(message);

  // "היי" carries no filter at all. Without this the search matches the whole
  // catalog and the customer gets five expensive cards they never asked about.
  if (!query && !grade && budget.min == null && budget.max == null) {
    return FALLBACK_HEAD + "\n\n" + FALLBACK_ASK + "\n\n" + FALLBACK_FOOT;
  }

  const res = await searchCatalog({
    query, grade, min_price: budget.min, max_price: budget.max, limit: 12,
  }, conversationId) as {
    products: Array<
      { title: string; price_ils: number | null; in_stock: number; url: string | null }
    >;
  };

  // searchCatalog scores a description hit the same as a title hit, which is
  // right for the model (it reads the rows and judges) and wrong here (nothing
  // judges). "charizard base set" matched a Jigglypuff on the word "set". With
  // no model in the loop, a named card must appear in the title or not at all.
  const terms = query.split(" ").filter(Boolean);
  const products = terms.length
    ? res.products.filter((p) =>
      terms.some((t) => p.title.toLowerCase().includes(t))
    ).slice(0, 5)
    : res.products.slice(0, 5);

  if (!products.length) {
    if (query) {
      await recordWishlist({
        card: query + (grade ? " " + grade : ""),
        notes: "Logged by the fallback assistant while the model was unavailable.",
      }, conversationId);
      return FALLBACK_HEAD + "\n\nלא מצאתי התאמה במלאי כרגע. רשמתי את הבקשה " +
        "אצל מתן לסבב הרכש הקרוב.\n\n" + FALLBACK_FOOT;
    }
    return FALLBACK_HEAD + "\n\nלא מצאתי התאמה לחיפוש הזה במלאי.\n\n" + FALLBACK_ASK +
      "\n\n" + FALLBACK_FOOT;
  }

  const lines = products.map((p) => {
    const row = "• " + p.title + (p.price_ils != null ? " — ₪" + p.price_ils : "");
    return p.url ? row + "\n  " + p.url : row;
  });
  return FALLBACK_HEAD + "\n\nהנה מה שיש לנו במלאי שמתאים:\n" + lines.join("\n") +
    "\n\n" + FALLBACK_FOOT;
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
  return { reply: "סליחה, נתקעתי כאן. אפשר לנסח את זה אחרת?", messages, trace };
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
    const auth = await authHealthy(url.searchParams.get("fresh") === "1");
    const ok = auth.ok && products.length > 0;
    return json({
      ok,
      model: MODEL,
      key: Boolean(ANTHROPIC_KEY),
      auth: auth.detail,
      products: products.length,
      in_stock: products.filter((p) => p.inventory > 0).length,
    }, ok ? 200 : 503, origin);
  }

  if (req.method !== "POST") return json({ error: "not found" }, 404, origin);

  // A missing key is handled the same way a rejected one is — callAnthropic
  // raises AuthError and the request falls through to the catalog fallback,
  // so there is one degraded path rather than two.

  const ipHash = await hashIp(req);
  if (await overRateLimit(ipHash)) {
    return json({
      reply: "שלחת הרבה הודעות בזמן קצר. תן לזה כמה דקות ונסה שוב.",
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
    return json({ reply: "ההודעה קצת ארוכה מדי לצ'אט — אפשר לקצר?", trace: [] }, 200, origin);
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
      reply: "השיחה כבר ארוכה. רענן את העמוד כדי להתחיל שיחה חדשה ונמשיך מכאן.",
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
    if (e instanceof AuthError) {
      // Nobody noticed the last outage because a dead chat left no trace Matan
      // reads. One handoff row per conversation is that trace — on the opening
      // turn only, so a long conversation does not flood his queue.
      if (turns === 0) {
        await supabase.from("handoffs").insert({
          reason: "chat_down",
          summary: "המודל לא זמין (" + String(e).slice(0, 120) +
            "). הצ'אט עונה במצב חיפוש־מלאי מצומצם.",
          contact: null,
          conversation_id: conversationId,
        }).then(() => {}, () => {});
      }
      // Degraded, but still selling: real stock, real prices, real links.
      let reply = "הצ'אט לא זמין כרגע ואנחנו כבר על זה. אפשר לכתוב למתן ישירות " +
        "דרך עמוד צור קשר ונחזור אליכם.";
      try {
        reply = await fallbackReply(message, conversationId);
      } catch (inner) {
        console.error("fallback failed", inner);
      }
      try {
        await supabase.from("conversations").update({
          turns: turns + 1, updated_at: new Date().toISOString(),
        }).eq("id", conversationId);
      } catch { /* the reply matters more than the counter */ }
      return json({
        reply, conversation_id: conversationId, trace: [], degraded: true,
      }, 200, origin);
    }
    return json({
      reply: "משהו השתבש אצלנו. נסו שוב עוד רגע.",
      conversation_id: conversationId, trace: [],
    }, 200, origin);
  }
});
