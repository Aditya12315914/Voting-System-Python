import json, os, random, string, sys

DATA_FILE = "election_data.json"


# ------------------- Helper Functions -------------------
def load_data():
    """Load data from JSON file or initialize new."""
    if not os.path.exists(DATA_FILE):
        data = {"admins": [{"username": "admin", "password": "admin123"}], "elections": {}}
        save_data(data)
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Save to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def generate_id(prefix, length=5):
    """Generate random ID with prefix."""
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ------------------- Core System -------------------
def admin_menu():
    data = load_data()
    while True:
        clear_screen()
        print("\n====== 🗳️ ADMIN DASHBOARD ======")
        print("1. Create Election")
        print("2. View Elections")
        print("3. Logout")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            create_election(data)
        elif choice == "2":
            view_elections(data)
        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice!")
            input("Press Enter...")


def voter_menu():
    data = load_data()
    clear_screen()
    print("\n====== 🪪 VOTER LOGIN ======")
    voter_id = input("Enter your Voter ID: ").strip()

    # Find election containing this voter
    found = None
    for e_name, e_data in data["elections"].items():
        if voter_id in e_data["voters"]:
            found = e_name
            break

    if not found:
        print("❌ Invalid Voter ID.")
        input("Press Enter...")
        return

    election = data["elections"][found]
    voter = election["voters"][voter_id]

    if voter["voted"]:
        print("⚠️ You have already voted.")
        input("Press Enter...")
        return

    vote_in_election(data, found, voter_id)


# ------------------- Admin Functions -------------------
def create_election(data):
    clear_screen()
    print("\n====== 🏛️ CREATE NEW ELECTION ======")
    name = input("Enter election name: ").strip()
    if name in data["elections"]:
        print("❌ Election already exists.")
        input("Press Enter...")
        return

    data["elections"][name] = {
        "candidates": [],
        "voters": {},
        "votes": {},
        "suggestions": [],
        "results_published": False
    }

    save_data(data)
    print(f"✅ Election '{name}' created successfully.")
    input("Press Enter...")


def view_elections(data):
    clear_screen()
    elections = data["elections"]

    if not elections:
        print("No elections available.")
        input("Press Enter...")
        return

    print("\n====== 📋 AVAILABLE ELECTIONS ======")
    for idx, e in enumerate(elections.keys(), start=1):
        print(f"{idx}. {e}")

    try:
        choice = int(input("\nSelect an election (number): "))
        selected = list(elections.keys())[choice - 1]
    except:
        print("Invalid choice!")
        input("Press Enter...")
        return

    manage_election(data, selected)

def manage_election(data, election_name):
    election = data["elections"][election_name]
    while True:
        clear_screen()
        print(f"\n====== ⚙️ MANAGING ELECTION: {election_name} ======")
        print("1. Add Candidate")
        print("2. Add Voter")
        print("3. View Candidates")
        print("4. View Voters")
        print("5. Remove Candidate")
        print("6. Remove Voter")
        print("7. View Results")
        print("8. Publish Results")
        print("9. Delete Election")
        print("10. Go Back")

        choice = input("\nEnter choice: ")

        if choice == "1":
            add_candidate(election)
        elif choice == "2":
            add_voter(election)
        elif choice == "3":
            view_candidates(election)
        elif choice == "4":
            view_voters(election)
        elif choice == "5":
            remove_candidate(election)
        elif choice == "6":
            remove_voter(election)
        elif choice == "7":
            view_results(election)
        elif choice == "8":
            election["results_published"] = True
            print("✅ Results published successfully.")
            input("Press Enter...")
        elif choice == "9":
            confirm = input(f"⚠️ Are you sure you want to delete '{election_name}'? (y/n): ").lower()
            if confirm == "y":
                del data["elections"][election_name]
                save_data(data)
                print(f"🗑️ Election '{election_name}' deleted successfully!")
                input("Press Enter...")
                break
            else:
                print("❌ Deletion canceled.")
                input("Press Enter...")
        elif choice == "10":
            save_data(data)
            break
        else:
            print("Invalid choice!")
            input("Press Enter...")

        save_data(data)



def add_candidate(election):
    clear_screen()
    print("\n====== 🧾 ADD CANDIDATE ======")
    name = input("Candidate Name: ").strip()
    party = input("Party Name: ").strip()

    cid = generate_id("C")
    candidate = {"id": cid, "name": name, "party": party}
    election["candidates"].append(candidate)
    election["votes"][cid] = 0

    print(f"✅ Candidate '{name}' added successfully!")
    input("Press Enter...")


def remove_candidate(election):
    clear_screen()
    print("\n====== ❌ REMOVE CANDIDATE ======")
    if not election["candidates"]:
        print("No candidates available.")
        input("Press Enter...")
        return

    for idx, c in enumerate(election["candidates"], start=1):
        print(f"{idx}. {c['name']} ({c['party']}) - ID: {c['id']}")

    try:
        choice = int(input("\nSelect candidate number to remove: "))
        selected = election["candidates"][choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice!")
        input("Press Enter...")
        return

    confirm = input(f"⚠️ Are you sure you want to remove '{selected['name']}'? (y/n): ").lower()
    if confirm == "y":
        election["candidates"].remove(selected)
        if selected["id"] in election["votes"]:
            del election["votes"][selected["id"]]
        print(f"✅ Candidate '{selected['name']}' removed successfully!")
    else:
        print("❌ Removal canceled.")

    input("Press Enter...")



def add_voter(election):
    clear_screen()
    print("\n====== 👤 REGISTER VOTER ======")
    name = input("Voter Name: ").strip()
    try:
        age = int(input("Age: "))
        if age < 18:
            print("❌ Voter must be at least 18 years old.")
            input("Press Enter...")
            return
    except:
        print("Invalid age!")
        input("Press Enter...")
        return

    vid = generate_id("V")
    election["voters"][vid] = {"name": name, "age": age, "voted": False}
    print(f"✅ Voter '{name}' added successfully with ID: {vid}")
    input("Press Enter...")


def remove_voter(election):
    clear_screen()
    print("\n====== ❌ REMOVE VOTER ======")
    if not election["voters"]:
        print("No voters registered yet.")
        input("Press Enter...")
        return

    for idx, (vid, v) in enumerate(election["voters"].items(), start=1):
        status = "✅ Voted" if v["voted"] else "❌ Not Voted"
        print(f"{idx}. {v['name']} ({v['age']} yrs) - {vid} - {status}")

    try:
        choice = int(input("\nSelect voter number to remove: "))
        selected_vid = list(election["voters"].keys())[choice - 1]
        selected_voter = election["voters"][selected_vid]
    except (ValueError, IndexError):
        print("Invalid choice!")
        input("Press Enter...")
        return

    confirm = input(f"⚠️ Remove voter '{selected_voter['name']}' (ID: {selected_vid})? (y/n): ").lower()
    if confirm == "y":
        del election["voters"][selected_vid]
        print(f"✅ Voter '{selected_voter['name']}' removed successfully!")
    else:
        print("❌ Removal canceled.")

    input("Press Enter...")



def view_candidates(election):
    clear_screen()
    print("\n====== 🧍‍♂️ CANDIDATES LIST ======")
    if not election["candidates"]:
        print("No candidates added yet.")
    else:
        for c in election["candidates"]:
            print(f"🗳️ {c['name']} ({c['party']}) — ID: {c['id']}")
    input("\nPress Enter...")


def view_voters(election):
    clear_screen()
    print("\n====== 🪪 VOTER LIST ======")
    if not election["voters"]:
        print("No voters registered.")
    else:
        for vid, v in election["voters"].items():
            status = "✅ Voted" if v["voted"] else "❌ Not Voted"
            print(f"{vid} - {v['name']} ({v['age']} yrs) - {status}")
    input("\nPress Enter...")


def view_results(election):
    clear_screen()
    print("\n====== 🏆 RESULTS ======")
    if not election["results_published"]:
        print("⚠️ Results not published yet.")
    else:
        total_votes = sum(election["votes"].values())
        if total_votes == 0:
            print("No votes cast yet.")
        else:
            for c in election["candidates"]:
                cid = c["id"]
                votes = election["votes"].get(cid, 0)
                percent = (votes / total_votes) * 100 if total_votes > 0 else 0
                print(f"{c['name']} ({c['party']}): {votes} votes ({percent:.2f}%)")
            winner = max(election["votes"], key=election["votes"].get)
            winner_name = next(c["name"] for c in election["candidates"] if c["id"] == winner)
            print(f"\n🏅 Winner: {winner_name}")
    input("\nPress Enter...")

# ------------------- Voter Functions -------------------
def vote_in_election(data, election_name, voter_id):
    election = data["elections"][election_name]
    voter = election["voters"][voter_id]

    clear_screen()
    print(f"\n====== 🗳️ VOTING PAGE ({election_name}) ======")
    print(f"Welcome, {voter['name']}!")
    print("\nCandidates:")
    for idx, c in enumerate(election["candidates"], start=1):
        print(f"{idx}. {c['name']} ({c['party']})")

    try:
        choice = int(input("\nSelect candidate number: "))
        selected = election["candidates"][choice - 1]
    except Exception:
        print("Invalid choice!")
        input("Press Enter...")
        return

    election["votes"][selected["id"]] += 1
    election["voters"][voter_id]["voted"] = True

    suggestion = input("Would you like to add a suggestion/feedback? (press Enter to skip): ")
    if suggestion.strip():
        election["suggestions"].append({"voter": voter_id, "text": suggestion.strip()})

    save_data(data)
    print("\n✅ Your vote has been recorded successfully!")
    input("Press Enter...")


# ------------------- Main Menu -------------------
def main():
    while True:
        clear_screen()
        print("\n========== SMART VOTING SYSTEM ==========")
        print("1. Admin Login")
        print("2. Voter Login")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            data = load_data()
            username = input("Username: ")
            password = input("Password: ")
            found = next((a for a in data["admins"] if a["username"] == username and a["password"] == password), None)
            if found:
                admin_menu()
            else:
                print("❌ Invalid credentials.")
                input("Press Enter...")

        elif choice == "2":
            voter_menu()

        elif choice == "3":
            print("Exiting... Goodbye!")
            sys.exit()

        else:
            print("Invalid choice!")
            input("Press Enter...")


if __name__ == "__main__":
    main()

