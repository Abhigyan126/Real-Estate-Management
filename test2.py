import json
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, ttk
from PIL import Image, ImageTk
import joblib  # Assuming your prediction model is saved using joblib

# Sample data structure
properties = []

# Original properties loaded from file
original_properties = []

# File to store properties
FILENAME = 'properties.json'

# Sorting variables
sort_column = None
sort_descending = False

# Load the prediction model
lr_clf_loaded = joblib.load('linear_regression_model.pkl')  # Update with your actual model file

# Function to predict price
def predict_price(total_sqft, bath, bhk):
    if lr_clf_loaded:
        try:
            total_sqft = float(total_sqft)
            bath = float(bath)
            bhk = int(bhk)
            price_prediction = lr_clf_loaded.predict([[total_sqft, bath, bhk]])
            return round(price_prediction[0], 2)  # Return rounded prediction
        except ValueError:
            messagebox.showwarning("Warning", "Total Sqft, Bath, and BHK must be numeric values.")
    else:
        messagebox.showwarning("Warning", "Prediction model not found or loaded.")

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
        tree.insert('', 'end', values=(prop['name'], prop['total_sqft'], prop['bath'], prop['price'], prop['bhk']))

sort_directions = {
    'name': '',
    'total_sqft': '',
    'bath': '',
    'price': '',
    'bhk': ''
}

def sort_table(column):
    global sort_column, sort_descending
    if sort_column == column:
        sort_descending = not sort_descending
    else:
        sort_column = column
        sort_descending = False

    properties.sort(key=lambda x: x[column], reverse=sort_descending)
    update_table()
    
    for col in sort_directions:
        sort_directions[col] = ''
    
    sort_directions[column] = ' ↓' if sort_descending else ' ↑'

    tree.heading('Name', text='Name' + sort_directions['name'], command=lambda: sort_table('name'))
    tree.heading('Total Sqft', text='Total Sqft' + sort_directions['total_sqft'], command=lambda: sort_table('total_sqft'))
    tree.heading('Bath', text='Bath' + sort_directions['bath'], command=lambda: sort_table('bath'))
    tree.heading('Price', text='Price' + sort_directions['price'], command=lambda: sort_table('price'))
    tree.heading('BHK', text='BHK' + sort_directions['bhk'], command=lambda: sort_table('bhk'))

# Function to display the property form
def show_property_form(property=None, title="Add Property", callback=None):
    form = Toplevel(root)
    form.title(title)
    
    def on_submit():
        name = entry_name.get().strip()
        total_sqft = entry_total_sqft.get().strip()
        bath = entry_bath.get().strip()
        price = entry_price.get().strip()
        bhk = entry_bhk.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return
        
        try:
            total_sqft = float(total_sqft) if total_sqft else None
            bath = float(bath) if bath else None
            price = float(price) if price else None
            bhk = int(bhk) if bhk else None
        except ValueError:
            messagebox.showwarning("Warning", "Total Sqft, Bath, and Price must be numbers, and BHK must be an integer.")
            return
        
        # Predict price
        predicted_price = predict_price(total_sqft, bath, bhk)
        if predicted_price is not None:
            price = predicted_price  # Update price with predicted value
        
        if callback:
            callback({
                'name': name,
                'total_sqft': total_sqft,
                'bath': bath,
                'price': price,
                'bhk': bhk
            })
        
        form.destroy()
        update_table()

    Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = Entry(form)
    entry_name.grid(row=0, column=1, padx=5, pady=5)
    
    Label(form, text="Total Sqft:").grid(row=1, column=0, padx=5, pady=5)
    entry_total_sqft = Entry(form)
    entry_total_sqft.grid(row=1, column=1, padx=5, pady=5)
    
    Label(form, text="Bath:").grid(row=2, column=0, padx=5, pady=5)
    entry_bath = Entry(form)
    entry_bath.grid(row=2, column=1, padx=5, pady=5)
    
    Label(form, text="Price:").grid(row=3, column=0, padx=5, pady=5)
    entry_price = Entry(form)
    entry_price.grid(row=3, column=1, padx=5, pady=5)
    
    Label(form, text="BHK:").grid(row=4, column=0, padx=5, pady=5)
    entry_bhk = Entry(form)
    entry_bhk.grid(row=4, column=1, padx=5, pady=5)
    
    if property:
        entry_name.insert(0, property['name'])
        entry_total_sqft.insert(0, property.get('total_sqft', ''))
        entry_bath.insert(0, property.get('bath', ''))
        entry_price.insert(0, property.get('price', ''))
        entry_bhk.insert(0, property.get('bhk', ''))
    
    Button(form, text="Submit", command=on_submit).grid(row=5, columnspan=2, pady=10)
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
        total_sqft = entry_total_sqft.get().strip()
        bath = entry_bath.get().strip()
        min_price = entry_min_price.get().strip()
        max_price = entry_max_price.get().strip()
        bhk = entry_bhk.get().strip()

        try:
            total_sqft = float(total_sqft) if total_sqft else None
            bath = float(bath) if bath else None
            min_price = float(min_price) if min_price else None
            max_price = float(max_price) if max_price else None
            bhk = int(bhk) if bhk else None
        except ValueError:
            messagebox.showwarning("Warning", "Total Sqft, Bath, and Price must be numbers, and BHK must be an integer.")
            return

        filtered_properties = [prop for prop in properties if
                               (not name or prop['name'].lower() == name.lower()) and
                               (total_sqft is None or (prop['total_sqft'] is not None and prop['total_sqft'] == total_sqft)) and
                               (bath is None or (prop['bath'] is not None and prop['bath'] == bath)) and
                               (min_price is None or (prop['price'] is not None and prop['price'] >= min_price)) and
                               (max_price is None or (prop['price'] is not None and prop['price'] <= max_price)) and
                               (bhk is None or (prop['bhk'] is not None and prop['bhk'] == bhk))]

        if filtered_properties:
            tree.delete(*tree.get_children())
            for prop in filtered_properties:
                tree.insert('', 'end', values=(prop['name'], prop['total_sqft'], prop['bath'], prop['price'], prop['bhk']))
            form.destroy()
        else:
            messagebox.showinfo("Search Result", "No properties found matching the criteria.")

    Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    entry_name = Entry(form)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    Label(form, text="Total Sqft:").grid(row=1, column=0, padx=5, pady=5)
    entry_total_sqft = Entry(form)
    entry_total_sqft.grid(row=1, column=1, padx=5, pady=5)

    Label(form, text="Bath:").grid(row=2, column=0, padx=5, pady=5)
    entry_bath = Entry(form)
    entry_bath.grid(row=2, column=1, padx=5, pady=5)

    Label(form, text="Min Price:").grid(row=3, column=0, padx=5, pady=5)
    entry_min_price = Entry(form)
    entry_min_price.grid(row=3, column=1, padx=5, pady=5)

    Label(form, text="Max Price:").grid(row=4, column=0, padx=5, pady=5)
    entry_max_price = Entry(form)
    entry_max_price.grid(row=4, column=1, padx=5, pady=5)

    Label(form, text="BHK:").grid(row=5, column=0, padx=5, pady=5)
    entry_bhk = Entry(form)
    entry_bhk.grid(row=5, column=1, padx=5, pady=5)

    Button(form, text="Submit", command=on_submit).grid(row=6, columnspan=2, pady=10)
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
tree = ttk.Treeview(root, columns=('Name', 'Total Sqft', 'Bath', 'Price', 'BHK'), show='headings')
tree.heading('Name', text='Name', command=lambda: sort_table('name'))
tree.heading('Total Sqft', text='Total Sqft', command=lambda: sort_table('total_sqft'))
tree.heading('Bath', text='Bath', command=lambda: sort_table('bath'))
tree.heading('Price', text='Price', command=lambda: sort_table('price'))
tree.heading('BHK', text='BHK', command=lambda: sort_table('bhk'))
tree.pack(padx=10, pady=10)

# Load initial data
read_from_file()
update_table()

# Run the GUI loop
root.mainloop()
