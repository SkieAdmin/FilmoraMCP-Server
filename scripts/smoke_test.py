"""Read-only, real stdio MCP round-trip test against installed Filmora.

Does not modify the current project. Use --no-desktop to test protocol/catalog only.
"""
import argparse
import asyncio
import base64
import io
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image


async def run(no_desktop=False, visible=False):
    params = StdioServerParameters(command=sys.executable, args=["-m", "filmora_mcp.server"])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            assert len(tools.tools) >= 30
            assert len({t.name for t in tools.tools}) == len(tools.tools)
            caps = await session.call_tool("filmora_capabilities", {})
            assert not caps.isError, caps
            resources = await session.list_resources()
            assert len(resources.resources) == 2
            workflow = await session.read_resource("filmora://workflow")
            assert workflow.contents
            prompts = await session.list_prompts()
            assert prompts.prompts
            prompt = await session.get_prompt("edit_video", {"task": "Inspect editor without edits"})
            assert prompt.messages
            unknown = await session.call_tool("filmora_command", {"action": "not_a_command"})
            assert unknown.isError
            result = {"protocol": init.protocolVersion, "tool_count": len(tools.tools),
                      "resources": len(resources.resources), "prompts": len(prompts.prompts),
                      "unknown_command_error": True,
                      "tools": [t.name for t in tools.tools]}
            if not no_desktop:
                status = await session.call_tool("filmora_status", {})
                assert not status.isError, status
                status_data = json.loads(next(c.text for c in status.content if c.type == "text"))
                assert status_data["windows"], "Launch Filmora before desktop smoke test"
                # Read-only screenshot test: actual protocol ImageContent, not a base64 text blob.
                screenshot = await session.call_tool("filmora_screenshot", {"save": True, "max_width": 1200,
                                                                          "mode": "visible" if visible else "window"})
                assert not screenshot.isError, screenshot
                images = [c for c in screenshot.content if c.type == "image"]
                assert len(images) == 1 and images[0].mimeType == "image/png"
                im = Image.open(io.BytesIO(base64.b64decode(images[0].data)))
                assert im.width == 1200 and im.height > 100
                meta = json.loads(next(c.text for c in screenshot.content if c.type == "text"))
                inspected = await session.call_tool("filmora_inspect", {"max_depth": 25})
                assert not inspected.isError, inspected
                tree = json.loads(next(c.text for c in inspected.content if c.type == "text"))
                assert tree["elements"], "Expected accessible editor controls; screenshot-only layouts need manual validation"
                result.update({"desktop_screenshot": meta, "accessible_control_count": len(tree["elements"]),
                               "runtime_version": status_data["runtime_version"]})
            return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-desktop", action="store_true")
    parser.add_argument("--visible", action="store_true", help="Test visible-pixel capture; Filmora must already be foreground")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = asyncio.run(run(args.no_desktop, args.visible))
    encoded = json.dumps(result, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
