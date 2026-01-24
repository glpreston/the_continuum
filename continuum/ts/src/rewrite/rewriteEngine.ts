// rewrite/rewriteEngine.ts

import { getRewriteConfig } from "../db/rewriteConfig";

export async function rewriteText(input: string) {
  const cfg = await getRewriteConfig();
  // Placeholder: call pinned model
  return input;
}