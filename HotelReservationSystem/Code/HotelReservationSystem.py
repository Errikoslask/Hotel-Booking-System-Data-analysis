from datetime import datetime, date, timedelta
import json
from pathlib import Path

STATS_FILE = "stats.json"

def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"cancelled_count": 0}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


CUSTOMERS_FILE = Path("customers.json")
BOOKINGS_FILE = Path("bookings.json")

# --- Loading data ---
def load_json_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # dates-strings to dates
        for item in data:
            if "check_in" in item and isinstance(item["check_in"], str):
                item["check_in"] = datetime.strptime(item["check_in"], "%Y-%m-%d").date()
            if "check_out" in item and isinstance(item["check_out"], str):
                item["check_out"] = datetime.strptime(item["check_out"], "%Y-%m-%d").date()
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def cancel_booking(booking_to_cancel):
    bookings.remove(booking_to_cancel)
    save_json_data(BOOKINGS_FILE, bookings)
    stats['cancelled_count'] += 1
    save_stats(stats)

stats = load_stats()
customers = load_json_data(CUSTOMERS_FILE)
bookings = load_json_data(BOOKINGS_FILE)

# --- saving data ---
def save_json_data(file_path, data):
    # dates-strings to dates
    data_to_save = []
    for item in data:
        item_copy = item.copy()
        if "check_in" in item_copy and isinstance(item_copy["check_in"], date):
            item_copy["check_in"] = item_copy["check_in"].strftime("%Y-%m-%d")
        if "check_out" in item_copy and isinstance(item_copy["check_out"], date):
            item_copy["check_out"] = item_copy["check_out"].strftime("%Y-%m-%d")
        data_to_save.append(item_copy)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)



# --- add customer function ---
def add_customer(customer_dict):
    customers.append(customer_dict)
    save_json_data(CUSTOMERS_FILE, customers)

# --- add bookings function ---
def add_booking(booking_dict):
    bookings.append(booking_dict)
    save_json_data(BOOKINGS_FILE, bookings)

def find_existing_customer(email, phone):
    for customer in customers:
        if customer["email"] == email or customer["phone"] == phone:
            return customer
    return None


def format_date(d):
    return d.strftime("%d-%m-%Y")
# function that compares the dates and do bookings
def make_booking(room_type, new_customer_name, check_in, check_out):
    found = False
    for room in rooms:
        if room["type"] == room_type.lower():  # same room type
            available = True
            for booking in bookings:
                if booking["room id"] == room["room id"]:
                    if check_in < booking["check_out"] and check_out > booking["check_in"]:
                        available = False
                        break
            if available:
                print("The room", room["room id"], "is available! Continue giving customer's info to do the booking")
                found = True
                num_nights = (check_out - check_in).days
                cost = price_info['final_price'] * num_nights
                new_customer_email = input("Please enter the customer's email: ")
                new_customer_phone = input("Please enter the customer's phone number: ")
                existing_customer = find_existing_customer(new_customer_email, new_customer_phone)

                if existing_customer:
                    customer_id = existing_customer["customer id"]
                    print(f"Welcome back, {existing_customer['name']}! Using existing customer ID: {customer_id}")
                else:
                    customer_id = "C" + str(len(customers) + 1)
                    new_customer = {
                        "customer id": customer_id,
                        "name": new_customer_name,
                        "email": new_customer_email,
                        "phone": new_customer_phone
                    }
                    add_customer(new_customer)

                new_booking = {
                    "room id": room["room id"],
                    "check_in": check_in,
                    "check_out": check_out,
                    "customer id": customer_id,
                    "total_cost": round(cost, 2),

                }
                add_booking(new_booking)
                save_json_data(BOOKINGS_FILE, bookings)

                print(f"Booking confirmed for room {room['room id']} from {check_in} to {check_out} for customer {customer_id} Total cost: {round(cost, 2)}€")
                break
    if not found:
        print("No rooms available exactly on these dates.")
        suggestions = []

        # suggestions
        for shift in [-2, -1, 1, 2]:
            alt_check_in = check_in + timedelta(days=shift)
            alt_check_out = check_out + timedelta(days=shift)

            # validation test
            if alt_check_in >= date.today() and alt_check_in < alt_check_out:
                for room in rooms:
                    if room["type"] == room_type:  # same room type
                        available = True
                        for booking in bookings:
                            if booking["room id"] == room["room id"]:
                                if alt_check_in < booking["check_out"] and alt_check_out > booking["check_in"]:
                                    available = False
                                    break
                        if available:
                            suggestions.append((room["room id"], alt_check_in, alt_check_out))

        if suggestions:
            print("Suggested alternatives within +/- 2 days:")
            for idx, s in enumerate(suggestions, start=1):
                print(f"{idx}. Room {s[0]} from {format_date(s[1])} to {format_date(s[2])}")

            choice = input("Enter the number of the option to book, or 0 to return to menu: ")

            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(suggestions):
                    # Get the selected suggestion
                    selected_room, selected_check_in, selected_check_out = suggestions[choice - 1]
                    print(
                        f"You selected room {selected_room} from {format_date(selected_check_in)} to {format_date(selected_check_out)}.")
                    new_customer_email = input("Please enter the customer's email: ")
                    new_customer_phone = input("Please enter the customer's phone number: ")
                    customer_id = "C" + str(len(customers) + 1)
                    num_nights = (check_out - check_in).days
                    cost = price_info['final_price'] * num_nights

                    new_customer = {
                        "customer id": customer_id,
                        "name": new_customer_name,
                        "email": new_customer_email,
                        "phone": new_customer_phone
                    }
                    add_customer(new_customer)

                    new_booking = {
                        "room id": selected_room,
                        "check_in": selected_check_in.strftime("%Y-%m-%d"),   # date -> string
                        "check_out": selected_check_out.strftime("%Y-%m-%d"),
                        "customer id": customer_id,
                        "total_cost": round(cost, 2),
                    }
                    add_booking(new_booking)
                    save_json_data(BOOKINGS_FILE, bookings)

                    print(
                        f"Booking confirmed for room {room['room id']} from {check_in} to {check_out} for customer {customer_id} Total cost: {round(cost, 2)}€")

                else:
                    print("Returning to menu...")
            else:
                print("Invalid input. Returning to menu...")


def find_available_rooms(check_in, check_out, rooms, bookings):
    available_rooms = []

    for room in rooms:
        available = True
        for booking in bookings:
            if booking["room id"] == room["room id"]:
                if check_in < booking["check_out"] and check_out > booking["check_in"]:
                    available = False
                    break

        if available:
            available_rooms.append(room)

    return available_rooms

#option 3
def view_upcoming_bookings(bookings, customers):
    today = date.today()

    # upcoming only
    upcoming_bookings = [b for b in bookings if b["check_out"] >= today]
    upcoming_bookings.sort(key=lambda b: b["check_in"])

    if not upcoming_bookings:
        print("There are no upcoming bookings.")
        return

    print("Upcoming bookings:")
    for b in upcoming_bookings:
        customer_info = next((c for c in customers if c["customer id"] == b["customer id"]), None)
        customer_name = customer_info["name"] if customer_info else "Unknown"

        total_cost = b.get("total_cost", 0)  # χρησιμοποιούμε την αποθηκευμένη τιμή

        print(f"Room {b['room id']} | {b['check_in']} - {b['check_out']} | "
              f"Customer {b['customer id']} ({customer_name}) | "
              f"Total cost: {total_cost}€")


def dynamic_price(room_type, check_in, check_out):
    # Calculating the dynamic price based on:
    # 1. Availability
    # 2. Seasonality
    # 3. Last-minute / Early booking

    # --- 1. Base rate ---
    base_rates = {"single": 40, "double": 60, "suite": 90}
    base_rate = base_rates[room_type]

    # --- 2. Availability on specific dates ---
    # total number of rooms per type
    total_rooms = sum(1 for r in rooms if r["type"] == room_type)

    # --- 2. Availability ---
    booked_rooms = 0
    for b in bookings:
        room_info = next((r for r in rooms if r["room id"] == b["room id"]), None)
        if room_info and room_info["type"] == room_type:
            # overlap test
            if check_in < b["check_out"] and check_out > b["check_in"]:
                booked_rooms += 1

    occupancy_ratio = booked_rooms / total_rooms if total_rooms > 0 else 0
    occupancy_multiplier = 1 + 0.5 * occupancy_ratio  # αυξάνει μέχρι +50% αν όλα γεμάτα

    # --- 3. Seasonality ---
    month = check_in.month
    if month in [7, 8]:  # high season (July-August)
        season_multiplier = 1.3
    elif month in [5, 6, 9]:  # mid season (May,June,September)
        season_multiplier = 1.1
    else:  # low season
        season_multiplier = 1.0

    # --- 4. Last-minute / Early booking ---
    days_before_checkin = (check_in - date.today()).days
    if days_before_checkin < 7:
        lastminute_multiplier = 1.15  # +15% if < 7 μέρες
    elif days_before_checkin > 30:
        lastminute_multiplier = 0.95  # -5% if > 30 μέρες
    else:
        lastminute_multiplier = 1.0

    # --- Total dynamic price ---
    final_price = base_rate * occupancy_multiplier * season_multiplier * lastminute_multiplier

    return {
        "final_price": round(final_price, 2),
        "base_rate": base_rate,
        "occupancy_multiplier": occupancy_multiplier,
        "season_multiplier": season_multiplier,
        "lastminute_multiplier": lastminute_multiplier
    }


rooms = [
    # Single rooms (A1-A5)
    {"room id": "A1", "Price": 40, "type": "single"},
    {"room id": "A2", "Price": 40, "type": "single"},
    {"room id": "A3", "Price": 40, "type": "single"},
    {"room id": "A4", "Price": 40, "type": "single"},
    {"room id": "A5", "Price": 40, "type": "single"},

    # Double rooms (D1-D5)
    {"room id": "D1", "Price": 60, "type": "double"},
    {"room id": "D2", "Price": 60, "type": "double"},
    {"room id": "D3", "Price": 60, "type": "double"},
    {"room id": "D4", "Price": 60, "type": "double"},
    {"room id": "D5", "Price": 60, "type": "double"},

    # Suites (S1-S3)
    {"room id": "S1", "Price": 90, "type": "suite"},
    {"room id": "S2", "Price": 90, "type": "suite"},
    {"room id": "S3", "Price": 90, "type": "suite"}
]
#All the rooms we have
total_rooms = len(rooms)

from datetime import date



while True:
    # Show menu
    print("1. New Booking")
    print("2. Show Available Rooms")
    print("3. View Bookings")
    print("4. Cancel booking")
    print("5. Exit")

    # Get user input
    answer = input("Select an option (1-5): ").strip()

    # Validate input
    if answer not in ["1", "2", "3", "4", "5"]:
        print("Invalid option. Please enter a number between 1 and 5.")
        continue  # Looping again

    # Exit
    if answer == "5":
        print("Exiting program...")
        break  # Exit the loop

    # Handle other options
    if answer == "1":
        print("You selected New Booking")
        # call function for new booking
        new_customer_name = input("Please enter the customer's full name: ")
        while True:
            room_type = input("Please enter the room type (single/double/suite): ").strip().lower()
            if room_type not in ["single", "double", "suite"]:
                print("Invalid option. Please answer between single, double or suite")
                continue

            else:
                break

        while True:
            check_in_str = input("Please enter the check-in date (DD-MM-YYYY): ")
            check_out_str = input("Please enter the check-out date (DD-MM-YYYY): ")

            try:
                check_in = datetime.strptime(check_in_str, "%d-%m-%Y").date()
                check_out = datetime.strptime(check_out_str, "%d-%m-%Y").date()
            except ValueError:
                print("Invalid format! Please enter dates as DD-MM-YYYY and ensure they are valid calendar dates.")
                continue

            stay_length = (check_out - check_in).days
            today = date.today()
            if check_in < today:
                print("Check-in must be after today. Try again")
                continue
            elif check_out <= check_in:
                print("Check-out must be after check-in (and not the same day). Try again")
                continue
            elif stay_length > 30:
                print("Stay cannot be longer than 30 days. Try again")
            else:
                break

        price_info = dynamic_price(room_type, check_in, check_out)
        num_nights = (check_out - check_in).days
        cost = price_info['final_price'] * num_nights
        print(f"Final price for this booking: {round(cost, 2)}€")
        print(
            f"(Base rate: {price_info['base_rate']}€, Occupancy multiplier: {price_info['occupancy_multiplier']}, Season multiplier: {price_info['season_multiplier']}, Last-minute multiplier: {price_info['lastminute_multiplier']})")

        #looking for availability of rooms
        make_booking(room_type, new_customer_name, check_in, check_out)


    elif answer == "2":
        print("You selected Show Available Rooms (info only)")
        # Input dates with validation
        while True:
            check_in_str = input("Please enter the check-in date (DD-MM-YYYY): ")
            check_out_str = input("Please enter the check-out date (DD-MM-YYYY): ")
            try:
                check_in = datetime.strptime(check_in_str, "%d-%m-%Y").date()
                check_out = datetime.strptime(check_out_str, "%d-%m-%Y").date()
            except ValueError:
                print("Invalid format! Please enter dates as DD-MM-YYYY and ensure they are valid calendar dates.")
                continue
            stay_length = (check_out - check_in).days
            today = date.today()

            if check_in < today:
                print("Check-in must be after today. Try again")
            elif check_out <= check_in:
                print("Check-out must be after check-in (and not the same day). Try again")
            elif stay_length > 30:
                print("Stay cannot be longer than 30 days. Try again")
            else:
                break

        # Finding available rooms
        available_rooms = find_available_rooms(check_in, check_out, rooms, bookings)
        if not available_rooms:
            print("No rooms available in these exact dates.")
        else:
            print("Available rooms in the selected period:")
            for room in available_rooms:
                print(f"- Room {room['room id']} ({room['type']})")


    elif answer == "3":
        print("You selected View Bookings")
        view_upcoming_bookings(bookings, customers)


    elif answer == "4":
        # 1. ask for customer id
        search_id = input("Enter customer id to cancel booking: ")
        # 2. look for the id and the check in in bookings
        found_booking = None
        for booking in bookings:
            if booking["customer id"] == search_id:
                found_booking = booking
                break

        # 3. if we found the id
        if found_booking:
            print(
                f"Booking found: Room {found_booking['room id']} from {found_booking['check_in']} to {found_booking['check_out']}, Customer {found_booking['customer id']}")
            confirm = input("Do you want to cancel this booking? (Y/N): ")
            if confirm.upper() == "Y":
                cancel_booking(found_booking)  # pass the correct variable
                print("Booking successfully cancelled.")
            else:
                print("Cancellation aborted.")
        else:
            print("No booking found with this id.")





