"""
booking_tools.py — LangChain Agent Tools for Flight Ticket Booking System
==========================================================================
Defines tools for flight search, ticket reservation with PNR, payment requests,
and booking status checks.
"""

from typing import Optional
from langchain_core.tools import tool
import booking_system.flight_service as flight_service
import booking_system.booking_db as booking_db


@tool
def search_flights_tool(origin: str, destination: str, travel_date: str) -> str:
    """Search for available flights between origin and destination for a specified travel date.
    
    Args:
        origin: Departure city or airport code (e.g., Delhi, Mumbai, BLR).
        destination: Arrival city or airport code (e.g., Mumbai, Goa, DEL).
        travel_date: Date of travel (e.g., "2026-07-26", "tomorrow", "next Monday").
    """
    try:
        flights = flight_service.search_available_flights(origin, destination, travel_date)
        if not flights:
            return f"No flights found from {origin} to {destination} on {travel_date}."
        
        lines = [f"**Available Flights ({origin} -> {destination}) on {travel_date}**:\n"]
        for f in flights:
            lines.append(
                f"• **{f['airline']} ({f['flight_number']})**\n"
                f"  Departure: {f['departure_time']} | Arrival: {f['arrival_time']} ({f['duration']})\n"
                f"  Price: ₹{f['price_inr']:,} per person | Seats Left: {f['seats_available']}\n"
            )
        lines.append("*Tell me which flight or departure time you prefer to reserve your ticket!*")
        return "\n".join(lines)
    except Exception as err:
        return f"Error searching flights: {str(err)}"


@tool
def book_flight_tool(
    origin: str,
    destination: str,
    travel_date: str,
    passenger_name: str,
    flight_number: Optional[str] = None,
    preferred_time: Optional[str] = None,
    user_id: str = "usr_guest"
) -> str:
    """Reserve a flight ticket from origin to destination, create a PNR record, and prompt for payment.
    
    Args:
        origin: Departure city or airport (e.g., Delhi).
        destination: Destination city or airport (e.g., Mumbai).
        travel_date: Date of travel (e.g., "2026-07-26").
        passenger_name: Full name of the passenger traveling.
        flight_number: (Optional) Specific flight code e.g. "6E-204" or "AI-301".
        preferred_time: (Optional) Preferred departure window e.g. "Morning", "10:30 AM".
        user_id: Active user ID.
    """
    try:
        booking = flight_service.process_flight_reservation(
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            passenger_name=passenger_name,
            flight_number=flight_number,
            preferred_time=preferred_time,
            user_id=user_id
        )
        
        pnr = booking["pnr"]
        price = booking["price_inr"]
        payment_link = booking["payment_url"]
        
        res = (
            f"**FLIGHT TICKET RESERVED SUCCESSFULLY**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**PNR Code**: `{pnr}`\n"
            f"**Passenger**: {passenger_name}\n"
            f"**Flight**: {booking['airline']} ({booking['flight_number']})\n"
            f"**Route**: {booking['origin']} -> {booking['destination']}\n"
            f"**Date & Time**: {travel_date} @ {booking['departure_time']}\n"
            f"**Total Fare**: ₹{price:,} INR\n"
            f"**Status**: `PENDING PAYMENT`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**PAYMENT INSTRUCTIONS**:\n"
            f"Please complete payment to issue your e-ticket.\n"
            f"• Quick Link: {payment_link}\n"
            f"• Or simply tell me: *'Pay ₹{price:,} for PNR {pnr} using UPI'* to complete payment now!"
        )
        return res
    except Exception as err:
        return f"Flight reservation failed: {str(err)}"


@tool
def check_flight_booking_tool(pnr: str, user_id: str = "usr_guest") -> str:
    """Lookup an existing flight reservation status using its PNR code.
    
    Args:
        pnr: The 6-character PNR code (e.g., "PNR-BOB9812").
        user_id: Active user ID.
    """
    try:
        booking = booking_db.get_booking_by_pnr(pnr)
        if not booking:
            return f"No flight reservation found for PNR code `{pnr}`."
        if booking.get("user_id") != user_id:
            return f"No flight reservation found for PNR code `{pnr}`."

        status_text = "CONFIRMED & ISSUED" if booking["payment_status"] == "PAID" else "PENDING PAYMENT"
        return (
            f"**Booking Details for PNR**: `{booking['pnr']}`\n"
            f"• Passenger: {booking['passenger_name']}\n"
            f"• Flight: {booking['airline']} ({booking['flight_number']})\n"
            f"• Route: {booking['origin']} -> {booking['destination']}\n"
            f"• Date: {booking['travel_date']} at {booking['departure_time']}\n"
            f"• Amount: ₹{booking['price_inr']:,}\n"
            f"• Status: {status_text}"
        )
    except Exception as err:
        return f"Error checking booking: {str(err)}"


@tool
def pay_flight_booking_tool(pnr: str, payment_method: str = "UPI", user_id: str = "usr_guest") -> str:
    """Process payment for a reserved flight ticket PNR and issue confirmed ticket.
    
    Args:
        pnr: The PNR code to pay for (e.g., "PNR-BOB9812").
        payment_method: Payment mode (e.g., "UPI", "Credit Card", "NetBanking").
        user_id: Active user ID.
    """
    try:
        existing = booking_db.get_booking_by_pnr(pnr)
        if not existing or existing.get("user_id") != user_id:
            return f"No flight reservation found for PNR code `{pnr}`."
        updated = flight_service.complete_booking_payment(pnr, payment_method=payment_method)
        return (
            f"**PAYMENT SUCCESSFUL! E-TICKET CONFIRMED**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**PNR Code**: `{updated['pnr']}`\n"
            f"**Passenger**: {updated['passenger_name']}\n"
            f"**Flight**: {updated['airline']} ({updated['flight_number']})\n"
            f"**Route**: {updated['origin']} -> {updated['destination']}\n"
            f"**Departure**: {updated['travel_date']} @ {updated['departure_time']}\n"
            f"**Payment Method**: {payment_method}\n"
            f"**Ticket Status**: `CONFIRMED (PAID)`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Your boarding pass will be delivered to your registered email!"
        )
    except Exception as err:
        return f"Payment processing error: {str(err)}"


BOOKING_TOOLS = [
    search_flights_tool,
    book_flight_tool,
    check_flight_booking_tool,
    pay_flight_booking_tool,
]
