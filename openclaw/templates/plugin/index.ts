import { OpenClawPluginApi } from "openclaw/plugin-sdk";

/**
 * OpenClaw App Example Plugin
 * 
 * This plugin demonstrates the basic structure of an OpenClaw plugin.
 * Uncomment and customize the sections you need.
 */

export default function register(api: OpenClawPluginApi) {
  console.log("OpenClaw App Example Plugin loaded!");
  
  // Example: Register a simple agent tool
  // api.registerTool({
  //   name: "example_tool",
  //   description: "An example tool that does something useful",
  //   parameters: {
  //     type: "object",
  //     properties: {
  //       input: { type: "string", description: "Input value" }
  //     }
  //   },
  //   execute: async ({ input }) => {
  //     // Your tool logic here
  //     return { result: `Processed: ${input}` };
  //   }
  // });

  // Example: Register a gateway RPC method
  // api.registerGatewayMethod("example.status", ({ respond }) => {
  //   respond(true, { ok: true, message: "Example plugin is running" });
  // });

  // Example: Register a channel plugin (for new messaging platform)
  // api.registerChannel({
  //   id: "example-chat",
  //   meta: {
  //     id: "example-chat",
  //     label: "Example Chat",
  //     selectionLabel: "Example Chat (API)",
  //     docsPath: "/plugins/example-chat",
  //     blurb: "Demo channel plugin for OpenClaw",
  //   },
  //   capabilities: { chatTypes: ["direct"] },
  //   config: {
  //     listAccountIds: (cfg) => Object.keys(cfg.channels?.examplechat?.accounts ?? {}),
  //     resolveAccount: (cfg, accountId) =>
  //       cfg.channels?.examplechat?.accounts?.[accountId ?? "default"] ?? { accountId },
  //   },
  //   outbound: {
  //     deliveryMode: "direct",
  //     sendText: async ({ text, to, channel }) => {
  //       // Implement message sending to your platform
  //       console.log(`Would send to ${to}: ${text}`);
  //       return { ok: true };
  //     },
  //   },
  // });

  // Example: Register background service
  // api.registerService({
  //   id: "example-service",
  //   start: () => console.log("Example service started"),
  //   stop: () => console.log("Example service stopped"),
  // });
}