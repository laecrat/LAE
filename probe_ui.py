import main

lae = main.LAE()
app = main.LAEApp(lae)

def check():
    main.event_queue.put("show")
    app.root.after(800, inspect)

def inspect():
    w = app.win
    print("geo:", w.winfo_geometry(), "mapped:", w.winfo_ismapped())
    print("entry width:", app.entry.winfo_width(), "status font:", app.result_label.cget("font"))
    # simulate typing a command to see status rendering
    app.entry.insert(0, "search python")
    app.on_enter()
    app.root.after(1200, snap2)

def snap2():
    txt = app.result_label.cget("text")
    print("status text (ascii):", txt.encode("ascii", "replace").decode())
    print("status color:", app.result_label.cget("fg"))
    app.root.destroy()

app.root.after(600, check)
app.root.mainloop()
print("done")
