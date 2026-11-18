from browser_controller import BrowserController

bc = BrowserController()
for b in ["xp", "xpl", "explorer", "files", "yt"]:
    site, base = bc.resolve_site("!" + b)
    print(f"!{b:10} -> site={site!r} base={base!r}")
print("search explorer demo:", bc.resolve_site("explorer"))
