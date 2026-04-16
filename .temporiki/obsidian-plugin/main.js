"use strict";

const obsidian = require("obsidian");
const { execFile } = require("child_process");
const path = require("path");

const DEBOUNCE_MS = 2000;

function resolveUvPath() {
  return new Promise((resolve) => {
    if (process.platform === "win32") {
      resolve("uv");
      return;
    }
    execFile("/bin/bash", ["-lc", "command -v uv"], (err, stdout) => {
      if (err || !stdout) {
        resolve(null);
        return;
      }
      const resolved = stdout.toString().trim();
      resolve(resolved || null);
    });
  });
}

class TemporikiAutoIngestPlugin extends obsidian.Plugin {
  async onload() {
    this.debounceTimer = null;
    this.running = false;
    this.statusEl = this.addStatusBarItem();
    this.statusEl.setText("Temporiki: resolving uv...");

    this.uvPath = await resolveUvPath();
    if (!this.uvPath) {
      this.statusEl.setText("Temporiki: uv not found");
      console.error(
        "[temporiki-autoingest] `uv` not found in login shell PATH. " +
          "Install uv (https://docs.astral.sh/uv/) and restart Obsidian."
      );
      return;
    }
    this.statusEl.setText("Temporiki: idle");

    const handler = (file) => this.onVaultChange(file);
    this.registerEvent(this.app.vault.on("create", handler));
    this.registerEvent(this.app.vault.on("modify", handler));

    console.log("[temporiki-autoingest] loaded, uv=", this.uvPath);
  }

  onunload() {
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    console.log("[temporiki-autoingest] unloaded");
  }

  onVaultChange(file) {
    if (!this.uvPath) return;
    if (!file || !file.path) return;
    if (!file.path.startsWith("raw/")) return;
    const name = file.path.split("/").pop() || "";
    if (name.startsWith(".") || name.endsWith(".tmp")) return;

    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.statusEl.setText("Temporiki: pending...");
    this.debounceTimer = setTimeout(() => this.runIngest(), DEBOUNCE_MS);
  }

  runIngest() {
    if (this.running) {
      this.debounceTimer = setTimeout(() => this.runIngest(), DEBOUNCE_MS);
      return;
    }
    const adapter = this.app.vault.adapter;
    const basePath =
      typeof adapter.getBasePath === "function"
        ? adapter.getBasePath()
        : adapter.basePath;
    if (!basePath) {
      console.warn("[temporiki-autoingest] vault basePath unavailable");
      this.statusEl.setText("Temporiki: disabled (no basePath)");
      return;
    }
    const projectDir = path.join(basePath, ".temporiki");
    const args = [
      "--project",
      projectDir,
      "run",
      "temporiki",
      "palace-event",
      "--root",
      basePath,
    ];
    this.running = true;
    this.statusEl.setText("Temporiki: ingesting...");
    const started = Date.now();
    execFile(this.uvPath, args, { cwd: basePath }, (err, stdout, stderr) => {
      this.running = false;
      const ms = Date.now() - started;
      if (err) {
        console.error(
          "[temporiki-autoingest] error",
          err,
          stderr && stderr.toString()
        );
        this.statusEl.setText(`Temporiki: error (${ms}ms)`);
      } else {
        console.log(`[temporiki-autoingest] ok (${ms}ms)`);
        this.statusEl.setText(`Temporiki: ok (${ms}ms)`);
      }
    });
  }
}

module.exports = TemporikiAutoIngestPlugin;
