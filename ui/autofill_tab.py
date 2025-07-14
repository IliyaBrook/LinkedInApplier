import json
import tkinter as tk
from tkinter import ttk, messagebox


class AutofillTab:
    def __init__(self, parent, autofill_file):
        self.frame = ttk.Frame(parent)
        self.autofill_file = autofill_file
        self.input_fields = {}
        self.radio_fields = {}
        self.dropdown_fields = {}
        self.autofill_sections = {}
        self.autofill_section_frames = {}
        self.autofill_section_states = {}
        self.dropdown_value_maps = {}
        self.section_buttons = {}
        self.setup_styles()
        self.create_widgets()
        self.load_autofill()

    # noinspection PyMethodMayBeStatic
    def setup_styles(self):
        """Setup custom styles for better UI"""
        style = ttk.Style()

        style.configure(
            "Section.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 8)
        )

        style.configure("Section.TFrame", relief="solid", borderwidth=1)

        style.configure("Content.TFrame", padding=10)

        style.configure("Delete.TButton", font=("Segoe UI", 8), foreground="red")

        style.configure("Save.TButton", font=("Segoe UI", 10, "bold"), padding=(20, 10))

    def create_widgets(self):
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = ttk.Label(
            header_frame, text="Autofill Configuration", font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Manage your form autofill settings",
            font=("Segoe UI", 9),
            foreground="gray",
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        sections_container = ttk.Frame(main_container)
        sections_container.pack(fill="both", expand=True)

        section_configs = [
            ("textInput", "📝 Text Input Fields", "Manage text input autofill values"),
            (
                "radioButtons",
                "🔘 Radio Button Groups",
                "Configure radio button selections",
            ),
            ("dropdowns", "📋 Dropdown Menus", "Set dropdown default values"),
        ]

        for i, (section_id, title, description) in enumerate(section_configs):
            self.create_section(sections_container, section_id, title, description)
            if i < len(section_configs) - 1:
                separator = ttk.Separator(sections_container, orient="horizontal")
                separator.pack(fill="x", pady=10)

        save_container = ttk.Frame(main_container)
        save_container.pack(fill="x", pady=(20, 0))

        save_button = ttk.Button(
            save_container,
            text="💾 Save Autofill Configuration",
            command=self.save_autofill,
            style="Save.TButton",
        )
        save_button.pack(side="right")

    def create_section(self, parent, section_id, title, description):
        section_frame = ttk.Frame(parent, style="Section.TFrame")
        section_frame.pack(fill="x", pady=5)

        header_frame = ttk.Frame(section_frame)
        header_frame.pack(fill="x", padx=5, pady=5)

        btn_text = (
            f"▼ {title}"
            if section_id in self.autofill_section_states
            and self.autofill_section_states[section_id]
            else f"▶ {title}"
        )
        toggle_btn = ttk.Button(
            header_frame,
            text=btn_text,
            command=lambda: self.toggle_section(section_id),
            style="Section.TButton",
        )
        toggle_btn.pack(side="left")

        desc_label = ttk.Label(
            header_frame, text=description, font=("Segoe UI", 9), foreground="gray"
        )
        desc_label.pack(side="left", padx=(15, 0))

        content_container = ttk.Frame(section_frame)

        canvas = tk.Canvas(
            content_container,
            height=300 if section_id == "textInput" else 200,
            highlightthickness=0,
            bg="white",
        )
        vsb = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        content_frame = ttk.Frame(canvas, style="Content.TFrame")

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)

        # noinspection PyUnusedLocal
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)

        def _on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)

        content_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # noinspection PyUnusedLocal
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # noinspection PyUnusedLocal
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        content_container.pack_forget()

        self.autofill_sections[section_id] = content_frame
        self.autofill_section_frames[section_id] = section_frame
        self.autofill_section_states[section_id] = False
        self.autofill_sections[section_id + "_container"] = content_container
        self.section_buttons[section_id] = toggle_btn

    def toggle_section(self, section_id):
        """Toggle section visibility with smooth animation"""
        state = self.autofill_section_states[section_id]
        container = self.autofill_sections[section_id + "_container"]
        button = self.section_buttons[section_id]

        if state:
            container.pack_forget()
            current_text = button.cget("text")
            new_text = current_text.replace("▼", "▶")
            button.configure(text=new_text)
        else:
            for other_id in self.autofill_section_states:
                if other_id == section_id or not isinstance(
                    self.autofill_section_states[other_id], bool
                ):
                    continue
                if self.autofill_section_states[other_id]:
                    other_container = self.autofill_sections[other_id + "_container"]
                    other_button = self.section_buttons[other_id]
                    other_container.pack_forget()
                    other_text = other_button.cget("text")
                    other_button.configure(text=other_text.replace("▼", "▶"))
                    self.autofill_section_states[other_id] = False
            container.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            current_text = button.cget("text")
            new_text = current_text.replace("▶", "▼")
            button.configure(text=new_text)

        self.autofill_section_states[section_id] = not state

    def create_text_input_item(self, parent, key, value):
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill="x", pady=5)

        label = ttk.Label(item_frame, text=key, font=("Segoe UI", 9, "bold"))
        label.pack(anchor="w")

        input_frame = ttk.Frame(item_frame)
        input_frame.pack(fill="x", pady=(5, 0))

        var = tk.StringVar(value=value)
        entry = ttk.Entry(input_frame, textvariable=var, width=40)
        entry.pack(side="left", fill="x", expand=True)

        del_btn = ttk.Button(
            input_frame,
            text="🗑 Delete",
            command=lambda: self.delete_textinput(key),
            style="Delete.TButton",
        )
        del_btn.pack(side="right", padx=(10, 0))

        self.input_fields[key] = var

    def create_radio_button_item(self, parent, rb_data):
        """Create a radio button group with improved layout"""
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill="x", pady=10)

        label_text = rb_data.get("placeholderIncludes", "")
        count = rb_data.get("count", None)
        if count is not None:
            label_text = f"{label_text} (count: {count})"

        header_frame = ttk.Frame(item_frame)
        header_frame.pack(fill="x")

        label = ttk.Label(header_frame, text=label_text, font=("Segoe UI", 9, "bold"))
        label.pack(side="left")

        del_btn = ttk.Button(
            header_frame,
            text="🗑 Delete",
            command=lambda: self.delete_radio(rb_data.get("placeholderIncludes", "")),
            style="Delete.TButton",
        )
        del_btn.pack(side="right")

        options_frame = ttk.Frame(item_frame)
        options_frame.pack(fill="x", pady=(10, 0), padx=20)

        var = tk.StringVar(value=rb_data.get("defaultValue", ""))
        self.radio_fields[rb_data.get("placeholderIncludes", "")] = var

        for opt in rb_data.get("options", []):
            radio_btn = ttk.Radiobutton(
                options_frame, text=opt["text"], value=opt["value"], variable=var
            )
            radio_btn.pack(anchor="w", pady=2)

    def create_dropdown_item(self, parent, dd_data):
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill="x", pady=10)

        label_text = dd_data.get("placeholderIncludes", "")
        count = dd_data.get("count", None)
        if count is not None:
            label_text = f"{label_text} (count: {count})"

        label = ttk.Label(item_frame, text=label_text, font=("Segoe UI", 9, "bold"))
        label.pack(anchor="w")

        dropdown_frame = ttk.Frame(item_frame)
        dropdown_frame.pack(fill="x", pady=(5, 0))

        var = tk.StringVar(value=dd_data.get("defaultValue", ""))
        self.dropdown_fields[dd_data.get("placeholderIncludes", "")] = var

        values = [opt["text"] for opt in dd_data.get("options", [])]
        value_map = {opt["text"]: opt["value"] for opt in dd_data.get("options", [])}

        combo = ttk.Combobox(
            dropdown_frame, textvariable=var, values=values, state="readonly", width=40
        )
        combo.pack(side="left", fill="x", expand=True)

        self.dropdown_value_maps[label_text] = value_map

        del_btn = ttk.Button(
            dropdown_frame,
            text="🗑 Delete",
            command=lambda: self.delete_dropdown(
                dd_data.get("placeholderIncludes", "")
            ),
            style="Delete.TButton",
        )
        del_btn.pack(side="right", padx=(10, 0))

    def load_autofill(self):
        """Load autofill data with improved UI creation"""
        for section in ["textInput", "radioButtons", "dropdowns"]:
            for widget in self.autofill_sections[section].winfo_children():
                widget.destroy()

        self.input_fields.clear()
        self.radio_fields.clear()
        self.dropdown_fields.clear()
        self.dropdown_value_maps.clear()

        try:
            with open(self.autofill_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key, value in data.get("textInput", {}).items():
                self.create_text_input_item(
                    self.autofill_sections["textInput"], key, value
                )

            for rb_data in data.get("radioButtons", []):
                self.create_radio_button_item(
                    self.autofill_sections["radioButtons"], rb_data
                )

            for dd_data in data.get("dropdowns", []):
                self.create_dropdown_item(self.autofill_sections["dropdowns"], dd_data)

        except Exception as e:
            print(f"Error loading autofill data: {e}")
            self.show_empty_state()

    def show_empty_state(self):
        for section_id in ["textInput", "radioButtons", "dropdowns"]:
            empty_frame = ttk.Frame(self.autofill_sections[section_id])
            empty_frame.pack(fill="both", expand=True, pady=20)

            empty_label = ttk.Label(
                empty_frame,
                text="No items configured yet",
                font=("Segoe UI", 10),
                foreground="gray",
            )
            empty_label.pack(anchor="center")

    def save_autofill(self):
        try:
            data = {
                "textInput": {k: v.get() for k, v in self.input_fields.items()},
                "radioButtons": [],
                "dropdowns": [],
            }

            for label, var in self.radio_fields.items():
                rb = None
                try:
                    with open(self.autofill_file, "r", encoding="utf-8") as f:
                        file_data = json.load(f)
                    for item in file_data.get("radioButtons", []):
                        if item.get("placeholderIncludes", "") == label:
                            rb = item
                            break
                except (
                    FileNotFoundError,
                    json.JSONDecodeError,
                    OSError,
                    PermissionError,
                ):
                    pass
                if rb:
                    rb["defaultValue"] = var.get()
                    data["radioButtons"].append(rb)

            for label, var in self.dropdown_fields.items():
                dd = None
                try:
                    with open(self.autofill_file, "r", encoding="utf-8") as f:
                        file_data = json.load(f)
                    for item in file_data.get("dropdowns", []):
                        if item.get("placeholderIncludes", "") == label:
                            dd = item
                            break
                except (
                    FileNotFoundError,
                    json.JSONDecodeError,
                    OSError,
                    PermissionError,
                ):
                    pass
                if dd:
                    dd["defaultValue"] = (
                        dd["options"][
                            [opt["text"] for opt in dd["options"]].index(var.get())
                        ]["value"]
                        if dd["options"]
                        and var.get() in [opt["text"] for opt in dd["options"]]
                        else var.get()
                    )
                    data["dropdowns"].append(dd)

            with open(self.autofill_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo(
                "✅ Success", "Autofill configuration saved successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "❌ Error", f"Failed to save autofill configuration:\n{str(e)}"
            )

    def delete_radio(self, label):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the radio button group '{label}'?",
        ):
            if label in self.radio_fields:
                del self.radio_fields[label]
            try:
                with open(self.autofill_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["radioButtons"] = [
                    rb
                    for rb in data.get("radioButtons", [])
                    if rb.get("placeholderIncludes", "") != label
                ]
                with open(self.autofill_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.load_autofill()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def delete_dropdown(self, label):
        if messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete the dropdown '{label}'?"
        ):
            if label in self.dropdown_fields:
                del self.dropdown_fields[label]
            try:
                with open(self.autofill_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["dropdowns"] = [
                    dd
                    for dd in data.get("dropdowns", [])
                    if dd.get("placeholderIncludes", "") != label
                ]
                with open(self.autofill_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.load_autofill()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def delete_textinput(self, label):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the text input '{label}'?",
        ):
            if label in self.input_fields:
                del self.input_fields[label]
            try:
                with open(self.autofill_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["textInput"].pop(label, None)
                with open(self.autofill_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.load_autofill()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
