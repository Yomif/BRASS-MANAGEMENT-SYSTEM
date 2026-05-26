# ======================================================
#       BRASS STORE SHOPPING SYSTEM
# ======================================================
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import sqlite3
from datetime import datetime
import os

# ======================================================
# APP SETTINGS
# ======================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ======================================================
# DATABASE SETUP
# ======================================================

conn = sqlite3.connect("brass_store.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    item_name TEXT,
    category TEXT,
    price REAL,
    quantity INTEGER,
    subtotal REAL,
    discount REAL,
    final_amount REAL,
    date TEXT
)
""")
conn.commit()

# ======================================================
# MAIN WINDOW
# ======================================================

app = ctk.CTk()
app.geometry("950x750")
app.title("Brass Store Shopping System")
app.resizable(False, False)

cart = []

# ======================================================
# FUNCTIONS
# ======================================================

def toggle_mode():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")


def add_to_cart():
    try:
        customer = customer_entry.get().strip()
        item     = item_entry.get().strip()
        category = category_option.get()
        price    = float(price_entry.get())
        quantity = int(quantity_entry.get())

        if not customer or not item:
            messagebox.showerror("Error", "Please fill all fields")
            return
        if price <= 0 or quantity <= 0:
            messagebox.showerror("Error", "Price and Quantity must be greater than 0")
            return

        subtotal = price * quantity
        cart.append({"customer": customer, "item": item, "category": category,
                     "price": price, "quantity": quantity, "subtotal": subtotal})

        cart_box.insert("end",
            f"{item} | {category} | ₦{price:,.2f} x {quantity} = ₦{subtotal:,.2f}\n")
        clear_inputs()
        messagebox.showinfo("Success", "Item added to cart successfully")

    except ValueError:
        messagebox.showerror("Invalid Input", "Enter valid price and quantity")


def generate_receipt():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    # ── Build receipt text ──────────────────────────────
    total         = sum(i["subtotal"] for i in cart)
    discount      = total * 0.10 if total >= 10000 else 0
    final_amount  = total - discount
    customer_name = cart[0]["customer"]
    now           = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    lines = [
        "=========================================",
        "          BRASS STORE RECEIPT",
        "=========================================",
        f"Customer : {customer_name}",
        f"Date     : {now}",
        "-----------------------------------------",
    ]
    for it in cart:
        lines.append(f"{it['item']}  ({it['category']})")
        lines.append(f"  ₦{it['price']:,.2f} x {it['quantity']} = ₦{it['subtotal']:,.2f}")
    lines += [
        "-----------------------------------------",
        f"Subtotal     : ₦{total:,.2f}",
        f"Discount 10% : ₦{discount:,.2f}" if discount else "Discount     : ₦0.00",
        f"TOTAL DUE    : ₦{final_amount:,.2f}",
        "=========================================",
        "   THANK YOU FOR SHOPPING WITH US! 🛍️",
        "=========================================",
    ]
    receipt_text = "\n".join(lines)

    # ── Save to DB ──────────────────────────────────────
    for it in cart:
        cursor.execute("""
            INSERT INTO sales
              (customer_name,item_name,category,price,quantity,subtotal,discount,final_amount,date)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (it["customer"], it["item"], it["category"], it["price"],
              it["quantity"], it["subtotal"], discount, final_amount, now))
    conn.commit()

    # ── Show receipt in a styled in-app popup ──────────
    show_receipt_popup(receipt_text, final_amount, discount)


def show_receipt_popup(receipt_text, final_amount, discount):
    """Opens a polished Toplevel receipt window centred over the main app."""
    popup = ctk.CTkToplevel(app)
    popup.title("Receipt")
    popup.geometry("520x620")
    popup.resizable(False, False)
    popup.grab_set()          # modal — blocks main window until closed
    popup.focus_force()

    # Centre popup over the main window
    app.update_idletasks()
    x = app.winfo_x() + (app.winfo_width()  - 520) // 2
    y = app.winfo_y() + (app.winfo_height() - 620) // 2
    popup.geometry(f"520x620+{x}+{y}")

    # ── Header bar ─────────────────────────────────────
    header_bar = ctk.CTkFrame(popup, fg_color=("#1a73e8", "#1a73e8"), corner_radius=0, height=60)
    header_bar.pack(fill="x")
    header_bar.pack_propagate(False)

    ctk.CTkLabel(
        header_bar,
        text="🧾  RECEIPT",
        font=("Arial", 22, "bold"),
        text_color="white",
    ).pack(side="left", padx=20, pady=10)

    # ── Receipt text box ───────────────────────────────
    txt = ctk.CTkTextbox(
        popup,
        width=480,
        height=420,
        font=("Courier New", 12),
        corner_radius=10,
    )
    txt.pack(padx=20, pady=16)
    txt.insert("end", receipt_text)
    txt.configure(state="disabled")

    # ── Summary badges ─────────────────────────────────
    badge_frame = ctk.CTkFrame(popup, fg_color="transparent")
    badge_frame.pack(pady=(0, 10))

    if discount > 0:
        disc_badge = ctk.CTkFrame(badge_frame, fg_color=("#fff3cd", "#5a4000"), corner_radius=8)
        disc_badge.pack(side="left", padx=8)
        ctk.CTkLabel(disc_badge, text=f"💰 Saved ₦{discount:,.2f}", font=("Arial", 12, "bold"),
                     text_color=("#856404", "#ffd166")).pack(padx=12, pady=6)

    total_badge = ctk.CTkFrame(badge_frame, fg_color=("#d1e7dd", "#1a3a2a"), corner_radius=8)
    total_badge.pack(side="left", padx=8)
    ctk.CTkLabel(total_badge, text=f"✅ Total  ₦{final_amount:,.2f}", font=("Arial", 12, "bold"),
                 text_color=("#0a5c2e", "#75c99a")).pack(padx=12, pady=6)

    # ── Buttons ────────────────────────────────────────
    btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
    btn_frame.pack(pady=10)

    ctk.CTkButton(
        btn_frame, text="💾  Save to File", width=180, height=40,
        command=lambda: [save_receipt_text(receipt_text), popup.destroy()]
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame, text="✖  Close", width=120, height=40,
        fg_color=("gray70", "gray30"), hover_color=("gray60", "gray20"),
        command=popup.destroy
    ).pack(side="left", padx=10)


def save_receipt_text(text):
    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    messagebox.showinfo("Saved", f"Receipt saved as {filename}")


def save_receipt():
    messagebox.showinfo("Info", "Generate a receipt first, then use 'Save to File' inside the receipt window.")


def clear_inputs():
    item_entry.delete(0, "end")
    price_entry.delete(0, "end")
    quantity_entry.delete(0, "end")


def clear_all():
    cart.clear()
    for w in (customer_entry, item_entry, price_entry, quantity_entry):
        w.delete(0, "end")
    cart_box.delete("0.0", "end")


def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if username == "admin" and password == "1234":
        login_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


# ======================================================
# LOGIN FRAME WITH BACKGROUND IMAGE
# ======================================================

login_frame = ctk.CTkFrame(app)
login_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(login_frame, width=950, height=750, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

IMAGE_SEARCH_PATHS = [
    os.path.join(os.path.expanduser("~"), "Downloads", "heidi-fin-2TLREZi7BUg-unsplash.jpg"),
    os.path.join(os.path.expanduser("~"), "Desktop",   "heidi-fin-2TLREZi7BUg-unsplash.jpg"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "heidi-fin-2TLREZi7BUg-unsplash.jpg"),
]

bg_photo = None
for img_path in IMAGE_SEARCH_PATHS:
    if os.path.exists(img_path):
        try:
            pil_img  = Image.open(img_path).resize((950, 750), Image.LANCZOS)
            pil_img  = pil_img.filter(ImageFilter.GaussianBlur(radius=3))
            bg_photo = ImageTk.PhotoImage(pil_img)
            canvas.create_image(0, 0, anchor="nw", image=bg_photo)
        except Exception as e:
            print(f"Background image error: {e}")
        break

if bg_photo is None:
    canvas.configure(bg="#1a1a2e")

canvas.create_rectangle(0, 0, 950, 750, fill="black", stipple="gray50", outline="")

card = ctk.CTkFrame(login_frame, width=420, height=480, corner_radius=20,
                    fg_color=("white", "#1e1e2e"),
                    border_width=1, border_color=("#d0d0d0", "#3a3a5c"))
card.place(relx=0.5, rely=0.5, anchor="center")
card.pack_propagate(False)

ctk.CTkLabel(card, text="🛒", font=("Arial", 48)).pack(pady=(30, 0))
ctk.CTkLabel(card, text="BRASS STORE", font=("Arial", 26, "bold"),
             text_color=("#1a73e8", "#6ea8fe")).pack(pady=(4, 0))
ctk.CTkLabel(card, text="Point of Sale System", font=("Arial", 12),
             text_color=("gray50", "gray70")).pack(pady=(2, 16))

ctk.CTkFrame(card, height=1, fg_color=("gray80", "gray40")).pack(fill="x", padx=30, pady=(0, 16))

username_entry = ctk.CTkEntry(card, placeholder_text="👤  Username",
                               width=300, height=44, corner_radius=10, font=("Arial", 13))
username_entry.pack(pady=6)

password_entry = ctk.CTkEntry(card, placeholder_text="🔒  Password", show="*",
                               width=300, height=44, corner_radius=10, font=("Arial", 13))
password_entry.pack(pady=6)

app.bind("<Return>", lambda e: login())

ctk.CTkButton(card, text="Login  →", width=300, height=44, corner_radius=10,
              font=("Arial", 14, "bold"), command=login).pack(pady=18)
ctk.CTkLabel(card, text="Demo  •  admin / 1234", font=("Arial", 11),
             text_color=("gray50", "gray60")).pack(pady=(0, 20))

# ======================================================
# MAIN FRAME
# ======================================================

main_frame = ctk.CTkFrame(app)

# Header
header = ctk.CTkFrame(main_frame)
header.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(header, text="🛍️ BRASS STORE SHOPPING SYSTEM",
             font=("Arial", 28, "bold")).pack(side="left", padx=20, pady=20)
ctk.CTkButton(header, text="Toggle Dark Mode", command=toggle_mode,
              width=180).pack(side="right", padx=20)

# Inputs
input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(input_frame, text="Customer Name").grid(row=0, column=0, padx=10, pady=10)
customer_entry = ctk.CTkEntry(input_frame, width=250)
customer_entry.grid(row=0, column=1, padx=10, pady=10)

ctk.CTkLabel(input_frame, text="Item Name").grid(row=1, column=0, padx=10, pady=10)
item_entry = ctk.CTkEntry(input_frame, width=250)
item_entry.grid(row=1, column=1, padx=10, pady=10)

ctk.CTkLabel(input_frame, text="Category").grid(row=2, column=0, padx=10, pady=10)
category_option = ctk.CTkOptionMenu(input_frame,
    values=["Electronics", "Fashion", "Food", "Accessories", "Home Items"], width=250)
category_option.grid(row=2, column=1, padx=10, pady=10)

ctk.CTkLabel(input_frame, text="Item Price").grid(row=3, column=0, padx=10, pady=10)
price_entry = ctk.CTkEntry(input_frame, width=250)
price_entry.grid(row=3, column=1, padx=10, pady=10)

ctk.CTkLabel(input_frame, text="Quantity").grid(row=4, column=0, padx=10, pady=10)
quantity_entry = ctk.CTkEntry(input_frame, width=250)
quantity_entry.grid(row=4, column=1, padx=10, pady=10)

# Buttons
button_frame = ctk.CTkFrame(main_frame)
button_frame.pack(fill="x", padx=20, pady=10)

ctk.CTkButton(button_frame, text="➕ Add To Cart",      command=add_to_cart,
              width=170, height=40).grid(row=0, column=0, padx=10, pady=10)
ctk.CTkButton(button_frame, text="🧾 Generate Receipt", command=generate_receipt,
              width=170, height=40, fg_color=("#1a73e8","#1a73e8"),
              hover_color=("#1558b0","#1558b0")).grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(button_frame, text="🗑️ Clear All",        command=clear_all,
              width=170, height=40, fg_color="red",
              hover_color="darkred").grid(row=0, column=2, padx=10, pady=10)

# Cart
ctk.CTkLabel(main_frame, text="🛒 Shopping Cart", font=("Arial", 18, "bold")).pack(pady=(10, 4))
cart_box = ctk.CTkTextbox(main_frame, width=880, height=180)
cart_box.pack(pady=6, padx=20)

# ======================================================
# RUN
# ======================================================

app.mainloop()