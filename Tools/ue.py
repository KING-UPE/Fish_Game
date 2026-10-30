"""Run Python inside the Unreal editor through its MCP endpoint (execute_python_code).
Usage: python ue.py script.py   (or code on stdin)"""
import json, sys, urllib.request

URL = "http://127.0.0.1:18765/mcp"
HDR = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def post(payload, session=None):
    h = dict(HDR)
    if session:
        h["Mcp-Session-Id"] = session
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        sid = r.headers.get("Mcp-Session-Id") or session
        body = r.read().decode("utf-8", "replace")
    msgs = []
    for line in body.splitlines():
        if line.startswith("data:"):
            msgs.append(json.loads(line[5:].strip()))
    if not msgs and body.strip().startswith("{"):
        msgs.append(json.loads(body))
    return sid, msgs

def main():
    code = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    sid, _ = post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                              "clientInfo": {"name": "ue-cli", "version": "1"}}})
    try:
        post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    except Exception:
        pass
    _, msgs = post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": "execute_python_code", "arguments": {"code": code, "auto_save": False}}}, sid)
    for m in msgs:
        if "result" in m:
            for c in m["result"].get("content", []):
                if c.get("type") == "text":
                    t = c["text"]
                    try:
                        j = json.loads(t)
                        print(j.get("output", ""))
                        if not j.get("success", True):
                            print("FAILED:", j.get("error") or j)
                    except Exception:
                        print(t)
        elif "error" in m:
            print("ERROR:", m["error"])

main()
