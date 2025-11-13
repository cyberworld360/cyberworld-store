# How Admins Can Add Products to CyberWorld Store

## Step-by-Step Guide

### **Step 1: Access the Admin Login**
1. Open your browser and go to: `https://cyberworldstore.shop/admin/login`
   - Or locally: `http://localhost:5000/admin/login`
2. You'll see the admin login page

### **Step 2: Login with Admin Credentials**
Enter your admin credentials:
- **Default Username:** `admin`
- **Default Password:** `admin` (⚠️ Change this in production!)

**Note:** You can change the admin password by updating the `ADMIN_PASSWORD` environment variable in your `.env` file.

### **Step 3: Access the Admin Dashboard**
Once logged in, you'll see the **Product Management Dashboard** with:
- ✅ List of all existing products
- ✅ Featured product badges
- ✅ Product images
- ✅ Prices and discount information
- ✅ Edit/Delete buttons for each product
- ✅ **"+ Add New Product"** button

### **Step 4: Click "Add New Product"**
Click the green **"+ Add New Product"** button in the top right corner of the dashboard.

### **Step 5: Fill in Product Details**

#### **Required Fields:**
1. **Product Title** (max 255 characters)
   - Example: "Wireless Bluetooth Speaker"
   - This is mandatory

2. **Price (GH₵)** (numeric value, cannot be negative)
   - Example: `150.50`
   - The selling price for your product
   - This is mandatory

#### **Optional Fields:**
3. **Product Description** (max 500 characters)
   - Example: "High-quality wireless speaker with 12-hour battery life"
   - Brief description shown in product listings

4. **Old Price (GH₵)** (numeric value, cannot be negative)
   - Example: `199.99`
   - Used to show discounts (e.g., "Was ₵199.99, Now ₵150.50")
   - Leave empty if there's no discount

5. **Upload Product Image**
   - Supported formats: PNG, JPG, JPEG, GIF
   - Maximum size: 5MB
   - If no image is uploaded, a placeholder image will be used

6. **Featured Product** (checkbox)
   - Check this box to display the product on the homepage
   - Uncheck if it's a regular product

### **Step 6: Submit the Form**
Click **"Create Product"** button to save the product.

### **Success!**
- You'll see a success message: `Product "Product Name" created successfully!`
- You'll be redirected to the admin dashboard
- Your new product is now visible in the product list

---

## Complete Example

**Let's add a "Wireless Modem 4G/5G" product:**

```
Title: Wireless Modem 4G/5G
Description: High-speed wireless modem with 4G/5G support
Price: 700.00
Old Price: 780.00
Image: (upload modem_4g5g.jpg)
Featured: ✓ (checked)
```

After clicking "Create Product", the product will:
- ✅ Appear on the homepage as a featured product
- ✅ Show "Was ₵780.00, Now ₵700.00"
- ✅ Have the uploaded image displayed
- ✅ Be available for customers to add to cart and purchase

---

## Product Management Operations

### **✏️ Edit a Product**
1. Go to Admin Dashboard (`/admin`)
2. Find the product you want to edit
3. Click the **"Edit"** button on the product card
4. Modify any field (title, price, description, image, featured status)
5. Click **"Update Product"**

### **🗑️ Delete a Product**
1. Go to Admin Dashboard (`/admin`)
2. Find the product you want to delete
3. Click the **"Delete"** button
4. Confirm the deletion in the dialog
5. Product is immediately removed

### **🚪 Logout**
Click **"Logout"** in the admin panel to end your session.

---

## Important Information

### **Database Storage**
- All products are stored in SQLite database (`data.db`)
- Images are stored in `static/images/` folder
- Filename conflicts are prevented with automatic timestamps

### **Image Upload Details**
- **Location:** `static/images/`
- **Naming:** Automatically timestamped (e.g., `1731234567_modem.jpg`)
- **Max Size:** 5MB
- **Formats:** PNG, JPG, JPEG, GIF

### **Price Validation**
- Prices must be valid numbers (e.g., 100, 99.99, 0.50)
- Negative prices are not allowed
- Both prices use GH₵ currency

### **Featured Products**
- Featured products appear on the homepage
- Maximum of 6-8 featured products recommended for best display
- You can change featured status anytime by editing the product

---

## Quick Reference

| Action | URL | Required Login |
|--------|-----|-----------------|
| Admin Login | `/admin/login` | ❌ No |
| Dashboard | `/admin` | ✅ Yes |
| Add Product | `/admin/new` | ✅ Yes |
| Edit Product | `/admin/edit/<id>` | ✅ Yes |
| Delete Product | Form at `/admin` | ✅ Yes |
| Logout | `/admin/logout` | ✅ Yes |

---

## Troubleshooting

### **Problem: "Product title is required"**
- ✅ Solution: Make sure you entered a product title before submitting

### **Problem: "Invalid price format"**
- ✅ Solution: Make sure prices are valid numbers (e.g., 100, 99.50)
- ✅ Check that prices are not negative

### **Problem: "Image upload failed"**
- ✅ Check file format (only PNG, JPG, JPEG, GIF allowed)
- ✅ Check file size (max 5MB)
- ✅ Try uploading a different image

### **Problem: "Error creating product"**
- ✅ Check that all required fields are filled
- ✅ Check database permissions
- ✅ Try again or contact support

---

## Security Notes

⚠️ **Important Security Tips:**
1. **Change Default Password:** Update the admin password from "admin" to a strong password
2. **Use HTTPS:** Always use HTTPS in production (https://cyberworldstore.shop)
3. **Secure Credentials:** Never share admin login credentials
4. **Regular Backups:** Back up your database regularly
5. **Update Environment:** Use `.env` file for sensitive configuration

---

Last Updated: November 11, 2025
