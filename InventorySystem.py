import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# File paths
PRODUCT_LIST_PATH = "C:/Users/rauna/Downloads/Updated_Fancy_Product_List.csv"
BILLS_FOLDER = "Bills"

if not os.path.exists(BILLS_FOLDER):
    os.makedirs(BILLS_FOLDER)

# Load inventory
if os.path.exists(PRODUCT_LIST_PATH):
    inventory = pd.read_csv(PRODUCT_LIST_PATH, dtype={"ML_Score": float})
    inventory.columns = inventory.columns.str.strip()
    inventory.columns = inventory.columns.str.replace('\ufeff', '')
    if 'Inventory' in inventory.columns:
        inventory = inventory.rename(columns={'Inventory': 'Quantity'})
    if 'ML_Score' not in inventory.columns:
        inventory['ML_Score'] = 0.0
else:
    inventory = pd.DataFrame(columns=['Product_ID', 'Product_Name', 'Price', 'Quantity', 'ML_Score'])

def save_inventory():
    inventory.to_csv(PRODUCT_LIST_PATH, index=False)

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.configure(bg="white")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 12), padding=6, background='#007acc', foreground='white')
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=28)
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'), background="#007acc", foreground="white")

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Incoming", command=self.show_incoming).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Outgoing", command=self.show_outgoing).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Dead Stock Report", command=self.show_dead_stock).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Low Inventory Report", command=self.show_low_inventory).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Graph Analysis", command=self.show_graphs).pack(side="left", padx=10)


        self.page_frame = tk.Frame(root, bg="white")
        self.page_frame.pack(pady=10)

        self.tree = ttk.Treeview(root, columns=('ID', 'Name', 'Price', 'Quantity', 'ML Score'), show='headings')
        for col in ('ID', 'Name', 'Price', 'Quantity', 'ML Score'):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(pady=20, padx=20, fill="both", expand=True)

        self.update_table()

        ttk.Button(root, text="Daily ML Score Update", command=self.daily_ml_score_update).pack(pady=10)

    def clear_page(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in inventory.iterrows():
            self.tree.insert('', tk.END, values=(row['Product_ID'], row['Product_Name'], row['Price'], row['Quantity'], round(row['ML_Score'], 3)))

    def show_incoming(self):
        self.clear_page()
        tk.Label(self.page_frame, text="Select Product:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        product_names = inventory['Product_Name'].tolist()
        self.selected_product_in = tk.StringVar()
        self.product_dropdown_in = ttk.Combobox(self.page_frame, textvariable=self.selected_product_in, values=product_names, state="readonly")
        self.product_dropdown_in.grid(row=0, column=1, pady=5)

        tk.Label(self.page_frame, text="Quantity to Add:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.quantity_entry_in = tk.Entry(self.page_frame)
        self.quantity_entry_in.grid(row=1, column=1, pady=5)

        ttk.Button(self.page_frame, text="Add Stock", command=self.add_stock).grid(row=2, column=0, columnspan=2, pady=15)

    def add_stock(self):
        product_name = self.selected_product_in.get()
        qty = self.quantity_entry_in.get()

        if product_name and qty.isdigit():
            qty = int(qty)
            idx = inventory.index[inventory['Product_Name'] == product_name].tolist()[0]
            inventory.at[idx, 'Quantity'] += qty
            save_inventory()
            self.update_table()
            messagebox.showinfo("Success", f" Added {qty} units to {product_name}")
        else:
            messagebox.showerror("Error", "Please select product and enter valid quantity.")

    def show_outgoing(self):
        self.clear_page()
        tk.Label(self.page_frame, text="Select Product:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        product_names = inventory['Product_Name'].tolist()
        self.selected_product_out = tk.StringVar()
        self.product_dropdown_out = ttk.Combobox(self.page_frame, textvariable=self.selected_product_out, values=product_names, state="readonly")
        self.product_dropdown_out.grid(row=0, column=1, pady=5)

        tk.Label(self.page_frame, text="Quantity to Remove:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.quantity_entry_out = tk.Entry(self.page_frame)
        self.quantity_entry_out.grid(row=1, column=1, pady=5)

        ttk.Button(self.page_frame, text="Add to Cart", command=self.add_to_cart).grid(row=2, column=0, columnspan=2, pady=10)

        self.cart = ttk.Treeview(self.page_frame, columns=('Product', 'Unit Price', 'Quantity', 'Total Price'), show='headings')
        for col in ('Product', 'Unit Price', 'Quantity', 'Total Price'):
            self.cart.heading(col, text=col)
            self.cart.column(col, anchor="center")
        self.cart.grid(row=3, column=0, columnspan=2, pady=15, sticky="nsew")

        tk.Label(self.page_frame, text="Bill File Name:", bg="white").grid(row=4, column=0, sticky="w", pady=5)
        self.billname_entry = tk.Entry(self.page_frame)
        self.billname_entry.grid(row=4, column=1, pady=5)

        ttk.Button(self.page_frame, text="Generate Bill", command=self.generate_bill_multiple_items).grid(row=5, column=0, columnspan=2, pady=15)

        self.cart_list = []

    def add_to_cart(self):
        product_name = self.selected_product_out.get()
        qty = self.quantity_entry_out.get()

        if product_name and qty.isdigit():
            qty = int(qty)
            idx = inventory.index[inventory['Product_Name'] == product_name].tolist()[0]
            available_qty = inventory.at[idx, 'Quantity']
            unit_price = inventory.at[idx, 'Price']
            ml_score = inventory.at[idx, 'ML_Score']

            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return

            if available_qty >= qty:
                discounted_price = unit_price
                if ml_score < 4:
                    discount_percent = self.ask_discount_rate()
                    if discount_percent is not None:
                        discounted_price = unit_price * (1 - discount_percent / 100)
                        messagebox.showinfo("Discount Applied", f"{discount_percent}% OFF applied!")

                total_price = discounted_price * qty

                self.cart_list.append({
                    'Product_Name': product_name,
                    'Unit_Price': discounted_price,
                    'Quantity': qty,
                    'Total_Price': total_price
                })

                self.cart.insert('', tk.END, values=(product_name, f"${discounted_price:.2f}", qty, f"${total_price:.2f}"))
            else:
                messagebox.showerror("Error", f"Not enough stock! Available: {available_qty}")
        else:
            messagebox.showerror("Error", "Please select product and valid quantity.")

    def ask_discount_rate(self):
        discount_window = tk.Toplevel(self.root)
        discount_window.title("Select Discount %")
        discount_window.geometry("300x200")
        discount_window.configure(bg="white")

        tk.Label(discount_window, text="Select Discount:", bg="white").pack(pady=10)
        selected_discount = tk.IntVar(value=20)

        for rate in [10, 20, 30, 40, 50]:
            tk.Radiobutton(discount_window, text=f"{rate}% OFF", variable=selected_discount, value=rate, bg="white").pack(anchor="w", padx=20)

        confirm = ttk.Button(discount_window, text="Apply", command=discount_window.destroy)
        confirm.pack(pady=10)

        self.root.wait_window(discount_window)
        return selected_discount.get()

    def generate_bill_multiple_items(self):
        bill_name = self.billname_entry.get()
        if not bill_name or not self.cart_list:
            messagebox.showerror("Error", "Fill all fields and add products first!")
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        total_amount = sum(item['Total_Price'] for item in self.cart_list)
        bill_path = os.path.join(BILLS_FOLDER, f"{bill_name}.pdf")

        c = canvas.Canvas(bill_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height-80, "INVOICE")

        c.setFont("Helvetica", 12)
        c.drawString(50, height-130, f"Date: {date_str}")
        c.drawString(300, height-130, f"Time: {time_str}")
        c.line(30, height-140, width-30, height-140)

        y = height-170
        for item in self.cart_list:
            c.drawString(50, y, item['Product_Name'])
            c.drawString(250, y, f"${item['Unit_Price']:.2f}")
            c.drawString(370, y, str(item['Quantity']))
            c.drawString(470, y, f"${item['Total_Price']:.2f}")
            y -= 20

        c.line(30, y-10, width-30, y-10)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y-40, f"TOTAL: ${total_amount:.2f}")
        c.save()

        for item in self.cart_list:
            idx = inventory.index[inventory['Product_Name'] == item['Product_Name']].tolist()[0]
            inventory.at[idx, 'Quantity'] -= item['Quantity']
            inventory.at[idx, 'ML_Score'] += (0.0025 * item['Quantity'])

        save_inventory()
        self.update_table()
        self.cart.delete(*self.cart.get_children())
        self.cart_list.clear()
        messagebox.showinfo("Success", f"Bill '{bill_name}.pdf' generated successfully!")

    def daily_ml_score_update(self):
        for idx in inventory.index:
            inventory.at[idx, 'ML_Score'] -= 0.003
            if inventory.at[idx, 'ML_Score'] < 0:
                inventory.at[idx, 'ML_Score'] = 0
        save_inventory()
        self.update_table()
        messagebox.showinfo("Success", " Daily ML Score updated!")

    def show_dead_stock(self):
        self.clear_page()
        dead_stock = inventory[inventory['ML_Score'] < 4]
        dead_tree = ttk.Treeview(self.page_frame, columns=('ID', 'Name', 'Price', 'Quantity', 'ML Score'), show='headings')
        for col in ('ID', 'Name', 'Price', 'Quantity', 'ML Score'):
            dead_tree.heading(col, text=col)
            dead_tree.column(col, anchor="center")
        dead_tree.pack(pady=20, padx=20, fill="both", expand=True)

        for _, row in dead_stock.iterrows():
            dead_tree.insert('', tk.END, values=(row['Product_ID'], row['Product_Name'], row['Price'], row['Quantity'], round(row['ML_Score'], 3)))

    def show_low_inventory(self):
        self.clear_page()
        low_inventory_list = []

        for _, row in inventory.iterrows():
            ml_score = row['ML_Score']
            quantity = row['Quantity']
            product_name = row['Product_Name']
            product_id = row['Product_ID']
            price = row['Price']

            if 7 <= ml_score <= 10 and quantity < 15:
                status = "URGENT - Reorder Now"
                message = "🔥 Very High Seller, Low Stock!"
            elif 4 <= ml_score < 7 and quantity < 8:
                status = "Good Seller - Keep in Stock"
                message = "👍 Moderate Seller, Needs Restock"
            elif ml_score < 4 and quantity <= 5:
                status = "Dead Stock - Wait till Over"
                message = "💤 Dead Stock, Don't Reorder"
            else:
                continue

            low_inventory_list.append((product_id, product_name, round(ml_score, 3), quantity, status, message))

        low_tree = ttk.Treeview(self.page_frame, columns=('ID', 'Name', 'ML Score', 'Quantity', 'Status', 'Message'), show='headings')
        for col in ('ID', 'Name', 'ML Score', 'Quantity', 'Status', 'Message'):
            low_tree.heading(col, text=col)
            low_tree.column(col, anchor="center")
        low_tree.pack(pady=20, padx=20, fill="both", expand=True)

        for item in low_inventory_list:
            low_tree.insert('', tk.END, values=item)

        if not low_inventory_list:
            tk.Label(self.page_frame, text=" No Low Inventory Issues Found!", bg="white", font=('Segoe UI', 12, 'bold')).pack(pady=20)

    def show_graphs(self):
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Inventory Graph Analysis")
        graph_window.geometry("1200x800")

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))

        # Top 8 Selling Items
        top_sellers = inventory.sort_values(by='ML_Score', ascending=False).head(8)
        axs[0, 0].bar(top_sellers['Product_Name'], top_sellers['ML_Score'], color='limegreen')
        axs[0, 0].set_title("Top 8 High-Selling Items")
        axs[0, 0].set_ylabel("ML Score")
        axs[0, 0].tick_params(axis='x', labelsize=8, rotation=45)

        # Bottom 8 Least Selling
        bottom_sellers = inventory.sort_values(by='ML_Score', ascending=True).head(8)
        axs[0, 1].bar(bottom_sellers['Product_Name'], bottom_sellers['ML_Score'], color='tomato')
        axs[0, 1].set_title("Bottom 8 Low-Selling Items")
        axs[0, 1].set_ylabel("ML Score")
        axs[0, 1].tick_params(axis='x', labelsize=8, rotation=45)

        # Pie chart: Dead Stock vs Active
        dead = inventory[inventory['ML_Score'] < 4].shape[0]
        active = inventory.shape[0] - dead
        axs[1, 0].pie([dead, active], labels=['Dead Stock', 'Active'], autopct='%1.1f%%', colors=['gray', 'lightcoral'])
        axs[1, 0].set_title("Dead vs Active Products")

        # Hide unused subplot
        fig.delaxes(axs[1, 1])

        fig.tight_layout(pad=3.0)
        canvas_plot = FigureCanvasTkAgg(fig, master=graph_window)
        canvas_plot.draw()
        canvas_plot.get_tk_widget().pack(fill='both', expand=True)
        plt.close(fig)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.geometry("1250x750")
    root.mainloop()
