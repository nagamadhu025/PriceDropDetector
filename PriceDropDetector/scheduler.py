from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Product, User, PriceHistory
from scraper import get_amazon_price
from email_service import send_email
from datetime import datetime, timedelta, timezone

PRICE_DROP_THRESHOLD = 100


def check_prices(product_id=None):
    """
    Scrape Amazon prices and build price history.
    Runs automatically every hour to track price changes over time.
    """
    db = SessionLocal()
    
    try:
        # Get products to check
        if product_id:
            products = [db.query(Product).filter(Product.id == product_id).first()]
        else:
            # Check all subscribed products
            products = db.query(Product).filter(Product.subscribed == True).all()

        for product in products:
            if not product:
                continue
                
            try:
                print(f"🔍 Scraping price for: {product.name[:50]}...")
                
                # ⭐ SCRAPE AMAZON for current price
                data = get_amazon_price(product.url)
                
                if not data:
                    print(f"❌ Failed to scrape: {product.name[:50]}")
                    continue

                new_price = float(data["price"])
                old_price = product.price
                now = datetime.now(timezone.utc)

                print(f"💰 Price found: ₹{new_price} (was ₹{old_price})")

                # ⭐ SAVE TO PRICE HISTORY (builds chart data over time)
                history_entry = PriceHistory(
                    product_id=product.id,
                    price=new_price,
                    timestamp=now
                )
                db.add(history_entry)
                print(f"✅ Price history saved for product {product.id}")

                # Update current price in product
                product.price = new_price

                # Get user for email alerts
                user = db.query(User).filter(User.id == product.user_id).first()
                if not user:
                    continue

                # ⭐ ALERT 1: Significant price drop (₹100+)
                if old_price and (old_price - new_price) >= PRICE_DROP_THRESHOLD:
                    print(f"📧 Sending price drop alert (₹{old_price - new_price} drop)")
                    send_email(
                        user.email,
                        product.name,
                        old_price,
                        new_price
                    )
                    product.last_alerted = now

                # ⭐ ALERT 2: Target price reached
                elif product.target_price and new_price <= product.target_price:
                    # Only send if not alerted in last 24 hours
                    if product.last_alerted is None or (now - product.last_alerted) >= timedelta(hours=24):
                        print(f"🎯 Target price reached! Sending alert...")
                        send_email(
                            user.email,
                            product.name,
                            old_price,
                            new_price
                        )
                        product.last_alerted = now

                db.commit()
                print(f"✅ Product {product.id} updated successfully\n")

            except Exception as e:
                print(f"❌ Error checking product {product.id}: {e}")
                db.rollback()

    except Exception as e:
        print(f"❌ Error in check_prices: {e}")
        db.rollback()
    finally:
        db.close()


def cleanup_old_history():
    """
    Clean up old price history records (keep last 90 days).
    Runs once daily to prevent database bloat.
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        deleted = db.query(PriceHistory).filter(
            PriceHistory.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        print(f"🧹 Cleaned up {deleted} old price history records")
        
    except Exception as e:
        print(f"❌ Error cleaning up history: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """
    Start the background price checking scheduler.
    - Scrapes Amazon prices every hour
    - Builds price history for charts
    - Sends email alerts when prices drop
    """
    scheduler = BackgroundScheduler()

    # ⭐ Check prices every HOUR (scrape Amazon and build history)
    scheduler.add_job(
        check_prices,
        "interval",
        hours=1,  # Every hour
        id="price_check_hourly"
    )
    
    # For testing: uncomment to check every 5 minutes
    # scheduler.add_job(
    #     check_prices,
    #     "interval",
    #     minutes=5,
    #     id="price_check_testing"
    # )

    # Clean up old history daily at 3 AM
    scheduler.add_job(
        cleanup_old_history,
        "cron",
        hour=3,
        minute=0,
        id="cleanup_history_daily"
    )

    scheduler.start()
    print("✅ Scheduler started!")
    print("📊 Scraping Amazon prices every hour to build price history")
    print("🧹 Cleaning up old records daily at 3 AM")


# For manual testing
if __name__ == "__main__":
    print("🧪 Running manual price check...")
    check_prices()
    print("✅ Manual check complete!")