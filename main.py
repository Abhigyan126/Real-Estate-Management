import json
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, ttk
from PIL import Image, ImageTk

# Sample data structure
properties = []

# Original properties loaded from file
original_properties = []

# File to store properties
FILENAME = 'properties.json'

# Sorting variables
sort_column = None
sort_descending = False

# Function to add a new property
def add_property(property):
    properties.append(property)
    properties.sort(key=lambda x: x['name'].lower())  # Maintain sorted order for binary search
    save_to_file()
    update_table()

# Function to remove a property by name
def remove_property(property_name):
    global properties
    properties = [prop for prop in properties if prop['name'] != property_name]
    save_to_file()
    update_table()

# Function to update a property by name
def update_property(property_name, updated_property):
    for i, prop in enumerate(properties):
        if prop['name'] == property_name:
            properties[i].update(updated_property)
            save_to_file()
            update_table()
            break

# Binary search function to find a property by name
def binary_search(property_name):
    low, high = 0, len(properties) - 1
    while low <= high:
        mid = (low + high) // 2
        if properties[mid]['name'] == property_name:
            return mid, properties[mid]
        elif properties[mid]['name'] < property_name:
            low = mid + 1
        else:
            high = mid - 1
    return None, None

# Function to save properties to a file
def save_to_file():
    with open(FILENAME, 'w') as file:
        json.dump(properties, file)

# Function to read properties from a file
def read_from_file():
    global properties, original_properties
    try:
        with open(FILENAME, 'r') as file:
            properties = json.load(file)
            original_properties = properties[:]  # Create a copy of properties for resetting
    except FileNotFoundError:
        properties = []
        original_properties = []

# Function to reset properties to original state
def reset_properties():
    global properties
    properties = original_properties[:]
    update_table()

# Function to update the table with current properties data
def update_table():
    tree.delete(*tree.get_children())
    for prop in properties:
        tree.insert('', 'end', values=(prop['name'], prop['bedrooms'], prop['bathrooms'], prop['price']))

# Function to sort table by column
def sort_table(column):
    global sort_column, sort_descending
    if sort_column == column:
        sort_descending = not sort_descending
    else:
        sort_column = column
        sort_descending = False

    properties.sort(key=lambda x: x[column], reverse=sort_descending)
    update_table()

# Function to display the property form
def show_property_form(property=None, title="Add Property", callback=None):
    form = Toplevel(root)
    form.title(title)
    
    def on_submit():
        name = entry_name.get().strip()
        bedrooms = entry_bedrooms.get().strip()
        bathrooms = entry_bathrooms.get().strip()
        price = entry_price.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return
        
        try:
            bedrooms = int(bedrooms) if bedrooms else None
            bathrooms = int(bathrooms) if bathrooms else None
            price = float(price) if price else None
        except ValueError:
            messagebox.showwarning("Warning", "Bedrooms and bathrooms must be integers, and price must be a number.")
            return
        
        if callback:
            callback({
                'name': name,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'price': price
            })
        
        form.destroy()
        update_table()

    Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = Entry(form)
    entry_name.grid(row=0, column=1, padx=5, pady=5)
    
    Label(form, text="Bedrooms:").grid(row=1, column=0, padx=5, pady=5)
    entry_bedrooms = Entry(form)
    entry_bedrooms.grid(row=1, column=1, padx=5, pady=5)
    
    Label(form, text="Bathrooms:").grid(row=2, column=0, padx=5, pady=5)
    entry_bathrooms = Entry(form)
    entry_bathrooms.grid(row=2, column=1, padx=5, pady=5)
    
    Label(form, text="Price:").grid(row=3, column=0, padx=5, pady=5)
    entry_price = Entry(form)
    entry_price.grid(row=3, column=1, padx=5, pady=5)
    
    if property:
        entry_name.insert(0, property['name'])
        entry_bedrooms.insert(0, property.get('bedrooms', ''))
        entry_bathrooms.insert(0, property.get('bathrooms', ''))
        entry_price.insert(0, property.get('price', ''))
    
    Button(form, text="Submit", command=on_submit).grid(row=4, columnspan=2, pady=10)
    form.transient(root)
    form.grab_set()
    root.wait_window(form)

def add_property_gui():
    show_property_form(title="Add Property", callback=lambda property: add_property(property))

def remove_property_gui():
    selected = tree.selection()
    if selected:
        property_name = tree.item(selected[0])['values'][0]
        remove_property(property_name)
    else:
        messagebox.showwarning("Warning", "Select a property to remove.")
        
def update_property_gui():
    selected = tree.selection()
    if selected:
        property_name = tree.item(selected[0])['values'][0]
        _, property = binary_search(property_name)
        show_property_form(property=property, title="Update Property", callback=lambda updated_property: update_property(property_name, updated_property))
    else:
        messagebox.showwarning("Warning", "Select a property to update.")

def search_property_gui():
    form = Toplevel(root)
    form.title("Search Property")

    def on_submit():
        name = entry_name.get().strip()
        bedrooms = entry_bedrooms.get().strip()
        bathrooms = entry_bathrooms.get().strip()
        min_price = entry_min_price.get().strip()
        max_price = entry_max_price.get().strip()

        try:
            bedrooms = int(bedrooms) if bedrooms else None
            bathrooms = int(bathrooms) if bathrooms else None
            min_price = float(min_price) if min_price else None
            max_price = float(max_price) if max_price else None
        except ValueError:
            messagebox.showwarning("Warning", "Bedrooms and bathrooms must be integers, and price must be a number.")
            return

        filtered_properties = [prop for prop in properties if
                               (not name or prop['name'].lower() == name.lower()) and
                               (bedrooms is None or prop['bedrooms'] == bedrooms) and
                               (bathrooms is None or prop['bathrooms'] == bathrooms) and
                               (min_price is None or (prop['price'] is not None and prop['price'] >= min_price)) and
                               (max_price is None or (prop['price'] is not None and prop['price'] <= max_price))]

        if filtered_properties:
            tree.delete(*tree.get_children())
            for prop in filtered_properties:
                tree.insert('', 'end', values=(prop['name'], prop['bedrooms'], prop['bathrooms'], prop['price']))
            form.destroy()
        else:
            messagebox.showinfo("Search Result", "No properties found matching the criteria.")

    Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = Entry(form)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    Label(form, text="Bedrooms:").grid(row=1, column=0, padx=5, pady=5)
    entry_bedrooms = Entry(form)
    entry_bedrooms.grid(row=1, column=1, padx=5, pady=5)

    Label(form, text="Bathrooms:").grid(row=2, column=0, padx=5, pady=5)
    entry_bathrooms = Entry(form)
    entry_bathrooms.grid(row=2, column=1, padx=5, pady=5)

    Label(form, text="Min Price:").grid(row=3, column=0, padx=5, pady=5)
    entry_min_price = Entry(form)
    entry_min_price.grid(row=3, column=1, padx=5, pady=5)

    Label(form, text="Max Price:").grid(row=4, column=0, padx=5, pady=5)
    entry_max_price = Entry(form)
    entry_max_price.grid(row=4, column=1, padx=5, pady=5)

    Button(form, text="Submit", command=on_submit).grid(row=5, columnspan=2, pady=10)
    form.transient(root)
    form.grab_set()
    root.wait_window(form)

# Initialize main window
root = tk.Tk()
root.title("Real Estate Management System")

# Load icons for buttons and resize them
def load_icon(path, size=(16, 16)):
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.LANCZOS))

icon_add = load_icon("add_icon.png")
icon_remove = load_icon("remove_icon.png")
icon_update = load_icon("update_icon.png")
icon_search = load_icon("search_icon.png")
icon_reset = load_icon("reset_icon.png")
icon_save = load_icon("save_icon.png")

# Create a frame to hold buttons and treeview
frame_buttons = tk.Frame(root)
frame_buttons.pack(padx=10, pady=10)

# Add buttons with icons
btn_add = tk.Button(frame_buttons, text="Add Property", image=icon_add, compound=tk.LEFT, command=add_property_gui)
btn_add.grid(row=0, column=0, padx=5)

btn_remove = tk.Button(frame_buttons, text="Remove Property", image=icon_remove, compound=tk.LEFT, command=remove_property_gui)
btn_remove.grid(row=0, column=1, padx=5)

btn_update = tk.Button(frame_buttons, text="Update Property", image=icon_update, compound=tk.LEFT, command=update_property_gui)
btn_update.grid(row=0, column=2, padx=5)

btn_search = tk.Button(frame_buttons, text="Search Property", image=icon_search, compound=tk.LEFT, command=search_property_gui)
btn_search.grid(row=0, column=3, padx=5)

btn_reset = tk.Button(frame_buttons, text="Reset", image=icon_reset, compound=tk.LEFT, command=reset_properties)
btn_reset.grid(row=0, column=4, padx=5)

btn_save = tk.Button(frame_buttons, text="Save to File", image=icon_save, compound=tk.LEFT, command=save_to_file)
btn_save.grid(row=0, column=5, padx=5)

# Create treeview with columns
tree = ttk.Treeview(root, columns=('Name', 'Bedrooms', 'Bathrooms', 'Price'), show='headings')
tree.heading('Name', text='Name', command=lambda: sort_table('name'))
tree.heading('Bedrooms', text='Bedrooms', command=lambda: sort_table('bedrooms'))
tree.heading('Bathrooms', text='Bathrooms', command=lambda: sort_table('bathrooms'))
tree.heading('Price', text='Price', command=lambda: sort_table('price'))
tree.pack(padx=10, pady=10)

# Load initial data
read_from_file()
update_table()

# Run the GUI loop
root.mainloop()
