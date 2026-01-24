export function toPlain<T>(row: any): T {
  return JSON.parse(JSON.stringify(row));
}