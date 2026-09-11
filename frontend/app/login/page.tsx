import { readFileSync } from "fs";
import { join } from "path";
import { LoginForm } from "./LoginForm";

export default function LoginPage() {
  const svgPath = join(process.cwd(), "assets", "yaqeen-balance-background.svg");
  let svgDataUri = "";
  try {
    const svg = readFileSync(svgPath, "utf-8");
    svgDataUri = `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
  } catch {}

  return (
    <div className="h-dvh bg-teal relative flex items-center justify-center px-6 overflow-hidden">
      {svgDataUri && (
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url(${svgDataUri})`,
            backgroundPosition: "100% 100%",
            backgroundSize: "auto 100%",
            backgroundRepeat: "no-repeat",
          }}
        />
      )}
      <div className="absolute inset-0 bg-teal/60" />

      <LoginForm />
    </div>
  );
}
