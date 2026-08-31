"""Turn system-prompt.md into the SQL that updates the live chat's brain.

    py prototype/sales-agent/prompt_to_sql.py

Writes prompt.sql next to it. Chat_Agent then runs that file's contents through
the Supabase MCP `execute_sql` tool against project uvlkacfnbnsqpizktcfi, and
the deployed chat picks it up within a minute — no redeploy.

system-prompt.md stays the source of truth; the config row is only its deployed
copy. Never edit the row directly, or the two drift and git stops telling the
truth about how the chat behaves.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "system-prompt.md"), encoding="utf-8") as f:
    prompt = f.read()

# Dollar quoting: the prompt is full of apostrophes and quotes, and doubling
# them all is how a prompt silently gets corrupted on its way to production.
tag = "$prompt$"
if tag in prompt:
    raise SystemExit("system-prompt.md contains the dollar-quote tag " + tag + " - pick another tag")

sql = ("insert into public.config (key, value) values ('system_prompt', "
       + tag + prompt + tag + ")\n"
       "on conflict (key) do update set value = excluded.value, updated_at = now();\n")

out = os.path.join(HERE, "prompt.sql")
with open(out, "w", encoding="utf-8") as f:
    f.write(sql)

print("wrote " + out)
print("  prompt : " + str(len(prompt)) + " chars, " + str(prompt.count(chr(10)) + 1) + " lines")
