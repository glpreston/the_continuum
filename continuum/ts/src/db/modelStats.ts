// db/modelStats.ts

import { db } from "./client";
import { toPlain } from "./utils";

export interface ModelStats {
  model_name: string;
  actor_role: string | null;
  success_rate: number;
  avg_latency_ms: number;
  avg_cost_per_call: number;
  total_calls: number;
  total_failures: number;
  last_updated: string;
}

export async function getModelStats(
  modelName: string,
  actorRole: string | null = null
): Promise<ModelStats | null> {
  const [rows] = await db.execute<any[]>(
    `
    SELECT *
    FROM model_stats
    WHERE model_name = ?
      AND (actor_role = ? OR ? IS NULL)
    LIMIT 1
    `,
    [modelName, actorRole, actorRole]
  );

  return rows.length > 0 ? toPlain(rows[0]) : null;
}

export async function createModelStats(
  modelName: string,
  actorRole: string | null = null
): Promise<void> {
  await db.execute(
    `
    INSERT INTO model_stats (model_name, actor_role)
    VALUES (?, ?)
    `,
    [modelName, actorRole]
  );
}

export async function updateModelStats(
  modelName: string,
  actorRole: string | null,
  {
    success,
    latencyMs,
    costPerCall
  }: {
    success: boolean;
    latencyMs: number;
    costPerCall: number;
  }
): Promise<void> {
  const existing = await getModelStats(modelName, actorRole);
  if (!existing) {
    await createModelStats(modelName, actorRole);
  }

  await db.execute(
    `
    UPDATE model_stats
    SET
      total_calls = total_calls + 1,
      total_failures = total_failures + ?,
      avg_latency_ms =
        CASE
          WHEN total_calls = 0 THEN ?
          ELSE ((avg_latency_ms * total_calls) + ?) / (total_calls + 1)
        END,
      avg_cost_per_call =
        CASE
          WHEN total_calls = 0 THEN ?
          ELSE ((avg_cost_per_call * total_calls) + ?) / (total_calls + 1)
        END,
      success_rate =
        CASE
          WHEN total_calls = 0 THEN ?
          ELSE (total_calls - (total_failures + ?)) / (total_calls + 1)
        END
    WHERE model_name = ?
      AND (actor_role = ? OR ? IS NULL)
    `,
    [
      success ? 0 : 1,
      latencyMs,
      latencyMs,
      costPerCall,
      costPerCall,
      success ? 1 : 0,
      success ? 0 : 1,
      modelName,
      actorRole,
      actorRole
    ]
  );
}