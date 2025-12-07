from datetime import datetime
import getpass  

LOST_FILE = "lost.txt"
FOUND_FILE = "found.txt"
RESOLVED_FILE = "resolved.txt"
SECRET_CODE = "CAMPUS123"  


for f in [LOST_FILE, FOUND_FILE, RESOLVED_FILE]:
    open(f, 'a').close()

def report_item(item_type):
    print(f"\n📝 Reporting {item_type} item:")
    
    verification_code = input("🔐 Set a 4-digit verification code: ")
    while not (verification_code.isdigit() and len(verification_code) == 4):
        verification_code = input("❌ Must be 4 digits! Try again: ")

    item_name = input("🔹 Item name: ")
    description = input("🔹 Description: ")

    if item_type == 'lost':
        location = input("📍 Location (press Enter if unknown): ").strip()
        if not location:
            location = "unknown"
    else:  
        location = input("📍 Location where item was found: ").strip()
        while not location:
            location = input("❌ Location cannot be empty! Please enter where it was found: ").strip()

    contact = input("📞 Contact: ")

    with open(LOST_FILE if item_type == 'lost' else FOUND_FILE, 'a') as f:
        f.write(f"{item_name}|{description}|{location}|{contact}|{verification_code}|"
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
    print(f"✅ {item_type.capitalize()} item reported successfully!")
    print(f"🔒 Verification code: {verification_code} (Required when claiming)\n")



def view_items(item_type):
  
    print(f"\n📜 {item_type.upper()} ITEMS:")
    try:
        with open(LOST_FILE if item_type == 'lost' else FOUND_FILE) as f:
            for i, line in enumerate(f, 1):
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    print(f"\n#{i} {parts[0]}")
                    print(f"📝 Description: {parts[1]}")
                    print(f"📍 Location: {parts[2]}")
                    print(f"📞 Contact: {parts[3]}")
                    print(f"⏰ Date: {parts[5]}")
                else:
                    print(f"⚠️ Corrupted entry: {line.strip()}")
    except FileNotFoundError:
        print("No items found yet!\n")

def search_items():
    
    term = input("\n🔍 Enter search term: ").lower()
    for name, file in [('LOST', LOST_FILE), ('FOUND', FOUND_FILE)]:
        print(f"\n=== {name} ITEMS ===")
        try:
            with open(file) as f:
                for i, line in enumerate(f, 1):
                    if term in line.lower():
                        print(f"🔹 #{i} {line.split('|')[0]}")
        except FileNotFoundError:
            print("No items found!\n")

def match_items():
    print("\n💞 MATCHING LOST & FOUND ITEMS...")
    try:
        with open(LOST_FILE) as lost, open(FOUND_FILE) as found:
            lost_items = [line.strip().split('|') for line in lost]
            found_items = [line.strip().split('|') for line in found]
        
        high_confidence = 0
        potential = 0

        for l in lost_items:
            for f in found_items:
                if len(l) > 4 and len(f) > 4:
                    lost_name = l[0].lower().strip()
                    found_name = f[0].lower().strip()
                    lost_location = l[2].lower().strip()
                    found_location = f[2].lower().strip()

                    # Check for item name similarity
                    name_match = lost_name in found_name or found_name in lost_name

                    # Handle unknown locations
                    if lost_location != "unknown" and found_location != "unknown":
                        location_match = lost_location in found_location or found_location in lost_location
                    else:
                        location_match = False  # You can also make this True if you want to be lenient

                    # Match logic
                    if name_match:
                        if location_match:
                            high_confidence += 1
                            print(f"\n🎯 HIGH-CONFIDENCE MATCH #{high_confidence}")
                        else:
                            potential += 1
                            print(f"\n✨ POTENTIAL MATCH #{potential}")
                        
                        print(f"🔹 Lost: {l[0]} (📅 {l[5]})")
                        print(f"🔹 Found: {f[0]} (📅 {f[5]})")
                        print(f"📍 Lost Location: {l[2]}" + (" (unknown)" if lost_location == "unknown" else ""))
                        print(f"📍 Found Location: {f[2]}" + (" (unknown)" if found_location == "unknown" else ""))
                        print(f"📞 Owner: {l[3]} | Finder: {f[3]}")
                        print("━" * 40)

        if high_confidence or potential:
            print(f"\n✅ {high_confidence} high-confidence and {potential} potential match(es) found!")
        else:
            print("\n❌ No matches found!")
    except FileNotFoundError:
        print("❌ Data files missing!")

   

def verify_claim():
    
    print("\n🔐 VERIFY OWNERSHIP")
    item_type = input("Are you verifying a (1) Lost item claim or (2) Resolving a Found item return?")
    if item_type not in ['1', '2']:
        print("❌ Invalid choice!")
        return
    
    view_items("lost" if item_type == '1' else "found")
    try:
        item_num = int(input("\n🔢 Enter item number: ")) - 1
        verification_code = input("🔢 Enter verification code: ")
        
        filename = LOST_FILE if item_type == '1' else FOUND_FILE
        with open(filename, 'r') as f:
            items = f.readlines()
        
        if 0 <= item_num < len(items):
            parts = items[item_num].strip().split('|')
            if len(parts) >= 6 and parts[4] == verification_code:
                print("\n🎉 OWNERSHIP VERIFIED!")
                print(f"📦 Item: {parts[0]}")
                print(f"👤 Owner: {parts[3]}")
                print(f"📅 Reported: {parts[5]}")
                
                
                if input("\n🔐 Admin override? (y/n): ").lower() == 'y':
                    if getpass.getpass("Enter admin password: ") == SECRET_CODE:
                        print("🔓 Admin override granted!")
                    else:
                        print("❌ Wrong password!")
                        return
                
                
                with open(RESOLVED_FILE, 'a') as f:
                    f.write(f"RESOLVED|{parts[0]}|{parts[3]}|{datetime.now().strftime('%Y-%m-%d')}\n")
                
                
                with open(filename, 'w') as f:
                    f.writelines(item for i, item in enumerate(items) if i != item_num)
                print("✅ Item successfully returned!")
            else:
                print("❌ Invalid verification code!")
        else:
            print("❌ Invalid item number!")
    except ValueError:
        print("❌ Please enter a valid number!")


while True:
    print("\n" + "━"*50)
    print("📌 LOST & FOUND TRACKER".center(50))
    print("━"*50)
    print("1️⃣ Report Lost Item")
    print("2️⃣ Report Found Item")
    print("3️⃣ View Lost Items")
    print("4️⃣ View Found Items")
    print("5️⃣ Search Items")
    print("6️⃣ Match Items")
    print("7️⃣ Verify Ownership")
    print("8️⃣ Exit")
    
    choice = input("\n👉 Enter choice (1-8): ")
    
    if choice == '1': report_item('lost')
    elif choice == '2': report_item('found')
    elif choice == '3': view_items('lost')
    elif choice == '4': view_items('found')
    elif choice == '5': search_items()
    elif choice == '6': match_items()
    elif choice == '7': verify_claim()
    elif choice == '8':
        print("\n👋 Thank you for using the Lost & Found Tracker!")
        break
    else:
        print("\n❌ Invalid choice! Please try again.")