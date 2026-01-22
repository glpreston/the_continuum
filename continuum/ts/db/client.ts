// db/client.ts
// Thin wrapper around your MySQL connection

import mysql from "mysql2/promise";

export const db = mysql.createPool({
  host: "localhost",
  user: "root",
  password: "",
  database: "continuum"
});