"""
Manual Price History Backfill Script

Run this ONCE after updating your scheduler to get initial price data.
This will scrape current Amazon prices for all existing products.

Usage:
    python backfill_prices.py
"""

from database import SessionLocal
from models import Product, PriceHistory
from scraper import get_amazon_price
from datetime import datetime, timezone
import time

def backfill_price_history():
    """Scrape current prices for all existing products"""
    db = SessionLocal()
    
    try:
        # Get all products
        products = db.query(Product).all()
        
        if not products:
            print("❌ No products found in database")
            return
        
        print(f"📊 Found {len(products)} products to scrape")
        print("🔍 Starting Amazon scraping...\n")
        
        success_count = 0
        failed_count = 0
        
        for i, product in enumerate(products, 1):
            try:
                print(f"[{i}/{len(products)}] Scraping: {product.name[:60]}...")
                
                # Scrape Amazon
                data = get_amazon_price(product.url)
                
                if data:
                    new_price = float(data["price"])
                    
                    # Save to price history
                    history_entry = PriceHistory(
                        product_id=product.id,
                        price=new_price,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(history_entry)
                    
                    # Update product current price
                    product.price = new_price
                    
                    db.commit()
                    
                    print(f"✅ Price: ₹{new_price} - Saved to history\n")
                    success_count += 1
                else:
                    print(f"❌ Failed to scrape Amazon\n")
                    failed_count += 1
                
                # Wait 2 seconds between requests to avoid Amazon blocking
                if i < len(products):
                    time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error: {e}\n")
                failed_count += 1
                db.rollback()
        
        print("\n" + "="*60)
        print(f"✅ Backfill complete!")
        print(f"📊 Success: {success_count}/{len(products)}")
        print(f"❌ Failed: {failed_count}/{len(products)}")
        print("="*60)
        
        if success_count > 0:
            print("\n🎉 Price history initialized!")
            print("📈 Charts will now show data")
            print("⏰ Scheduler will continue building history every hour")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("🔄 PRICE HISTORY BACKFILL SCRIPT")
    print("="*60)
    print("\nThis will scrape current Amazon prices for all products")
    print("and create initial price history data.\n")
    
    confirm = input("Continue? (y/n): ")
    
    if confirm.lower() == 'y':
        print("\n🚀 Starting backfill...\n")
        backfill_price_history()
    else:
        print("❌ Cancelled")