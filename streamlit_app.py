
import streamlit as st
import sqlite3
import re
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="SUNMIT Travel",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = Path(__file__).parent / "bookings.db"

CITIES = [
    "Shirpur", "Pune", "Mumbai", "Nashik", "Dhule",
    "Indore", "Surat", "Ahmedabad", "Aurangabad", "Nagpur"
]

BUSES = {
    "SUNMIT Express · AC Seater": 650,
    "Royal Roadlines · Non-AC": 350,
    "BlueLine Travels · AC Sleeper": 950,
}

SEATS = [f"{row}{n}" for row in "ABCDEF" for n in range(1, 7)]


# ---------------- DATABASE ----------------
def get_db():
    con = sqlite3.connect(DB_PATH, timeout=10)

    con.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            gender TEXT DEFAULT 'Prefer not to say',
            bus TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            seats TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Confirmed'
        )
    """)

    existing = {
        row[1]
        for row in con.execute("PRAGMA table_info(bookings)").fetchall()
    }

    if "gender" not in existing:
        con.execute(
            "ALTER TABLE bookings ADD COLUMN gender TEXT DEFAULT 'Prefer not to say'"
        )

    if "status" not in existing:
        con.execute(
            "ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Confirmed'"
        )

    con.commit()
    return con


def get_bookings():
    con = get_db()
    rows = con.execute("""
        SELECT id, name, phone, gender, bus, source, destination,
               travel_date, seats, total, status
        FROM bookings
        ORDER BY id DESC
    """).fetchall()
    con.close()
    return rows


def booked_seats(bus, travel_date):
    con = get_db()
    rows = con.execute("""
        SELECT seats FROM bookings
        WHERE bus = ? AND travel_date = ? AND status = 'Confirmed'
    """, (bus, str(travel_date))).fetchall()
    con.close()

    result = set()
    for row in rows:
        result.update(s.strip() for s in row[0].split(","))
    return result


def money(amount):
    return f"₹{amount:,.0f}"


get_db().close()


# ---------------- PREMIUM MOBILE UI ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(145deg, #0b1220, #101a30 60%, #101c2e);
    color: #f7f9fc;
}
header[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 1180px;
    padding: 1.2rem 1rem 3rem;
}
h1, h2, h3, p, label {
    color: #f7f9fc;
}
.brand {
    font-size: 1.65rem;
    font-weight: 800;
    letter-spacing: -.7px;
}
.brand span {
    color: #38d9e6;
}
.eyebrow {
    color: #38d9e6;
    text-transform: uppercase;
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: 2px;
}
.hero {
    padding: 1.5rem;
    border: 1px solid #293952;
    border-radius: 24px;
    background: linear-gradient(120deg, #1a2b47, #152239 65%, #153345);
    margin: 1rem 0 1.4rem;
}
.hero h1 {
    font-size: clamp(1.7rem, 5vw, 2.8rem);
    line-height: 1.12;
    margin: .5rem 0;
}
.hero p, .muted {
    color: #bac6d9;
}
.metric-card {
    background: #17243b;
    border: 1px solid #293952;
    border-radius: 18px;
    padding: 1rem;
    min-height: 110px;
    margin-bottom: .5rem;
}
.metric-label {
    font-size: .82rem;
    color: #9aa8bd;
}
.metric-value {
    font-size: clamp(1.35rem, 4vw, 2rem);
    font-weight: 800;
    margin-top: .35rem;
}
.section-title {
    font-size: 1.2rem;
    font-weight: 800;
    margin: 1.2rem 0 .7rem;
}
.seat-note {
    color: #9aa8bd;
    font-size: .82rem;
}
div[data-testid="stForm"] {
    border: 1px solid #293952;
    border-radius: 18px;
    padding: 1rem;
}
.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px;
    min-height: 2.7rem;
    font-weight: 700;
    border: 1px solid #38d9e6;
}
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: #38d9e6;
    color: #071522;
}
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] textarea {
    border-radius: 10px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #293952;
    border-radius: 14px;
    overflow: hidden;
}
footer {
    visibility: hidden;
}
@media (max-width: 640px) {
    .block-container {
        padding: .7rem .65rem 2rem;
    }
    .hero {
        padding: 1.1rem;
        border-radius: 18px;
    }
    .brand {
        font-size: 1.4rem;
    }
    .metric-card {
        padding: .75rem;
        min-height: 95px;
    }
    div[data-testid="stForm"] {
        padding: .65rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER / NAVIGATION ----------------
st.markdown(
    '<div class="brand">🚌 SUNMIT <span>TRAVEL</span></div>'
    '<div style="color:#9aa8bd;font-size:.85rem;">'
    'MADE SIMPLE · YOUR JOURNEY, REIMAGINED</div>',
    unsafe_allow_html=True
)

page = st.radio(
    "Main navigation",
    ["Dashboard", "Book Ticket", "Bookings", "Reports"],
    horizontal=True,
    label_visibility="collapsed"
)

rows = get_bookings()
confirmed = [r for r in rows if r[10] == "Confirmed"]
revenue = sum(r[9] for r in confirmed)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">Travel smarter</div>
      <h1>Your next journey<br>starts here.</h1>
      <p>Choose your route, pick your seat and travel with SUNMIT.</p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)

    for col, label, value in [
        (a, "TOTAL BOOKINGS", str(len(rows))),
        (b, "CONFIRMED", str(len(confirmed))),
        (c, "TOTAL REVENUE", money(revenue)),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-title">Ready for your next trip?</div>',
        unsafe_allow_html=True
    )
    st.write("Select **Book Ticket** above to reserve a seat.")

    if rows:
        st.markdown("### Recent bookings")
        st.dataframe([
            {
                "ID": r[0],
                "Passenger": r[1],
                "Route": f"{r[5]} → {r[6]}",
                "Date": r[7],
                "Seats": r[8],
                "Amount": money(r[9]),
                "Status": r[10]
            }
            for r in rows[:5]
        ], use_container_width=True, hide_index=True)


# ---------------- BOOK TICKET ----------------
elif page == "Book Ticket":
    st.markdown('<div class="eyebrow">Reservation</div>',
                unsafe_allow_html=True)
    st.title("Book your ticket")
    st.caption("Enter your details and choose your preferred seats.")

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown("### 01 · Your journey")

        source = st.selectbox("Leaving from", CITIES, key="source")
        destinations = [c for c in CITIES if c != source]
        destination = st.selectbox("Going to", destinations, key="destination")
        travel_date = st.date_input(
            "Travel date", value=date.today(), min_value=date.today()
        )
        bus = st.selectbox("Choose your bus", list(BUSES.keys()))
        fare = BUSES[bus]

        st.markdown("### 02 · Passenger details")
        name = st.text_input("Full name", placeholder="Enter passenger name")
        phone = st.text_input(
            "Mobile number", placeholder="10-digit mobile number",
            max_chars=10
        )
        gender = st.selectbox(
            "Gender (optional)",
            ["Prefer not to say", "Male", "Female", "Other"]
        )

    unavailable = booked_seats(bus, travel_date)

    with right:
        st.markdown("### 03 · Select your seats")
        st.markdown(
            '<div class="seat-note">Select available seats. '
            'Disabled seats are already booked for this bus and date.</div>',
            unsafe_allow_html=True
        )

        selected = []

        for row_label in "ABCDEF":
            cols = st.columns(6)
            for number, col in enumerate(cols, start=1):
                seat = f"{row_label}{number}"
                with col:
                    if seat in unavailable:
                        st.button(
                            f"✕ {seat}", key=f"unavailable_{seat}",
                            disabled=True, use_container_width=True
                        )
                    else:
                        if st.checkbox(
                            seat,
                            key=f"seat_{bus}_{travel_date}_{seat}"
                        ):
                            selected.append(seat)

        st.caption("✕ = already booked · Tick a seat to select it.")

        total = fare * len(selected)
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">FARE PER SEAT</div>'
            f'<div class="metric-value">{money(fare)}</div>'
            f'<div class="metric-label">Seats: '
            f'{", ".join(selected) if selected else "None"}</div>'
            f'<hr style="border-color:#293952;">'
            f'<div class="metric-label">TOTAL FARE</div>'
            f'<div class="metric-value" style="color:#38d9e6;">'
            f'{money(total)}</div></div>',
            unsafe_allow_html=True
        )

    if st.button("Confirm booking →", type="primary",
                 use_container_width=True):
        if not re.fullmatch(r"[A-Za-z ]+", name.strip()):
            st.error("Enter a name using English letters and spaces only.")
        elif not re.fullmatch(r"[0-9]{10}", phone):
            st.error("Enter a valid 10-digit mobile number.")
        elif not selected:
            st.error("Please select at least one available seat.")
        else:
            con = get_db()
            try:
                # Recheck selected seats before saving.
                current = booked_seats(bus, travel_date)

                if any(s in current for s in selected):
                    st.error(
                        "A selected seat has just been booked. "
                        "Please refresh and choose another seat."
                    )
                else:
                    con.execute("""
                        INSERT INTO bookings
                        (name, phone, gender, bus, source, destination,
                         travel_date, seats, total, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
                    """, (
                        name.strip(), phone, gender, bus,
                        source, destination, str(travel_date),
                        ", ".join(selected), total
                    ))
                    con.commit()
                    st.success(
                        f"Booking confirmed! Seats: {', '.join(selected)} · "
                        f"Total: {money(total)}"
                    )
                    st.balloons()
            except sqlite3.Error as error:
                st.error(f"Could not save booking: {error}")
            finally:
                con.close()


# ---------------- BOOKING HISTORY ----------------
elif page == "Bookings":
    st.title("Your bookings")
    st.caption("View your booking history and manage reservations.")

    if not rows:
        st.info("No bookings yet. Go to Book Ticket to make your first booking.")
    else:
        st.dataframe([
            {
                "ID": r[0],
                "Passenger": r[1],
                "Mobile": r[2],
                "Bus": r[4],
                "Route": f"{r[5]} → {r[6]}",
                "Date": r[7],
                "Seats": r[8],
                "Total": money(r[9]),
                "Status": r[10]
            }
            for r in rows
        ], use_container_width=True, hide_index=True)

        active_ids = [r[0] for r in confirmed]

        if active_ids:
            st.markdown("### Cancel a booking")
            booking_id = st.selectbox("Booking ID", active_ids)

            if st.button("Cancel selected booking"):
                con = get_db()
                con.execute(
                    "UPDATE bookings SET status='Cancelled' WHERE id=?",
                    (booking_id,)
                )
                con.commit()
                con.close()
                st.success(f"Booking #{booking_id} cancelled.")
                st.rerun()


# ---------------- REPORTS ----------------
elif page == "Reports":
    st.title("Reports & insights")
    st.caption("Summary of confirmed bookings and revenue.")

    a, b = st.columns(2)
    a.metric("Confirmed revenue", money(revenue))
    b.metric(
        "Cancelled bookings",
        sum(1 for r in rows if r[10] == "Cancelled")
    )

    if confirmed:
        st.markdown("### Revenue by bus")
        bus_totals = {}
        for r in confirmed:
            bus_totals[r[4]] = bus_totals.get(r[4], 0) + r[9]
        st.bar_chart(bus_totals)

        st.markdown("### Bookings by route")
        route_totals = {}
        for r in confirmed:
            route = f"{r[5]} → {r[6]}"
            route_totals[route] = route_totals.get(route, 0) + 1
        st.bar_chart(route_totals)
    else:
        st.info("Reports will appear after your first confirmed booking.")


# ---------------- FOOTER ----------------
st.markdown("""
<div style="text-align:center;color:#8290a7;font-size:.78rem;padding:2rem 0 0;">
SUNMIT TRAVEL · MADE SIMPLE<br>
Demo booking system · No online payments
</div>
""", unsafe_allow_html=True)
