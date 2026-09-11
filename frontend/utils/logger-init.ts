import { appendFileSync, existsSync, mkdirSync, renameSync, statSync } from "fs";
import { join } from "path";
import { setLogWriter, type LogLevel } from "./logger";

const MAX_BYTES = 10 * 1024 * 1024;

const logDir = join(process.cwd(), "logs");
if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });

function rotate(fp: string): void {
  if (!existsSync(fp)) return;
  try {
    if (statSync(fp).size >= MAX_BYTES) {
      renameSync(fp, `${fp}.1`);
    }
  } catch {}
}

setLogWriter((level: LogLevel, line: string): void => {
  const file = level === "error" ? "error.log" : "app.log";
  const fp = join(logDir, file);
  rotate(fp);
  try {
    appendFileSync(fp, line + "\n", "utf-8");
  } catch {
    const fn = level === "error" ? console.error : level === "warn" ? console.warn : console.log;
    fn(line);
  }
});
