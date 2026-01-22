// selector/hybridSelector.ts

import { getModelStats } from "../db/modelStats";
import { getActorPreferences } from "../db/actorPreferences";
import { getRewriteConfig } from "../db/rewriteConfig";

export async function selectModel(ctx) {
  const rewrite = await getRewriteConfig();

  if (ctx.role === "rewriter") {
    return rewrite.pinned_model;
  }

  const prefs = await getActorPreferences(ctx.actor);
  const stats = await getModelStats(ctx.defaultModel, ctx.role);

  // Placeholder: combine rule-based + stats + prefs
  return ctx.defaultModel;
}