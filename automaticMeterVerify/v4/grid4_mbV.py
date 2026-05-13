if __name__ == "__main__":
  root = tk.Tk()
  app = UltimateReviewer(root)
  root.bind("<Button-3>", lambda e: "break")
  root.mainloop()
