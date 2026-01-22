// db/actorPreferences.ts

import { db } from "./client";

export async function getActorPreferences(actorName: string) {
  const [rows] = await db.execute(
    `SELECT * FROM actor_model_preferences WHERE actor_name = ?`,
    [actorName]
  );
  return rows;
}

export async function updateActorPreference(actorName: string, modelName: string, weight: number) {
  await db.execute(
    `
    INSERT INTO actor_model_preferences (actor_name, model_name, preference_weight)
    VALUES (?, ?, ?)
    ON DUPLICATE KEY UPDATE preference_weight = VALUES(preference_weight)
    `,
    [actorName, modelName, weight]
  );
}