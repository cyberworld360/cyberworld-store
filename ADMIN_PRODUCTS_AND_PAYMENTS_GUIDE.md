# Admin Products & Payments - Complete Guide

## 📋 Overview

This guide covers the complete admin product management system and customer payment flow, including recent improvements for better UX and responsive design.

---

## 🖼️ ADMIN PRODUCT MANAGEMENT

### Features Added/Enhanced

#### 1. **Image Preview Before Upload**
- **Location**: [templates/admin_edit.html](templates/admin_edit.html) (Lines: Image preview container)
- **What It Does**: 
  - Shows preview of selected image BEFORE uploading
  - Displays file size (in KB)
  - Shows image dimensions (width × height)
  - Allows user to cancel and select a different image
  - Validates file size (max 5MB) with user feedback

**How to Use**:
1. Click "Upload Product Image" file input
2. Select an image from your computer
3. Preview appears below with file info
4. If not satisfied, click "Cancel Upload" to try another
5. Once happy, save the product

**Example Flow**:
```
Admin clicks file input
  ↓
Selects image.jpg (2.4 MB, 1200×800)
  ↓
Preview shows with dimensions
  ↓
Can cancel or proceed to save
```

#### 2. **Live Product Preview**
- **Location**: [templates/admin_edit.html](templates/admin_edit.html) (Lines: Product preview section)
- **What It Does**:
  - Shows how product appears to customers AS YOU TYPE
  - Updates title, description, price in real-time
  - Calculates and displays discount percentage
  - Shows featured product badge
  - Uses actual product image (or placeholder)

**How to Use**:
1. Enter product details in form (left side)
2. Watch preview update on right side
3. See exactly how customers will see it
4. Make adjustments until happy
5. Click "Create/Update Product"

**Fields Tracked**:
- Title → Updates in preview title
- Description → Updates in preview text
- Current Price → Shows in large blue text
- Old Price → Shows strikethrough, triggers discount badge
- Featured → Shows/hides ⭐ badge
- Image → Shows preview image

#### 3. **Image Upload Validation**
- Validates file type: PNG, JPG, JPEG, GIF only
- Validates file size: Max 5MB
- Shows clear error messages if validation fails
- Prevents submission if file invalid

---

## 🛍️ CUSTOMER SHOPPING FLOW

### Page Structure

#### 1. **Product Listing Page** (`/`)
- Shows all products in responsive grid
- Each product shows:
  - Product image (with fallback placeholder)
  - Title
  - Description
  - Current price (in green)
  - Old price (strikethrough if discounted)
  - Discount percentage badge
  - Featured product indicator (⭐)
  - Add to cart button

**Responsive**:
- Desktop: 2-column grid
- Tablet: 2-column grid with adjusted sizing
- Mobile: 1-column full width

#### 2. **Product Detail Page** (`/product/<id>`)
- Full product information
- Large product image
- Detailed description
- Pricing with discount info
- Quantity selector
- Add to cart button
- Related products (optional)

#### 3. **Shopping Cart** (`/cart`)
- Shows all items in cart
- Quantity editor for each item
- Subtotal calculation
- Actions:
  - **Update Cart**: Recalculate after quantity changes
  - **Proceed to Checkout**: Go to payment
  - **Continue Shopping**: Return to products
  - **Clear Cart**: Empty entire cart

**Responsive**: 
- Converts to mobile-friendly table on small screens
- Button layout adapts (stacks on mobile)

#### 4. **Checkout Page** (`/checkout`)
- 🎟️ **Promo Code Section** (Optional)
  - Enter coupon code
  - Click "Apply"
  - Shows discount and final total
  - Error messages for invalid codes

- 📋 **Order Summary**
  - Shows all cart items with quantities
  - Subtotal
  - Discount (if coupon applied)
  - Final total (highlighted in green)

- 🚚 **Shipping Information**
  - Full Name (required)
  - Phone Number (required)
  - City/Town (required)

- 💳 **Payment Method Selection**
  - **Wallet Balance** (if logged in)
    - Shows available balance
    - Indicates if insufficient (red warning)
    - Only available if balance ≥ final total
  
  - **Paystack** (always available)
    - Card/Mobile money payment
    - Secure payment gateway
    - Works without account login

- 📧 **Email Field** (for Paystack)
  - Pre-filled if logged in
  - Required for payment confirmation
  - Hidden if wallet payment selected

**Mobile Responsive**:
- All form fields stack vertically
- Payment buttons full-width on mobile
- Coupon input becomes single-column
- Touch-friendly spacing (44px+ buttons)

---

## 💳 PAYMENT METHODS

### 1. **Paystack Payment** 

**Flow**:
```
User clicks "Continue to Paystack" on checkout
  ↓
Form validates shipping info and email
  ↓
Payment details sent to Paystack API
  ↓
User redirected to Paystack hosted form
  ↓
User enters card/mobile money details
  ↓
Paystack processes payment
  ↓
Paystack redirects back to app with reference
  ↓
App verifies payment with Paystack API
  ↓
Order created if verified
  ↓
Email sent to customer and admin
  ↓
Success message and redirect to home
```

**Features**:
- ✅ Secure card payments
- ✅ Mobile money integration
- ✅ Automatic email notifications
- ✅ Order tracking
- ✅ Payment verification
- ✅ Double-payment prevention

**Error Handling**:
- Network timeout → Flash warning, redirect to checkout
- Paystack API error → Flash danger message
- Missing reference → Flash warning, redirect home
- Payment failed → Flash warning with Paystack message

**Implementation**: [app.py](app.py) lines 2587-2700 (init), 3028-3300 (callback)

### 2. **Wallet Payment**

**Flow**:
```
User selects "Pay with Wallet" on checkout
  ↓
App checks wallet balance
  ↓
If insufficient:
  - Shows red warning
  - Prevents selection
  - Redirects to choose different method

If sufficient:
  User clicks "Pay GH₵XXX with Wallet"
  ↓
Form validates (name, phone, city)
  ↓
Wallet balance deducted
  ↓
Order created in database
  ↓
Email sent to customer and admin
  ↓
Success message and redirect to home
```

**Features**:
- ✅ Instant payment (no gateway)
- ✅ Balance pre-validation
- ✅ Atomic transaction (all or nothing)
- ✅ Auto email notifications
- ✅ Balance update in email

**Error Handling**:
- Insufficient balance → Shows red warning, prevents payment
- Database error → Rolls back, shows error, redirects to checkout
- Email error → Payment still completes, logged for admin follow-up

**Implementation**: [app.py](app.py) lines 2782-3027

---

## 🎟️ COUPON/DISCOUNT SYSTEM

### Features

- **Code Validation**: Check if code exists and is valid
- **Expiration**: Supports expiry dates
- **Usage Limits**: Set max uses per coupon
- **Amount Thresholds**: Minimum order amount requirement
- **Discount Types**: 
  - Percentage discount (e.g., 10% off)
  - Fixed amount discount (e.g., GH₵5 off)
- **One-Time Use**: Can limit to single use (optional)

### How to Use (Customer)

1. On checkout page, find "🎟️ Have a Promo Code?" section
2. Type coupon code (case-insensitive)
3. Click "Apply" button
4. **If valid**:
   - Green success message
   - Discount shown in order summary
   - Final total updated
   - Payment button now shows discounted amount
5. **If invalid**:
   - Red error message explaining reason
   - Discount removed from order
   - Original total shown

### Example Coupons (for testing)

Create these in database or admin panel:
```
SAVE10 → 10% discount (min: GH₵50)
FLAT5 → GH₵5 off (min: GH₵25)
WELCOME → 15% first purchase discount
```

### Error Messages

| Scenario | Message |
|----------|---------|
| Code doesn't exist | "Coupon code not found" |
| Code expired | "Coupon has expired" |
| Max uses reached | "Coupon usage limit reached" |
| Below minimum amount | "Coupon requires minimum order of GH₵XX" |
| Already used (one-time) | "Coupon has already been used" |

### Implementation

- **API Endpoint**: [app.py](app.py) `/api/validate-coupon` (POST)
- **Database Model**: `Coupon` table with fields:
  - `code`: Coupon code
  - `discount_type`: 'percent' or 'fixed'
  - `discount_value`: 10 (for 10%) or 5 (for GH₵5)
  - `min_amount`: Minimum order amount
  - `max_uses`: Maximum times this code can be used
  - `current_uses`: Current usage count
  - `expiry_date`: When coupon expires
  - `active`: Enable/disable coupon

---

## 📧 EMAIL NOTIFICATIONS

### Paystack Payment

**To Customer**:
- Subject: `[Cyber World Store] Order confirmation — Paystack payment [REF]`
- Contains: Payment verified, order reference, items list, amount paid, next steps
- HTML formatted with branding

**To Admin**:
- Subject: `[Cyber World Store] New Paystack order received — [REF]`
- Contains: Customer email, amount, items, action checklist
- Quick access to order in admin dashboard

### Wallet Payment

**To Customer**:
- Subject: `[Cyber World Store] Order confirmation — wallet payment [REF]`
- Contains: Items ordered, amount charged, remaining wallet balance, tracking link
- HTML formatted with branding

**To Admin**:
- Subject: `[Cyber World Store] New wallet order received — [REF]`
- Contains: Customer details, items, amount, action steps
- Quick access link to admin order view

### Email Features

- ✅ HTML and plain text versions
- ✅ Product images embedded (if available)
- ✅ Professional styling
- ✅ Async sending (doesn't block order flow)
- ✅ Error logging for failed emails
- ✅ Retry mechanism for failed deliveries

### Configuration

Set these environment variables:
```
MAIL_SERVER=smtp.gmail.com (or your provider)
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

**Testing**: Visit `/admin/test-email` to send test notification

---

## 🎨 RESPONSIVE DESIGN IMPROVEMENTS

### Breakpoints

- **Desktop**: 1024px+ (2-3 column layouts)
- **Tablet**: 768px-1023px (2-column, adjusted)
- **Mobile**: <768px (single column, full-width)

### Checkout Mobile Improvements

1. **Payment Buttons**: Stack vertically on mobile (100% width)
2. **Coupon Input**: Splits to two rows on mobile (input above button)
3. **Form Fields**: Proper touch sizing (min 44px height)
4. **Text**: Scales appropriately for readability
5. **Spacing**: Reduces from 30px to 20px on mobile

### Product Pages Mobile Improvements

1. **Grid**: 1 column on mobile, 2 on tablet/desktop
2. **Images**: Scale responsively, max-width: 100%
3. **Buttons**: Full-width on mobile for easier touch
4. **Text**: Adjusted font sizes for smaller screens
5. **Cart**: Converts to simple list on mobile

### Testing

**On Desktop Browser**:
- Open DevTools (F12)
- Toggle device toolbar (Ctrl+Shift+M)
- Test at: iPhone 12, iPad, Android phone sizes
- Verify all buttons clickable, text readable
- Check no horizontal scrolling

**On Real Devices**:
- Test on actual phone/tablet
- Try payment flow end-to-end
- Verify coupon code entry on mobile keyboard
- Check image loading on mobile network

---

## 🧪 TESTING CHECKLIST

### Admin Product Management

- [ ] Create new product with image
  - [ ] See image preview before upload
  - [ ] Live preview updates as you type
  - [ ] Discount badge appears when old price entered
  - [ ] Featured badge toggles
  - [ ] Product saves successfully

- [ ] Edit existing product
  - [ ] Current image displays
  - [ ] Can upload new image
  - [ ] Preview shows new image immediately
  - [ ] Form pre-fills with existing data
  - [ ] Changes save correctly

- [ ] Image validation
  - [ ] Try file >5MB → Error message
  - [ ] Try non-image file → Error message
  - [ ] Try valid PNG/JPG → Accepts
  - [ ] File size shows in preview

### Shopping Flow (Happy Path)

- [ ] Browse products on home page
  - [ ] Products display with images
  - [ ] Prices show correctly
  - [ ] Discounts calculate correctly (% shown)
  - [ ] Layout responsive on mobile

- [ ] Add products to cart
  - [ ] Quantity selector works
  - [ ] "Add to cart" button adds items
  - [ ] Cart count in header updates
  - [ ] Can add same product multiple times

- [ ] View cart
  - [ ] All items display
  - [ ] Quantities editable
  - [ ] Subtotal calculates correctly
  - [ ] Update cart recalculates
  - [ ] Clear cart empties it
  - [ ] Buttons work on mobile

- [ ] Checkout (no coupon)
  - [ ] Shipping form shows
  - [ ] Order summary shows all items
  - [ ] Total calculates correctly
  - [ ] Both payment methods available
  - [ ] Form validation works (empty fields rejected)

- [ ] Checkout with coupon
  - [ ] Can enter coupon code
  - [ ] Valid code shows green success message
  - [ ] Discount appears in summary
  - [ ] Final total updates
  - [ ] Invalid code shows red error
  - [ ] Discount clears after error

### Payment Flow: Paystack

- [ ] Paystack payment selection
  - [ ] Click Paystack radio button
  - [ ] Email field shows
  - [ ] Button text updates to "Continue to Paystack"

- [ ] Paystack checkout
  - [ ] Form validates (name/phone/city required)
  - [ ] Clicking pay redirects to Paystack
  - [ ] Paystack form loads
  - [ ] Can enter test card details
  - [ ] Payment completes

- [ ] Paystack callback
  - [ ] Redirects back to app after payment
  - [ ] Success message shows
  - [ ] Cart is cleared
  - [ ] Customer receives email
  - [ ] Admin receives email
  - [ ] Order appears in admin dashboard

- [ ] Paystack errors
  - [ ] Cancelled payment shows warning
  - [ ] Network error shows appropriate message
  - [ ] Can return to checkout and retry

### Payment Flow: Wallet

**Prerequisites**: Logged-in user with sufficient wallet balance

- [ ] Wallet payment option
  - [ ] Only shows when logged in
  - [ ] Shows current balance
  - [ ] Red warning if insufficient balance
  - [ ] Disabled if insufficient
  - [ ] Green checkmark if sufficient

- [ ] Wallet checkout
  - [ ] Click wallet radio button
  - [ ] Email field hidden
  - [ ] Button text updates to "Pay GH₵XXX with Wallet"
  - [ ] Form validates

- [ ] Wallet payment
  - [ ] Clicking pay completes transaction
  - [ ] Success message shows
  - [ ] Cart cleared
  - [ ] Customer email received
  - [ ] Admin email received
  - [ ] Wallet balance deducted
  - [ ] New balance shown in email

- [ ] Insufficient wallet
  - [ ] Shows red warning
  - [ ] Can't select wallet option
  - [ ] Can choose Paystack instead

### Responsive Design

**Tablet (768px)**:
- [ ] Checkout buttons don't wrap awkwardly
- [ ] Form fields full-width but readable
- [ ] Touch areas ≥44px
- [ ] Images scale properly

**Mobile (375px)**:
- [ ] No horizontal scrolling
- [ ] All buttons touchable (44px+ height)
- [ ] Form fields full-width
- [ ] Coupon input stacks vertically
- [ ] Payment options readable
- [ ] Keyboard doesn't cover form fields

---

## 🚀 DEPLOYMENT CHECKLIST

Before going live:

1. **Database**
   - [ ] Create `Coupon` table (if not exists)
   - [ ] Run migrations: `python -m flask db upgrade`
   - [ ] Add test coupons

2. **Environment Variables** (Set in .env and Vercel/hosting)
   ```
   PAYSTACK_PUBLIC_KEY=pk_test_...
   PAYSTACK_SECRET_KEY=sk_test_...
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=...
   MAIL_PASSWORD=...
   ADMIN_EMAIL=...
   ```

3. **File Uploads**
   - [ ] Verify S3 configuration (if using S3)
   - [ ] Or verify local fallback works
   - [ ] Test product image upload on staging

4. **Email Delivery**
   - [ ] Test email sending: `/admin/test-email`
   - [ ] Verify customer receives order confirmation
   - [ ] Verify admin receives order notification
   - [ ] Check spam folder

5. **Payment Gateway**
   - [ ] Switch Paystack to LIVE keys (not test)
   - [ ] Test full payment flow with real card/mobile money
   - [ ] Verify callbacks work

6. **Testing**
   - [ ] Run full test suite
   - [ ] Manual testing on staging
   - [ ] Test on real mobile devices
   - [ ] Test on slow network (Mobile 3G)

7. **Security**
   - [ ] HTTPS enabled
   - [ ] CSRF tokens present
   - [ ] No sensitive data in logs
   - [ ] Rate limiting configured (if needed)

---

## 📞 TROUBLESHOOTING

### Image not showing in product

**Symptoms**: Product image shows placeholder instead of actual image

**Fixes**:
1. Check image file exists and is accessible
2. Verify S3 bucket configuration (if using S3)
3. Check image path in database
4. Try re-uploading image
5. Check browser cache (Ctrl+Shift+Delete)

### Coupon not applying

**Symptoms**: Enter valid coupon but get error

**Fixes**:
1. Check coupon code exists in database
2. Verify coupon hasn't expired
3. Check coupon min_amount vs order total
4. Check coupon usage limits
5. Verify coupon is marked `active=True`

### Payment not processing

**Symptoms**: Click pay button, nothing happens

**Fixes**:
1. Check Paystack keys are set (production vs test)
2. Check network connectivity
3. Verify form validation (fill all required fields)
4. Check browser console for errors (F12)
5. Check server logs for exceptions

### Email not sending

**Symptoms**: Payment completes but customer doesn't receive email

**Fixes**:
1. Check MAIL_SERVER and credentials
2. Verify ADMIN_EMAIL is set
3. Check spam/promotions folder
4. Test with `/admin/test-email`
5. Check server logs for email errors
6. Verify email isn't being rate-limited

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| [app.py](app.py) | Backend routes and payment logic |
| [templates/admin_edit.html](templates/admin_edit.html) | Product form with previews |
| [templates/product.html](templates/product.html) | Product detail page |
| [templates/checkout.html](templates/checkout.html) | Checkout with payments |
| [templates/cart.html](templates/cart.html) | Shopping cart view |
| [templates/base.html](templates/base.html) | Base template (header, nav) |
| [static/js/settings-sync.js](static/js/settings-sync.js) | Real-time settings sync |

---

## 🎯 Next Steps (Future Enhancements)

- [ ] Wishlist feature
- [ ] Product reviews/ratings
- [ ] Multiple payment methods (Stripe, etc.)
- [ ] Inventory management
- [ ] Order tracking updates
- [ ] Customer account page
- [ ] Admin dashboard improvements
- [ ] Analytics and reporting

---

**Last Updated**: 2024  
**Status**: ✅ Ready for Deployment  
**Version**: 1.0
