// db/rewriteConfig.ts

import { db } from "./client";
import { toPlain } from "./utils";

export interface RewriteConfig {
  id: number;
  pinned_model: string | null;
  forbidden_models: string | null;
  drift_guard_enabled: boolean;
  max_rewrite_depth: number;
}

export async function getRewriteConfig(): Promise<RewriteConfig | null> {
  const [rows] = await db.execute<any[]>(
    `SELECT * FROM rewrite_config LIMIT 1`
  );

  return rows.length > 0 ? toPlain<RewriteConfig>(rows[0]) : null;
}

export async function updateRewriteConfig(config: {
  pinned_model?: string;
  forbidden_models?: any;
  drift_guard_enabled?: boolean;
  max_rewrite_depth?: number;
}) {
  const existing = await getRewriteConfig();

  if (!existing) {
    await db.execute(
      `
      INSERT INTO rewrite_config (pinned_model, forbidden_models, drift_guard_enabled, max_rewrite_depth)
      VALUES (?, ?, ?, ?)
      `,
      [
        config.pinned_model ?? "qwen3:4b",
        JSON.stringify(config.forbidden_models ?? []),
        config.drift_guard_enabled ?? true,
        config.max_rewrite_depth ?? 1
      ]
    );
    return;
  }

  await db.execute(
    `
    UPDATE rewrite_config
    SET
      pinned_model = COALESCE(?, pinned_model),
      forbidden_models = COALESCE(?, forbidden_models),
      drift_guard_enabled = COALESCE(?, drift_guard_enabled),
      max_rewrite_depth = COALESCE(?, max_rewrite_depth)
    WHERE id = ?
    `,
    [
      config.pinned_model ?? null,
      config.forbidden_models ? JSON.stringify(config.forbidden_models) : null,
      config.drift_guard_enabled ?? null,
      config.max_rewrite_depth ?? null,
      existing.id
    ]
  );
}