import main
lae = main.LAE()
app = main.LAEApp(lae)

def check():
    app.win.update_idletasks()
    sw = app.win.winfo_screenwidth()
    sh = app.win.winfo_screenheight()
    print("screen:", sw, sh)
    app.show()
    app.win.update_idletasks()
    print("after show geometry:", app.win.geometry(), "x/y:", app.win.winfo_x(), app.win.winfo_y())
    print("_shown:", app._shown)
    app.root.destroy()

app.root.after(400, check)
app.root.mainloop()
print("done")
