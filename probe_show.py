import time
import main

lae = main.LAE()
app = main.LAEApp(lae)

def snap(tag):
    w = app.win
    print(tag,
          "geo=", w.winfo_geometry(),
          "mapped=", w.winfo_ismapped(),
          "shown=", getattr(app, "_shown", None),
          "focus=", w.focus_get())

app.root.after(600, lambda: (main.event_queue.put("show"), snap("t0")))
app.root.after(900, lambda: snap("t300"))
app.root.after(1400, lambda: snap("t800"))
app.root.after(2200, lambda: (snap("t1600"), app.root.destroy()))
app.root.mainloop()
print("done")
