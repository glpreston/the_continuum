// utils/types.ts

export interface ActorContext {
  actor: string;
  role: string;
  defaultModel: string;
  tags?: string[];
  complexity?: "low" | "medium" | "high";
}