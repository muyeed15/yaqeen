import { spawn } from "child_process";
import { loadEnv, requiredEnv } from "./env.mjs";

const env = loadEnv(".env");
const port = requiredEnv(env, "PORT");
const host = requiredEnv(env, "HOST");

const args = ["next", "dev", "-p", port];
if (host) args.push("-H", host);

const child = spawn("npx", args, { stdio: "inherit", shell: process.platform === "win32" });
child.on("exit", (code) => process.exit(code ?? 0));
