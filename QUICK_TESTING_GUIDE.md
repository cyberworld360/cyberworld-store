# Quick Testing Guide - Products & Payments

## ⚡ 5-Minute Quick Test

### 1. Admin: Create Product with Preview
```
1. Go to /admin/new
2. Fill in:
   - Title: "Test Product"
   - Description: "A test product"
   - Price: 25.00
   - Old Price: 35.00
   - Upload an image
3. Watch LIVE PREVIEW update on right side
4. See discount percentage (≈29%)
5. Check image preview before upload
6. Click "Create Product"
```

✅ **Expected**: Product appears on home page with image and discount shown

---

### 2. Customer: Shop and Add to Cart
```
1. Go to /
2. Find product you just created
3. Verify image, title, old price, discount %, new price visible
4. Click "Add to Cart"
5. Verify cart count in header increases
```

✅ **Expected**: Product in cart, cart count shows "1"

---

### 3. Checkout with Wallet (if logged in with balance)
```
1. Click cart icon → "View Cart"
2. Click "Proceed to Checkout"
3. Fill shipping: Name, Phone, City
4. Select "💰 Pay with Wallet Balance" if you have balance
5. Click "Pay GH₵XX.XX with Wallet"
6. Wait for success message
7. Check email for order confirmation
```

✅ **Expected**: 
- Order created
- Success message
- Cart cleared
- Email received

---

### 4. Checkout with Paystack (no account needed)
```
1. Go to home, add product to cart
2. Go to /cart, click "Proceed to Checkout"
3. Fill shipping: Name, Phone, City
4. Enter email: your-email@example.com
5. Select "💳 Pay with Paystack"
6. Click "Continue to Paystack"
7. Enter test card: 4111111111111111
8. Expiry: 01/25 (any future date)
9. CVC: 123 (any 3 digits)
10. Click "Charge Authorization"
```

✅ **Expected**:
- Redirects back to success page
- Success message appears
- Email received
- Order in admin dashboard

---

### 5. Test Coupon Code
```
1. Create coupon in database (or ask admin)
   Code: TEST10, Discount: 10%, Min: GH₵50

2. Add GH₵50+ products to cart
3. Go to checkout
4. Find "🎟️ Have a Promo Code?" section
5. Enter: TEST10
6. Click "Apply"
7. Watch discount appear in order summary
8. Final total updates
```

✅ **Expected**:
- Green success message
- Discount shows (GH₵X.XX saved)
- Final total reduced

---

## 🔍 Detailed Testing Scenarios

### Scenario A: Admin Creates Multiple Products

```bash
# Product 1: Simple product (no discount)
Title: Basic T-Shirt
Price: 15.00
Old Price: (leave empty)
Image: upload shirt.png

# Product 2: Product on sale
Title: Premium Shoes
Price: 45.00
Old Price: 60.00
Image: upload shoes.jpg
Featured: ☑ (check this)

# Product 3: Expensive item
Title: Designer Watch
Price: 150.00
Old Price: 200.00
Image: upload watch.png
```

**Test**: Check all three appear on home page with correct pricing and discount badges

---

### Scenario B: Complete Purchase Flow with Coupon

```
Step 1: Add multiple products
  - Add 2× T-Shirt (GH₵30 total)
  - Add 1× Shoes (GH₵45)
  - Cart total: GH₵75

Step 2: Checkout
  - Shipping: John Doe, 0501234567, Accra
  - Apply coupon: SAVE10 (10% off)
  - New total: GH₵67.50

Step 3: Paystack
  - Pay with card
  - Verify order confirmation email

Step 4: Verify Admin
  - New order in dashboard
  - Can see customer details, items, amount
  - Can update order status
```

---

### Scenario C: Insufficient Wallet Balance

```
Step 1: User has GH₵20 wallet balance
Step 2: Add product costing GH₵50 to cart
Step 3: Go to checkout
Step 4: Wallet option shows RED warning: "❌ Insufficient balance"
Step 5: Wallet option is DISABLED (can't select)
Step 6: Only Paystack available
Step 7: User must use Paystack or top-up wallet
```

---

### Scenario D: Invalid Coupon

```
Step 1: Checkout with GH₵50+ items
Step 2: Try coupon codes:
  - "INVALID" → Error: "Coupon not found"
  - "EXPIRED" → Error: "Coupon expired"
  - Expired in past → Error: "Coupon expired"
  - Max uses reached → Error: "Usage limit reached"

Step 3: Each shows RED error message
Step 4: Final total stays unchanged
Step 5: Can try different coupon
```

---

## 📱 Mobile Testing Checklist

### On iPhone 12 (390px width)

- [ ] Checkout page loads without horizontal scroll
- [ ] All form fields full-width
- [ ] Coupon input above button (stacked)
- [ ] Payment buttons full-width
- [ ] All text readable (not too small)
- [ ] Images scale properly
- [ ] Can scroll through entire form
- [ ] Keyboard doesn't cover form fields
- [ ] Submit button easily clickable

### On Android (375px width)

- [ ] Same as iPhone tests
- [ ] Test on Chrome browser
- [ ] Test on default Android browser
- [ ] Virtual keyboard accessible

---

## 🧪 Test Data

### Test Paystack Card Numbers

| Card | Number | Status |
|------|--------|--------|
| Visa | 4111111111111111 | Success |
| Visa (Decline) | 4000000000000002 | Declined |
| Mastercard | 5398935056570010 | Success |

**Expiry**: Any future date (01/25, 12/26, etc.)  
**CVV**: Any 3 digits (123, 456, 789)

### Test Coupons to Create

```sql
-- 10% discount, minimum GH₵50 order
INSERT INTO coupon (code, discount_type, discount_value, min_amount, max_uses, active)
VALUES ('WELCOME10', 'percent', 10, 50, 100, TRUE);

-- GH₵5 flat discount, no minimum
INSERT INTO coupon (code, discount_type, discount_value, min_amount, max_uses, active)
VALUES ('SAVE5', 'fixed', 5, 0, 999, TRUE);

-- Single use coupon (max_uses=1)
INSERT INTO coupon (code, discount_type, discount_value, min_amount, max_uses, active)
VALUES ('ONCE', 'percent', 15, 100, 1, TRUE);
```

---

## ✅ Final Verification Checklist

Before declaring "ready for production":

### Backend
- [ ] Python syntax valid: `python -m py_compile app.py` ✅
- [ ] All routes respond correctly
- [ ] Payment callbacks working
- [ ] Email sending working
- [ ] Database transactions atomic

### Frontend
- [ ] Admin form has image/product preview
- [ ] Checkout responsive on all sizes
- [ ] Payment form validation works
- [ ] Coupon validation working
- [ ] Error messages user-friendly

### Integration
- [ ] Paystack sandbox works end-to-end
- [ ] Wallet payment works
- [ ] Coupon system integrated
- [ ] Email notifications sending
- [ ] Orders created in database

### Deployment Ready
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Static files collected (if needed)
- [ ] Paystack live keys ready (don't switch yet!)
- [ ] Email configured and tested

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Image not showing | Check image URL, verify S3 (if used), browser cache |
| Coupon not applying | Check coupon exists, not expired, min amount met |
| Email not sending | Check MAIL_SERVER, credentials, spam folder |
| Cart empty on checkout | Verify session not cleared, check cookie settings |
| Payment fails silently | Check browser console F12, check server logs |
| Mobile buttons too small | Check viewport meta tag, resize browser |

---

## 📞 Support

**For issues**, check:
1. Browser console: F12 → Console tab
2. Server logs: Terminal where Flask running
3. Database: Check relevant tables
4. Email settings: Test with `/admin/test-email`
5. Paystack dashboard: Check recent transactions

---

**Last Updated**: 2024  
**Version**: 1.0  
**Status**: ✅ Testing Guide Complete
