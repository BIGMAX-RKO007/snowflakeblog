import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("data/box_openapi_full.json", "r", encoding="utf-8") as f:
    spec = json.load(f)

# Helper to find operations for given tags
def get_ops_for_tags(tags):
    ops_by_tag = {t: [] for t in tags}
    for path, methods in spec["paths"].items():
        for m, op in methods.items():
            if not isinstance(op, dict):
                continue
            op_tags = [t.lower() for t in op.get("tags", [])]
            for t in tags:
                if t.lower() in op_tags:
                    # Parse params
                    params = []
                    for p in op.get("parameters", []):
                        p_in = p.get("in", "")
                        p_name = p.get("name", "")
                        p_req = p.get("required", False)
                        p_schema = p.get("schema", {})
                        p_type = p_schema.get("type", "string")
                        p_desc = p.get("description", "")
                        params.append({"in": p_in, "name": p_name, "required": p_req, "type": p_type, "desc": p_desc})
                    
                    # Parse body
                    body_props = []
                    req_body = op.get("requestBody", {})
                    content = req_body.get("content", {})
                    json_c = content.get("application/json") or content.get("application/x-www-form-urlencoded") or content.get("multipart/form-data")
                    if json_c:
                        schema = json_c.get("schema", {})
                        props = schema.get("properties", {})
                        req_fields = schema.get("required", [])
                        for pn, pv in props.items():
                            body_props.append({
                                "name": pn,
                                "type": pv.get("type", "object"),
                                "required": pn in req_fields,
                                "desc": pv.get("description", "")[:120]
                            })
                    
                    ops_by_tag[t].append({
                        "method": m.upper(),
                        "path": path,
                        "summary": op.get("summary", ""),
                        "description": op.get("description", ""),
                        "params": params,
                        "body": body_props
                    })
    return ops_by_tag

print("Script framework ready.")
