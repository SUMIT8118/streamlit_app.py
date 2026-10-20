import streamlit as st
import sqlite3
import re
from pathlib import Path

st.set_page_config(
    page_title="SUNMIT Travel",
    page_icon="🚌",
    layout="wide"
)

DB = Path(__file__).parent / "bookings.db"

CITIES = [
    "Shirpur", "Pune", "Mumbai", "Nashik",
    "Dhule", "Indore", "Surat", "Ahmedabad"
]

BUSES = {
    "SUNMIT Express": 450,
    "SUNMIT Premium": 700,
    "SUNMIT Sleeper": 950
}

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            bus TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            seats TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)
    con.commit()
    con.close()

init_db()

st.title("🚌 SUNMIT Travel")
st.caption("Made Simple | Bus Ticket Booking")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Book Ticket", "Bookings"]
)

if page == "Dashboard":
    con = sqlite3.connect(DB)
    count, revenue = con.execute(
        "SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bookings"
    ).fetchone()
    con.close()

    a, b = st.columns(2)
    a.metric("Total Bookings", count)
    b.metric("Total Revenue", f"₹{revenue:,.0f}")

    st.subheader("Welcome to SUNMIT Travel")
    st.write("Your journey, made simple!")

elif page == "Book Ticket":
    st.subheader("Book Your Ticket")

    with st.form("booking_form"):
        name = st.text_input("Passenger Name")
        phone = st.text_input("Mobile Number", max_chars=10)
        source = st.selectbox("From", CITIES)
        destination = st.selectbox(
            "To", [c for c in CITIES if c != source]
        )
        travel_date = st.date_input("Travel Date")
        bus = st.selectbox("Select Bus", list(BUSES.keys()))
        seats = st.multiselect(
            "Select Seats",
            [f"{r}{n}" for r in "ABCDE" for n in range(1, 9)]
        )

        total = BUSES[bus] * len(seats)
        st.write(f"Fare per seat: ₹{BUSES[bus]}")
        st.write(f"Total fare: ₹{total}")

        submitted = st.form_submit_button("Book Ticket")

    if submitted:
        if not re.fullmatch(r"[A-Za-z ]+", name.strip()):
            st.error("Name mein sirf English letters aur spaces use karo.")
        elif not re.fullmatch(r"[0-9]{10}", phone):
            st.error("Mobile number exactly 10 digits ka hona chahiye.")
        elif not seats:
            st.error("Kam se kam ek seat select karo.")
        else:
            con = sqlite3.connect(DB)
            con.execute("""
                INSERT INTO bookings
                (name, phone, bus, source, destination,
                 travel_date, seats, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name.strip(), phone, bus, source,
                destination, str(travel_date),
                ", ".join(seats), total
            ))
            con.commit()
            con.close()
            st.success("Ticket booking saved successfully!")

elif page == "Bookings":
    st.subheader("Booking History")

    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT id, name, phone, bus, source, destination,
               travel_date, seats, total
        FROM bookings ORDER BY id DESC
    """).fetchall()
    con.close()

    if rows:
        st.dataframe([
            {
                "Booking ID": r[0],
                "Name": r[1],
                "Mobile": r[2],
                "Bus": r[3],
                "From": r[4],
                "To": r[5],
                "Date": r[6],
                "Seats": r[7],
                "Total": f"₹{r[8]:,.0f}"
            }
            for r in rows
        ], use_container_width=True)
    else:
        st.info("Abhi koi booking nahi hai.")
