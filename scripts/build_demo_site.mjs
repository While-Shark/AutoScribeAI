import { cp, mkdir, rm } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const out = resolve(root, "demo-dist");
const demo = resolve(root, "demo");

const samples = ["uptime-kuma", "changedetection", "it-tools"];

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

for (const file of ["index.html", "styles.css", "app.js"]) {
  await cp(resolve(demo, file), resolve(out, file));
}

for (const sample of samples) {
  const source = resolve(root, "tests", "manual_samples", sample, "output");
  const target = resolve(out, "manuals", sample);
  await mkdir(target, { recursive: true });
  await cp(source, target, { recursive: true });
}

console.log("AutoScribeAI demo site assembled at", out);
