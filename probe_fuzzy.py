from app_controller import AppController

ac = AppController()
ac._app_cache = [
    ('WhatsApp', 'uwp', 'AppID1'),
    ('Intel Graphics Command Center', 'lnk', 'C:/x.lnk'),
    ('cmd', 'exe', 'cmd.exe'),
    ('GitHub Desktop', 'lnk', 'C:/gh.lnk'),
    ('Notepad', 'exe', 'notepad.exe'),
]

tests = ['whatapp', 'whatappppp', 'whatsap', 'intel graphics', 'cmd', 'git', 'note', 'xyz']
for q in tests:
    r = ac.find_app(q)
    print(f"{q!r:18} -> {r[0] if r else None}")
