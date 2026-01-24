// db/actorPreferences.ts

import { db } from "./client";
import { toPlain } from "./utils";

export async function getActorPreferences(actorName: string) {
  // Explicitly type rows as an array so .map() is valid
  const [rows] = await db.execute<any[]>(
    `SELECT * FROM actor_model_preferences WHERE actor_name = ?`,
    [actorName]
  );

  // Convert each RowDataPacket into a plain JSON object
  return rows.map(r => toPlain(r));
}

export async function updateActorPreference(
  actorName: string,
  modelName: string,
  weight: number
) {
  await db.execute(
    `
    INSERT INTO actor_model_preferences (actor_name, model_name, preference_weight)
    VALUES (?, ?, ?)
    ON DUPLICATE KEY UPDATE preference_weight = VALUES(preference_weight)
    `,
    [actorName, modelName, weight]
  );
}