// db/client.ts
// Thin wrapper around your MySQL connection

import mysql from "mysql2/promise";

export const db = mysql.createPool({
  host: "192.168.50.114",
  user: "hal",
  password: "Hal@2025!",
  database: "aira_config"
});