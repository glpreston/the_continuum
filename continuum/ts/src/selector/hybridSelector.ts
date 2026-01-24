// selector/hybridSelector.ts

Weimport { db } from "../db/client";
import { getModelStats } from "../db/modelStats";
import { getActorPreferences } from "../db/actorPreferences";
import { getRewriteConfig } from "../db/rewriteConfig";
import { ActorContext } from "../utils/types";

export async function selectModel(ctx: ActorContext): Promise<string> {
  const rewrite = await getRewriteConfig();

  // Rewrite actor always uses pinned model
  if (ctx.role === "rewriter") {
    return rewrite?.pinned_model ?? ctx.defaultModel;
  }

  const prefs = await getActorPreferences(ctx.actor);
  const stats = await getModelStats(ctx.defaultModel, ctx.role);

  // Placeholder logic — will evolve later
  return ctx.defaultModel;
}

// Allow this file to be executed as a standalone script
if (require.main === module) {
  (async () => {
    // Read stdin FIRST
    const input = await new Promise<string>(resolve => {
      let data = "";
      process.stdin.on("data", chunk => (data += chunk));
      process.stdin.on("end", () => resolve(data));
    });

    if (!input.trim()) {
      console.error("No stdin payload received for selectModel");
      process.exitCode = 1;
      return;
    }

    const ctx = JSON.parse(input);

    // Only AFTER stdin is read do we call async DB functions
    try {
      const model = await selectModel({
        actor: ctx.actor,
        role: ctx.role,
        defaultModel: ctx.default_model,
        tags: ctx.tags,
        complexity: ctx.complexity
      });

      process.stdout.write(JSON.stringify({ model }));
    } finally {
      // Ensure the MySQL pool closes so the one-off script exits
      await db.end();
    }
  })();
}