export type LogLevel = "debug" | "info" | "warn" | "error";

const LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const configuredLevel = process.env.NEXT_PUBLIC_LOG_LEVEL as LogLevel | undefined;
if (!configuredLevel || !(configuredLevel in LEVELS)) {
  throw new Error("NEXT_PUBLIC_LOG_LEVEL must be set to debug, info, warn, or error");
}
const currentLevel: LogLevel = configuredLevel;

let writeFn: (level: LogLevel, line: string) => void = () => {};

export function setLogWriter(fn: (level: LogLevel, line: string) => void): void {
  writeFn = fn;
}

function fmtTimestamp(): string {
  return new Date().toISOString();
}

function log(level: LogLevel, context: string, message: string, ...args: unknown[]): void {
  if (LEVELS[level] < LEVELS[currentLevel]) return;

  const ts = fmtTimestamp();
  const prefix = `[${ts}] [${level.toUpperCase()}] [server] [${context}]`;

  const extra =
    args.length > 0
      ? args
          .map((a) => {
            if (a instanceof Error) return `${a.name}: ${a.message}\n${a.stack ?? ""}`;
            try {
              return JSON.stringify(a, null, 2);
            } catch {
              return String(a);
            }
          })
          .join(" ")
      : "";

  const full = `${prefix} ${message} ${extra}`.trim();
  writeFn(level, full);
}

export const logger = {
  debug: (context: string, message: string, ...args: unknown[]) =>
    log("debug", context, message, ...args),
  info: (context: string, message: string, ...args: unknown[]) =>
    log("info", context, message, ...args),
  warn: (context: string, message: string, ...args: unknown[]) =>
    log("warn", context, message, ...args),
  error: (context: string, message: string, ...args: unknown[]) =>
    log("error", context, message, ...args),
};
