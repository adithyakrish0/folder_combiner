import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FolderCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Combiner")
        
        self.folder_path = ""
        self.selected_files = []
        
        # Create mode selection
        self.mode_var = tk.StringVar(value="folder")
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        
        tk.Radiobutton(mode_frame, text="Folder Mode", variable=self.mode_var, 
                      value="folder", command=self.update_ui).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Files Mode", variable=self.mode_var, 
                      value="files", command=self.update_ui).pack(side=tk.LEFT, padx=5)
        
        # Create buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.select_btn = tk.Button(btn_frame, text="Select Folder", command=self.select_folder)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.combine_btn = tk.Button(btn_frame, text="Combine Files", command=self.combine_files)
        self.combine_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.label = tk.Label(root, text="No selection made", fg="gray", wraplength=400)
        self.label.pack(padx=10, pady=10)
        
        # Listbox for selected files
        self.listbox = tk.Listbox(root, height=8, selectmode=tk.EXTENDED)
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.pack_forget()  # Hide initially
        
        self.update_ui()

    def update_ui(self):
        """Update UI elements based on selected mode"""
        if self.mode_var.get() == "folder":
            self.select_btn.config(text="Select Folder")
            self.listbox.pack_forget()
            if self.folder_path:
                self.label.config(text=self.folder_path)
            else:
                self.label.config(text="No folder selected")
        else:
            self.select_btn.config(text="Select Files")
            self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            if self.selected_files:
                self.label.config(text=f"{len(self.selected_files)} files selected")
            else:
                self.label.config(text="No files selected")

    def select_folder(self):
        if self.mode_var.get() == "folder":
            folder = filedialog.askdirectory(title="Select folder to combine")
            if folder:
                self.folder_path = folder
                self.selected_files = []  # Clear files selection
                self.label.config(text=folder)
                self.listbox.delete(0, tk.END)
        else:
            files = filedialog.askopenfilenames(title="Select files to combine")
            if files:
                self.selected_files = list(files)
                self.folder_path = ""  # Clear folder selection
                self.label.config(text=f"{len(self.selected_files)} files selected")
                self.listbox.delete(0, tk.END)
                for file in self.selected_files:
                    self.listbox.insert(tk.END, file)

    def build_folder_tree(self, root_folder):
        tree_lines = []
        prefix = ""

        def walk_dir(current_path, prefix=""):
            try:
                entries = sorted(os.listdir(current_path), key=lambda e: (not os.path.isdir(os.path.join(current_path, e)), e.lower()))
            except PermissionError:
                return
            for i, entry in enumerate(entries):
                path = os.path.join(current_path, entry)
                connector = "└── " if i == len(entries) -1 else "├── "
                tree_lines.append(f"{prefix}{connector}{entry}")
                if os.path.isdir(path):
                    extension = "    " if i == len(entries) -1 else "│   "
                    walk_dir(path, prefix + extension)

        tree_lines.append(os.path.basename(root_folder))
        walk_dir(root_folder)
        return "\n".join(tree_lines)

    def combine_files(self):
        if self.mode_var.get() == "folder" and not self.folder_path:
            messagebox.showwarning("No folder", "Please select a folder first!")
            return
        elif self.mode_var.get() == "files" and not self.selected_files:
            messagebox.showwarning("No files", "Please select files first!")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save combined file as"
        )
        if not output_file:
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                if self.mode_var.get() == "folder":
                    # Write folder tree first
                    folder_tree = self.build_folder_tree(self.folder_path)
                    outfile.write("Folder structure:\n")
                    outfile.write(folder_tree + "\n\n")

                    # Walk all files recursively
                    for root, dirs, files in os.walk(self.folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, self.folder_path)
                            outfile.write(rel_path + "\n")
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    outfile.write(f.read() + "\n\n")
                            except Exception as e:
                                outfile.write(f"[Error reading file: {e}]\n\n")
                else:
                    # Files mode
                    outfile.write("Selected files:\n")
                    for file in self.selected_files:
                        outfile.write(file + "\n")
                    outfile.write("\n")
                    
                    for file in self.selected_files:
                        outfile.write(f"=== {os.path.basename(file)} ===\n")
                        outfile.write(f"Path: {file}\n\n")
                        try:
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                outfile.write(f.read() + "\n\n")
                        except Exception as e:
                            outfile.write(f"[Error reading file: {e}]\n\n")

            messagebox.showinfo("Success", f"Files combined into:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to combine files:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderCombinerApp(root)
    root.mainloop()