"""
movie_tools.py — LangChain Agent Tools for Movie Ticket Booking System
========================================================================
Defines tools for movie search, theater showtime recommendations, PNR ticket reservations,
payment processing, and booking status checks.
"""

from typing import Optional
from langchain_core.tools import tool
import booking_system.movie_service as movie_service


@tool
def search_movies_tool(city: str = "Delhi", movie_name: Optional[str] = None) -> str:
    """Search for currently showing movies in cinemas, theaters, IMAX screen formats, showtimes, and ticket prices.
    
    Args:
        city: City name (e.g., Delhi, Mumbai, Bengaluru, Goa).
        movie_name: (Optional) Movie title keyword e.g. "Avatar", "Pushpa 2", "Dune".
    """
    try:
        movies = movie_service.search_showing_movies(city=city, movie_query=movie_name)
        if not movies:
            return f"No movie showtimes found in {city}."
        
        lines = [f"**Now Showing in Cinemas ({city.capitalize()})**:\n"]
        for m in movies:
            lines.append(
                f"• **{m['movie_title']}** ({m['rating']} | {m['genre']})\n"
                f"  Cinema: {m['cinema_hall']} ({m['screen_type']})\n"
                f"  Showtimes: {m['showtimes']}\n"
                f"  Fare: ₹{m['price_per_ticket']:,} per ticket | Format: {m['language']}\n"
            )
        lines.append("*Tell me which movie & showtime you want to reserve tickets for!*")
        return "\n".join(lines)
    except Exception as err:
        return f"Error searching movies: {str(err)}"


@tool
def book_movie_tool(
    movie_title: str,
    customer_name: str,
    city: str = "Delhi",
    tickets_count: int = 2,
    show_date: str = "Today",
    preferred_time: str = "7:30 PM",
    screen_type: str = "IMAX 3D",
    user_id: str = "usr_guest"
) -> str:
    """Reserve movie tickets, assign cinema seats (e.g. Recliner E7, E8), generate a PNR code, and prompt for payment.
    
    Args:
        movie_title: Movie title e.g. "Avatar: Fire & Ash", "Pushpa 2".
        customer_name: Full name of person booking tickets.
        city: City name (default Delhi).
        tickets_count: Number of tickets (default 2).
        show_date: (Optional) Show date e.g. "Today", "Tomorrow", "2026-07-28".
        preferred_time: (Optional) Preferred showtime e.g. "7:30 PM", "9:45 PM".
        screen_type: (Optional) Screen format e.g. "IMAX 3D", "4DX", "Dolby 2D".
        user_id: Active user ID.
    """
    try:
        booking = movie_service.process_movie_reservation(
            movie_title=movie_title,
            customer_name=customer_name,
            city=city,
            tickets_count=tickets_count,
            show_date=show_date,
            preferred_time=preferred_time,
            screen_type=screen_type,
            user_id=user_id
        )
        
        pnr = booking["pnr"]
        total_price = booking["total_price_inr"]
        payment_link = booking["payment_url"]
        
        res = (
            f"**MOVIE TICKETS RESERVED SUCCESSFULLY**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**Cinema PNR Code**: `{pnr}`\n"
            f"**Movie**: {booking['movie_title']}\n"
            f"**Theater**: {booking['cinema_hall']}\n"
            f"**Format**: {booking['screen_type']}\n"
            f"**Show Date & Time**: {show_date} @ {preferred_time}\n"
            f"**Assigned Seats**: `{booking['seats']}` ({booking['tickets_count']} Ticket(s))\n"
            f"**Customer**: {customer_name}\n"
            f"**Total Fare**: ₹{total_price:,} INR\n"
            f"**Status**: `PENDING PAYMENT`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**PAYMENT INSTRUCTIONS**:\n"
            f"• Quick Link: {payment_link}\n"
            f"• Or simply tell me: *'Pay ₹{total_price:,} for Movie PNR {pnr} using UPI'* to get your digital e-tickets now!"
        )
        return res
    except Exception as err:
        return f"Movie ticket reservation failed: {str(err)}"


@tool
def check_movie_booking_tool(pnr: str, user_id: str = "usr_guest") -> str:
    """Lookup an existing cinema ticket reservation status using its PNR code.
    
    Args:
        pnr: The movie ticket PNR code (e.g., PNR-MOV392810).
        user_id: Active user ID.
    """
    try:
        booking = movie_service.get_movie_booking_by_pnr(pnr)
        if not booking:
            return f"No movie booking found for PNR: '{pnr}'."
        
        return (
            f"**MOVIE TICKET STATUS FOR `{booking['pnr']}`**:\n"
            f"• Movie: {booking['movie_title']}\n"
            f"• Theater: {booking['cinema_hall']} ({booking['screen_type']})\n"
            f"• Showtime: {booking['show_date']} @ {booking['show_time']}\n"
            f"• Seats: {booking['seats']} ({booking['tickets_count']} Ticket(s))\n"
            f"• Customer: {booking['customer_name']}\n"
            f"• Total Fare: ₹{booking['total_price_inr']:,} INR\n"
            f"• Payment Status: **{booking['payment_status']}**"
        )
    except Exception as err:
        return f"Error checking movie booking: {str(err)}"


@tool
def pay_movie_booking_tool(pnr: str, payment_method: str = "UPI", user_id: str = "usr_guest") -> str:
    """Confirm payment for a pending movie ticket reservation PNR code.
    
    Args:
        pnr: The movie ticket PNR code (e.g., PNR-MOV392810).
        payment_method: Payment mode e.g. "UPI", "Credit Card", "Net Banking".
        user_id: Active user ID.
    """
    try:
        booking = movie_service.get_movie_booking_by_pnr(pnr)
        if not booking:
            return f"Cannot process payment. No movie booking found for PNR: '{pnr}'."
        
        updated = movie_service.update_movie_payment_status(pnr, new_status="PAID")
        
        return (
            f"**CINEMA E-TICKET CONFIRMED & ISSUED**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 **Cinema PNR**: `{updated['pnr']}`\n"
            f"🎬 **Movie**: {updated['movie_title']}\n"
            f"🏛️ **Theater**: {updated['cinema_hall']}\n"
            f"💺 **Seats**: `{updated['seats']}`\n"
            f"💳 **Payment Method**: {payment_method} (Status: `PAID`)\n"
            f"💰 **Amount Paid**: ₹{updated['total_price_inr']:,} INR\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🍿 Show your digital e-ticket QR at the cinema entrance. Enjoy the movie!"
        )
    except Exception as err:
        return f"Payment confirmation error: {str(err)}"


MOVIE_TOOLS = [search_movies_tool, book_movie_tool, check_movie_booking_tool, pay_movie_booking_tool]
