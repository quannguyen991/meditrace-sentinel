/**
 * Nạp biến môi trường từ `.env.local` và `.env` TRƯỚC mọi module khác.
 * Module này phải được import ở dòng đầu tiên của `web/server.ts`.
 */
import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: ".env.local", quiet: true });
dotenv.config({ quiet: true });
dotenv.config({ path: path.resolve(process.cwd(), "..", ".env.local"), quiet: true });
dotenv.config({ path: path.resolve(process.cwd(), "..", ".env"), quiet: true });
