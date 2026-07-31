"""
hotel_tools.py — LangChain Agent Tools for Hotel Booking System
================================================================
Defines tools for hotel search, deluxe room reservations with PNR,
payment processing, and reservation status checks.
"""

from typing import Optional
from langchain_core.tools import tool
import booking_system.hotel_service as hotel_service


@tool
def search_hotels_tool(city: str, sort_by: str = "default", check_in: str = "Tomorrow", nights: int = 1) -> str:
    """Search for available hotels in a city/destination with options for cheapest, budget, or luxury sorting.
    
    Args:
        city: City or destination name (e.g., Delhi, Goa, Mumbai, Jaipur, Bengaluru).
        sort_by: Sorting mode e.g. "cheapest", "budget", "luxury", or "default".
        check_in: Check-in date or phrase (e.g., "Tomorrow", "2026-08-01").
        nights: Number of nights stay (default 1).
    """
    try:
        hotels = hotel_service.search_available_hotels(city, sort_by=sort_by, check_in=check_in, nights=nights)
        if not hotels:
            return f"No hotel recommendations found for {city}."
        
        is_cheap = any(k in sort_by.lower() for k in ["cheap", "budget", "price"])
        header_title = f"Cheapest & Best Value Hotels in {city.capitalize()}" if is_cheap else f"Top Hotel Recommendations in {city.capitalize()}"
        lines = [f"🏨 **{header_title} ({nights} night(s), Check-in: {check_in})**:\n"]
        for h in hotels:
            amenities_str = ", ".join(h['amenities'])
            lines.append(
                f"• **{h['name']}** ({h['rating']})\n"
                f"  📍 Location: {h['location']}\n"
                f"  🛏️ Room: {h['room_type']}\n"
                f"  💰 Fare: ₹{h['price_per_night']:,} / night (Total: ₹{h['total_price_inr']:,} INR)\n"
                f"  ✨ Amenities: {amenities_str}\n"
            )
        lines.append("💡 *Tell me if you want me to book any of these hotels for you right now!*")
        return "\n".join(lines)
    except Exception as err:
        return f"Error searching hotels: {str(err)}"


@tool
def book_hotel_tool(
    city: str,
    guest_name: str,
    hotel_name: Optional[str] = None,
    check_in: str = "Tomorrow",
    check_out: str = "Day after tomorrow",
    guests_count: int = 2,
    nights_count: int = 1,
    user_id: str = "usr_guest"
) -> str:
    """Reserve a hotel room, generate a unique PNR code, and issue payment instructions.
    
    Args:
        city: Destination city (e.g., Goa, Mumbai, Jaipur).
        guest_name: Primary guest full name.
        hotel_name: (Optional) Specific hotel name e.g. "Taj Holiday Village" or "The Leela Palace".
        check_in: (Optional) Check-in date string e.g. "2026-08-01".
        check_out: (Optional) Check-out date string e.g. "2026-08-03".
        guests_count: Number of guests (default 2).
        nights_count: Number of nights (default 1).
        user_id: Active user ID.
    """
    try:
        booking = hotel_service.process_hotel_reservation(
            city=city,
            guest_name=guest_name,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            nights_count=nights_count,
            hotel_name=hotel_name,
            user_id=user_id
        )
        
        pnr = booking["pnr"]
        total_price = booking["total_price_inr"]
        payment_link = booking["payment_url"]
        
        res = (
            f"🎉 **HOTEL ROOM RESERVED SUCCESSFULLY!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 **Hotel PNR Code**: `{pnr}`\n"
            f"👤 **Primary Guest**: {guest_name} ({guests_count} Guests)\n"
            f"🏨 **Hotel**: {booking['hotel_name']}\n"
            f"🛏️ **Room Type**: {booking['room_type']}\n"
            f"📍 **City**: {booking['city']}\n"
            f"📅 **Stay Period**: {check_in} ➔ {check_out} ({booking['nights_count']} Night(s))\n"
            f"✨ **Included**: {booking['amenities']}\n"
            f"💰 **Total Fare**: ₹{total_price:,} INR\n"
            f"⏳ **Status**: `PENDING PAYMENT`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 **PAYMENT INSTRUCTIONS**:\n"
            f"• Quick Link: {payment_link}\n"
            f"• Or simply tell me: *'Pay ₹{total_price:,} for Hotel PNR {pnr} using UPI'* to confirm your room now!"
        )
        return res
    except Exception as err:
        return f"Hotel reservation failed: {str(err)}"


@tool
def check_hotel_booking_tool(pnr: str, user_id: str = "usr_guest") -> str:
    """Lookup an existing hotel room reservation status using its PNR code.
    
    Args:
        pnr: The hotel reservation PNR code (e.g., PNR-HTL849201).
        user_id: Active user ID.
    """
    try:
        booking = hotel_service.get_hotel_booking_by_pnr(pnr)
        if not booking:
            return f"No hotel reservation found for PNR: '{pnr}'."
        
        return (
            f"📌 **HOTEL RESERVATION STATUS FOR `{booking['pnr']}`**:\n"
            f"• Guest: {booking['guest_name']} ({booking['guests_count']} Guests)\n"
            f"• Hotel: {booking['hotel_name']}\n"
            f"• Room: {booking['room_type']}\n"
            f"• Dates: {booking['check_in']} to {booking['check_out']}\n"
            f"• Total Fare: ₹{booking['total_price_inr']:,} INR\n"
            f"• Payment Status: **{booking['payment_status']}**"
        )
    except Exception as err:
        return f"Error checking hotel booking: {str(err)}"


@tool
def pay_hotel_booking_tool(pnr: str, payment_method: str = "UPI", user_id: str = "usr_guest") -> str:
    """Confirm payment for a pending hotel room reservation PNR code.
    
    Args:
        pnr: The hotel reservation PNR code (e.g., PNR-HTL849201).
        payment_method: Payment mode e.g. "UPI", "Credit Card", "Net Banking".
        user_id: Active user ID.
    """
    try:
        booking = hotel_service.get_hotel_booking_by_pnr(pnr)
        if not booking:
            return f"Cannot process payment. No hotel reservation found for PNR: '{pnr}'."
        
        updated = hotel_service.update_hotel_payment_status(pnr, new_status="PAID")
        
        return (
            f"✅ **HOTEL PAYMENT CONFIRMED & ROOM BOOKED!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 **Hotel PNR**: `{updated['pnr']}`\n"
            f"👤 **Guest**: {updated['guest_name']}\n"
            f"🏨 **Hotel**: {updated['hotel_name']}\n"
            f"🛏️ **Room**: {updated['room_type']}\n"
            f"💳 **Payment Method**: {payment_method} (Status: `PAID`)\n"
            f"💰 **Amount Paid**: ₹{updated['total_price_inr']:,} INR\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏨 Your e-voucher has been generated! Check-in instructions sent."
        )
    except Exception as err:
        return f"Payment confirmation error: {str(err)}"


HOTEL_TOOLS = [search_hotels_tool, book_hotel_tool, check_hotel_booking_tool, pay_hotel_booking_tool]
