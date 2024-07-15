import os
import tkinter as tk
from tkinter import filedialog, messagebox, Label, Entry, Button, Checkbutton, Radiobutton, BooleanVar
from bffnt import Bffnt  # Assuming Bffnt class is defined in bffnt.py
import png  # Import pypng for handling PNG

class BffntConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("iomkrBFFNT")
       
        self.create_widgets()

    def create_widgets(self):
        # File selection
        Label(self.root, text="BFFNT File:").grid(row=0, column=0, padx=10, pady=5)
        self.file_entry = Entry(self.root, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=5)
        Button(self.root, text="Browse", command=self.select_file).grid(row=0, column=2, padx=10, pady=5)

        # Options
        self.verbose_var = BooleanVar()
        Checkbutton(self.root, text="Verbose", variable=self.verbose_var).grid(row=1, column=0, padx=10, pady=5)

        self.debug_var = BooleanVar()
        Checkbutton(self.root, text="Debug", variable=self.debug_var).grid(row=1, column=1, padx=10, pady=5)

        self.yes_var = BooleanVar()
        Checkbutton(self.root, text="Yes to all prompts", variable=self.yes_var).grid(row=1, column=2, padx=10, pady=5)

        self.ensure_ascii_var = BooleanVar(value=True)
        Checkbutton(self.root, text="Ensure ASCII in JSON", variable=self.ensure_ascii_var).grid(row=2, column=0, padx=10, pady=5)

        self.big_endian_var = BooleanVar()
        Radiobutton(self.root, text="Little Endian", variable=self.big_endian_var, value=False).grid(row=2, column=1, padx=10, pady=5)
        Radiobutton(self.root, text="Big Endian", variable=self.big_endian_var, value=True).grid(row=2, column=2, padx=10, pady=5)

        self.extract_var = BooleanVar()
        self.create_var = BooleanVar()
        Radiobutton(self.root, text="Extract", variable=self.extract_var, value=True).grid(row=3, column=0, padx=10, pady=5)
        Radiobutton(self.root, text="Create", variable=self.create_var, value=True).grid(row=3, column=1, padx=10, pady=5)

        Button(self.root, text="Run", command=self.run).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("BFFNT Files", "*.bffnt"), ("All Files", "*.*")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def run(self):
        filename = self.file_entry.get()
        if not os.path.exists(filename):
            messagebox.showerror("Error", "File not found")
            return

        basename = os.path.splitext(os.path.basename(filename))[0]
        json_file = '%s_manifest.json' % basename

        if self.extract_var.get() and os.path.exists(json_file) and not self.yes_var.get():
            if not messagebox.askyesno("Overwrite", "JSON output file exists. Overwrite?"):
                return

        sheet_file = '%s_sheet0.png' % basename

        if self.extract_var.get() and os.path.exists(sheet_file) and not self.yes_var.get():
            if not messagebox.askyesno("Overwrite", "At least one sheet PNG file exists. Overwrite?"):
                return

        if self.create_var.get() and os.path.exists(filename) and not self.yes_var.get():
            if not messagebox.askyesno("Overwrite", "BFFNT output file exists. Overwrite?"):
                return

        order = '>' if self.big_endian_var.get() else '<'
        bffnt = Bffnt()  # No arguments

        # Set attributes directly if needed
        bffnt.load_order = order
        bffnt.verbose = self.verbose_var.get()
        bffnt.debug = self.debug_var.get()

        if self.extract_var.get():
            bffnt.read(filename)
            if not bffnt.invalid:
                bffnt.extract(self.ensure_ascii_var.get())
                # Example assuming bffnt has a method for exporting PNG
                for i, image_data in enumerate(bffnt.images):
                    if image_data.data:
                        try:
                            with open(f"{basename}_sheet{i}.png", 'wb') as f:
                                writer = png.Writer(width=image_data.width, height=image_data.height, alpha=True)
                                writer.write_array(f, image_data.data)
                            messagebox.showinfo("Export", f"Exported {basename}_sheet{i}.png")
                        except Exception as e:
                            messagebox.showerror("Error", f"Error exporting PNG: {e}")
                    else:
                        messagebox.showwarning("Warning", f"No data found for {basename}_sheet{i}.png")
        elif self.create_var.get():
            bffnt.load(json_file)
            if not bffnt.invalid:
                bffnt.save(filename)

if __name__ == '__main__':
    root = tk.Tk()
    app = BffntConverterApp(root)
    root.mainloop()