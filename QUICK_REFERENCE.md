# Quick Reference — Final Features Implementation

## What's New ✨

### 1. Coupon Discount Now Applied at Checkout
- **Before**: Discount showed in UI but customer paid full price
- **After**: Discount deducted from actual payment (both wallet & Paystack)
- **How it works**: 
  - Customer applies coupon code at checkout
  - Discount calculated based on coupon type (percent/fixed)
  - Final amount = Subtotal - Discount
  - Customer charged final amount only

### 2. City/Town Added to Shipping
- **New field**: City/Town input required at checkout
- **Used for**: Order fulfillment and delivery
- **Stored in**: Order confirmation emails and payment metadata
- **Required**: Yes (form won't submit without it)

### 3. Coupon Images for Marketing
- **New feature**: Admins can upload images for coupons
- **Display**: Image shows in checkout popup when coupon applied
- **Use case**: Brand coupons, seasonal promotions, visual discounts
- **How to use**:
  1. Go to Admin → Coupons
  2. Create/Edit coupon
  3. Upload image (max 2MB)
  4. Save coupon

---

## For Customers

### Applying a Coupon at Checkout
1. Add items to cart
2. Go to checkout
3. Under "Coupon Code" section, enter code
4. Click "Apply"
5. See discount amount deducted from total
6. Complete payment with discounted amount

### Wallet Payment with Coupon
1. Apply coupon (see discount)
2. Select "Pay with Wallet"
3. Your wallet charged: `Subtotal - Discount`
4. Confirmation email shows breakdown

### Paystack Payment with Coupon
1. Apply coupon (see discount)
2. Select "Pay with Paystack"
3. Paystack charged: `Subtotal - Discount`
4. Payment confirmation shows final amount

---

## For Admins

### Creating a Coupon with Image
```
1. Admin Dashboard → Coupons → Create Coupon
2. Enter coupon code (e.g., "SAVE20")
3. Choose discount type:
   - Percentage (e.g., 20% off)
   - Fixed amount (e.g., GH₵10 off)
4. Set discount value
5. Optional: Set min order amount, max uses, expiry date
6. Upload promotional image (PNG/JPG)
7. Click "Create Coupon"
```

### Editing Coupon Image
```
1. Admin Dashboard → Coupons → Find coupon
2. Click Edit
3. Upload new image (old image will be replaced)
4. Or leave empty to keep existing image
5. Click "Update Coupon"
```

### Viewing Coupon Usage
```
Admin Dashboard → Coupons
- See "Current Usage: X/Y" for each coupon
- X = times used, Y = max uses (or ∞ for unlimited)
```

### Disabling a Coupon
```
1. Edit coupon
2. Uncheck "Active" checkbox
3. Save
- Coupon appears as invalid to customers
```

---

## Email Notifications

### Customer Receives (Wallet Payment)
```
Subject: Order confirmation — wallet payment [REF]

Your order details:
Name: [Customer Name]
Phone: [Customer Phone]
City: [Customer City]
Subtotal: GH₵100.00
Discount: -GH₵20.00
Final Amount: GH₵80.00

Wallet Balance After Payment: GH₵150.00
Items: [Item list]
```

### Admin Receives (Wallet Payment)
```
Subject: New wallet order received — [REF]

Customer: customer@email.com
Name: [Name]
Phone: [Phone]
City: [City]
Subtotal: GH₵100.00
Discount: -GH₵20.00 (SAVE20)
Final Amount: GH₵80.00
Items: [Item list]
```

---

## Technical Details

### Coupon Calculation Examples

**Percentage Discount with Cap**
```
Coupon: 20% off, max discount GH₵50
Order: GH₵500
Calculation: 500 × 20% = GH₵100
Applied: GH₵50 (capped)
Final: GH₵450
```

**Fixed Amount Discount**
```
Coupon: GH₵25 off
Order: GH₵80
Calculation: 80 - 25 = GH₵55
Final: GH₵55
```

**Minimum Order Amount**
```
Coupon: GH₵50 off, min GH₵500
Order: GH₵300
Result: ❌ "Minimum order amount: GH₵500"
```

### File Upload Settings
- **Max size**: 2MB per image
- **Formats**: JPG, PNG, GIF, WebP, SVG
- **Storage**: `/static/images/coupons/`
- **Naming**: `coupon_[CODE]_[UUID].ext`

---

## Troubleshooting

### Coupon Not Applying
1. Check if coupon code is correct (case-insensitive)
2. Verify coupon is active
3. Check if minimum order amount is met
4. Verify coupon hasn't expired
5. Check if usage limit reached

### Image Not Showing
1. Verify file size < 2MB
2. Check file format (JPG/PNG recommended)
3. Try reuploading
4. Clear browser cache

### Payment Not Working
1. Ensure coupon is applied
2. Check wallet/Paystack settings
3. Verify user is logged in (for wallet)
4. Check PAYSTACK_SECRET_KEY env variable
5. Review app error logs

### Email Not Sent
1. Check SMTP settings in .env
2. Verify ADMIN_EMAIL is set
3. Check internet connection
4. Review app debug logs

---

## Data Flow Diagram

```
Checkout Page
    ↓
Customer enters coupon code
    ↓
Frontend validates: GET /api/validate-coupon
    ↓
Backend checks:
  - Code exists?
  - Coupon valid?
  - Min amount met?
  - Not expired?
  - Usage limit ok?
    ↓
Returns: discount amount + image
    ↓
Frontend updates total display + shows image popup
    ↓
Hidden coupon_id sent with payment
    ↓
Backend Payment Route (Paystack or Wallet)
    ↓
Recalculates discount
    ↓
Charges final_total (subtotal - discount)
    ↓
Increments coupon.current_uses
    ↓
Sends confirmation email with breakdown
```

---

## Deployment Checklist

- [ ] Update database schema (auto-migrates)
- [ ] Create `/static/images/coupons/` directory
- [ ] Verify SMTP settings for emails
- [ ] Test coupon creation with image
- [ ] Test checkout with coupon
- [ ] Test both payment methods
- [ ] Verify email notifications
- [ ] Test on production (staging first)

---

## Version Info
- **Implementation Date**: November 12, 2025
- **Features Added**: 3 (coupon discounts, city field, coupon images)
- **Files Modified**: 3 (app.py, checkout.html, admin_coupon_edit.html)
- **Database Changes**: 1 field added (image_url to Coupon)
- **Backward Compatible**: ✅ Yes
