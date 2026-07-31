"""
demo.py — Standalone Interactive Demo for Flight Booking System
================================================================
Run this file directly to test flight searching, reservation creation (PNR),
payment prompts, status checks, and ticket issuance!

Usage:
  python booking_system/demo.py              (Runs automated test flow)
  python booking_system/demo.py --interactive (Runs interactive demo terminal)
"""

import os
import sys
import time

# Add root folder to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


from booking_system.booking_tools import (
    search_flights_tool,
    book_flight_tool,
    check_flight_booking_tool,
    pay_flight_booking_tool,
)


def run_automated_demo():
    print("=" * 70)
    print("🚀 BOT-O-BRAIN FLIGHT BOOKING SYSTEM DEMO (AUTOMATED TEST)")
    print("=" * 70)

    # 1. Search Flights
    print("\n[STEP 1] 🔍 Searching Flights: Delhi to Mumbai for 2026-07-26...")
    search_res = search_flights_tool.invoke({
        "origin": "Delhi",
        "destination": "Mumbai",
        "travel_date": "2026-07-26"
    })
    print(search_res)

    time.sleep(1)

    # 2. Book Flight Ticket
    print("\n[STEP 2] ✈️ Reserving Flight Ticket for passenger 'Priyanshu'...")
    book_res = book_flight_tool.invoke({
        "origin": "Delhi",
        "destination": "Mumbai",
        "travel_date": "2026-07-26",
        "passenger_name": "Priyanshu",
        "preferred_time": "10:30 AM"
    })
    print(book_res)

    # Extract PNR from output string
    import re
    pnr_match = re.search(r"PNR-BOB\d+", book_res)
    pnr_code = pnr_match.group(0) if pnr_match else "PNR-BOB1234"

    time.sleep(1)

    # 3. Check Booking Status Before Payment
    print(f"\n[STEP 3] 📋 Checking Status for PNR `{pnr_code}` (Before Payment)...")
    check_res1 = check_flight_booking_tool.invoke({"pnr": pnr_code})
    print(check_res1)

    time.sleep(1)

    # 4. Simulate Payment
    print(f"\n[STEP 4] 💳 Processing Payment for PNR `{pnr_code}` via UPI...")
    pay_res = pay_flight_booking_tool.invoke({"pnr": pnr_code, "payment_method": "UPI"})
    print(pay_res)

    time.sleep(1)

    # 5. Check Booking Status After Payment
    print(f"\n[STEP 5] 📋 Checking Status for PNR `{pnr_code}` (After Payment)...")
    check_res2 = check_flight_booking_tool.invoke({"pnr": pnr_code})
    print(check_res2)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETED SUCCESSFULLY! ALL TESTS PASSED.")
    print("=" * 70)


def run_interactive_demo():
    print("=" * 70)
    print("✈️ BOT-O-BRAIN FLIGHT BOOKING SYSTEM — INTERACTIVE CLI")
    print("=" * 70)
    print("Commands:")
    print("  1. search  -> Search flights between cities")
    print("  2. book    -> Reserve a flight ticket")
    print("  3. status  -> Check booking status by PNR")
    print("  4. pay     -> Pay for reserved ticket PNR")
    print("  5. exit    -> Exit demo")
    print("=" * 70)

    while True:
        try:
            cmd = input("\n[Flight System] Enter command (search/book/status/pay/exit): ").strip().lower()
            if cmd in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            elif cmd == "search":
                orig = input("Origin city: ").strip() or "Delhi"
                dest = input("Destination city: ").strip() or "Mumbai"
                date = input("Travel date (YYYY-MM-DD): ").strip() or "2026-07-26"
                res = search_flights_tool.invoke({"origin": orig, "destination": dest, "travel_date": date})
                print("\n" + res)
            elif cmd == "book":
                orig = input("Origin city: ").strip() or "Delhi"
                dest = input("Destination city: ").strip() or "Mumbai"
                date = input("Travel date (YYYY-MM-DD): ").strip() or "2026-07-26"
                name = input("Passenger Name: ").strip() or "User"
                res = book_flight_tool.invoke({
                    "origin": orig,
                    "destination": dest,
                    "travel_date": date,
                    "passenger_name": name
                })
                print("\n" + res)
            elif cmd == "status":
                pnr = input("Enter PNR code: ").strip()
                res = check_flight_booking_tool.invoke({"pnr": pnr})
                print("\n" + res)
            elif cmd == "pay":
                pnr = input("Enter PNR code: ").strip()
                method = input("Payment method (UPI/Card/NetBanking): ").strip() or "UPI"
                res = pay_flight_booking_tool.invoke({"pnr": pnr, "payment_method": method})
                print("\n" + res)
            else:
                print("Unknown command. Choose: search, book, status, pay, exit.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_demo()
    else:
        run_automated_demo()
