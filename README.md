# Zoomzy Cars
https://zoomzycars.com/

Zoomzy Cars is an online store for RC (remote-controlled) cars and related collectables, covering categories such as drift cars, monster trucks, off-road and on-road vehicles, FPV RC cars, and collectable models. Customers can browse the catalog, view products, and purchase them for delivery.

---

## Overview

Zoomzy Cars operates as an e-commerce storefront built around a hobbyist product category: RC cars and accessories. The site combines category-based browsing, product pages, account management, and supporting content (blog, gallery, FAQ) to guide customers from discovery to purchase.

The platform serves one primary type of user:

- **Customers**, who browse RC car categories, manage a cart, wishlist, and account, and place orders for delivery.

An underlying admin/catalog layer (not customer-facing) maintains product listings, categories, pricing, and stock.

---

## How the Platform Works

### 1. Browsing and Discovery

1. A visitor lands on the homepage, which opens with a promotional banner and a "Shop by Category" section covering all six product categories: Collectables, Drift Cars, FPV RC Cars, Monster Truck, Off Road, and On Road.
2. Below the categories, a "New Arrivals" section highlights recently added products, giving returning visitors a quick way to see what's new.
3. From the top navigation, a visitor can jump directly into any category through the Categories dropdown, or browse the complete catalog through the Shop page.

### 2. Product Selection

1. Clicking a product from the category grid or New Arrivals section opens its individual product page with full details.
2. Header icons give quick access to core actions from any page: Cart, Profile, Wishlist, and Search.
3. Adding a product to the cart or wishlist requires the customer to be logged in; both icons route to the login page if the customer is not yet signed in.

### 3. Account and Checkout

1. New customers register and log in through the account system, which also grants access to Wishlist and Cart functionality.
2. The Profile page lets customers manage their account and view order-related information.
3. From the Cart, the customer proceeds through checkout to complete the purchase.
4. Delivery, cancellation, and refund terms are available at any point through the footer policy links (Terms & Conditions, Return & Refund Policy, Privacy & Security Policy).

### 4. Engagement and Trust Building

1. The Gallery page showcases a mix of customer and product videos and images, giving visitors a feel for the RC cars in action before purchase.
2. The Blogs section publishes hobbyist content, such as racing tips, guides to RC car components, and challenge ideas to try with friends, supporting both customer education and organic discovery of the site.
3. A newsletter subscription in the footer lets visitors opt in for updates on new products and deals.

### 5. Support

1. Customers with questions can reach the team through the Contact Us page or directly via WhatsApp, linked site-wide.
2. The FAQ page answers common questions without requiring direct contact.
3. The About Us page provides background on the brand for visitors evaluating the store's credibility.

---

## Core Features

- Product catalog organized into six categories, with dedicated category pages.
- Homepage sections for category browsing and new arrivals.
- Individual product pages with full product details.
- Cart and wishlist functionality tied to customer accounts.
- Customer account system with login, registration, and profile management.
- Gallery page featuring product videos and images.
- Blog section for hobbyist guides and racing content.
- Newsletter subscription for product updates and deals.
- FAQ, Terms & Conditions, Privacy & Security Policy, and Return & Refund Policy pages.
- Direct contact via a contact page and WhatsApp integration.
- Responsive design for both desktop and mobile browsing.

---

## Technology Stack

The site is server-rendered with a template-based architecture and is confirmed to run on a Python/Django backend (visible from the `/media/` and `/static/` directory structure, and an internal link resolving to a local Django development server).

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, CSS, JavaScript |
| Media | Product images, category images, and videos served from a dedicated media directory |

---
