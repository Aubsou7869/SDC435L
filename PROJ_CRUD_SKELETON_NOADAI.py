## import gzip #<-- for  json.gz and openign github zip archive file may need may not 
import json
## import redis <-- make real when reddis or other program is ready 


# This function lets every program option accept normal input, B, or E.
def get_user_input(message):
    user_input = input(message + " (B = Back, E = Exit): ").strip()

    if user_input.upper() == "B":
        return None, "back"
    elif user_input.upper() == "E":
        return None, "exit"
    else:
        return user_input, "continue"


# This function runs after an operation has finished.
def option_finished():
    while True:
        choice = input(
            "Enter B to return to the menu or E to exit: "
        ).strip()

        if choice.upper() == "B":
            return "back"
        elif choice.upper() == "E":
            return "exit"
        else:
            print("Error: Enter B to go back or E to exit the program.")


# Function for the Redis database connection sequence.
def connect_to_database():
    """Connect to a Redis database running on this computer."""

    try:
        database = redis.Redis(
            host="localhost",
            port=0,
            db=0,
            decode_responses=True)

        # ping() tests whether Redis is available.
        database.ping()
        print("Redis connection Succesaful.")
        return database

    except redis.exceptions.RedisError as error:
        print("Unable to connect to Redis.")
        print("Error:", error)
        return None


# Function for reading a GitHub Archive file.
def read_archive_file(file_path):
    ##Reads JSON-formatted recs from a GitHub Archive file.##

    records = []

    # A compressed JSON or JSONL file. gzip used for this JIC
    if file_path.lower().endswith(".gz"):
        with gzip.open(file_path, "rt", encoding="utf-8") as archive_file:
            for line in archive_file:
                if line.strip() != "":
                    records.append(json.loads(line))

    #line-by-line for  JSON file.
    elif file_path.lower().endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8") as archive_file:
            for line in archive_file:
                if line.strip() != "":
                    records.append(json.loads(line))

    # normal JSON with list or one dictionary.
    else:
        with open(file_path, "r", encoding="utf-8") as archive_file:
            json_data = json.load(archive_file)

            if isinstance(json_data, list):
                records = json_data
            else:
                records.append(json_data)

    return records


# func for imnporting
def import_archive(database):
    ##Load archive recs and creates them in Redis##

    file_path, action = get_user_input(
        "Please enter the GitHub Archive filename"
    )

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    try:
        records = read_archive_file(file_path)
    except (OSError, json.JSONDecodeError) as error:
        print("The archive could not be read.")
        print("Error:", error)
        return option_finished()

    new_records = 0
    duplicate_records = 0
    invalid_records = 0

    for record in records:
        if not isinstance(record, dict) or "id" not in record:
            invalid_records += 1
        else:
            record_id = str(record["id"])
            redis_key = "github:event:" + record_id

            # using nx=True cause it will prevent a existing record from being replaced.
            record_saved = database.set(
                redis_key,
                json.dumps(record),
                nx=True)

            if record_saved:
                new_records += 1
            else:
                duplicate_records += 1

    print(f"{len(records)} records ready to be imported.")
    print("New records:", new_records)
    print("Duplicate records:", duplicate_records)
    print("Invalid records:", invalid_records)

    return option_finished()


# func for creating / adds new record to redis
def create_record(database):
    print("\nCREATE RECORD")

    record_id, action = get_user_input("Enter unique record ID")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    record_type, action = get_user_input(
        "Please enter record type: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    repository, action = get_user_input("Please enter the repository name: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    new_record = {
        "id": record_id,
        "type": record_type,
        "repository": repository}

    print("\nThis record will now be saved:")
    print(json.dumps(new_record, indent=2))

    confirmation, action = get_user_input(
        "Enter Y to save record or N to cancel")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    if confirmation.upper() == "Y":
        redis_key = "github:event:" + record_id

        # nx=True so redis creates key
        record_saved = database.set(
            redis_key,
            json.dumps(new_record),
            nx=True)

        if record_saved:
            print("Record was successfully created.")
        else:
            print("ERROR: A record with that ID already exists.")
    else:
        print("Record creation canceled.")

    return option_finished()


# func for read to display data to user end.
def read_record(database):
    print("\nREAD RECORD")

    record_id, action = get_user_input("Enter the record ID: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = "github:event:" + record_id
    saved_record = database.get(redis_key)

    if saved_record is None:
        print(f"Record {record_id} was not found.")
    else:
        print(json.dumps(json.loads(saved_record), indent=2))

    return option_finished()


# fuc update for uipdate appending already est data
def update_record(database):
    print("\nUPDATE RECORD")

    record_id, action = get_user_input("Enter the record ID to update: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = "github:event:" + record_id
    saved_record = database.get(redis_key)

    if saved_record is None:
        print(f"Sorry, {record_id} was not found.")
        return option_finished()

    current_record = json.loads(saved_record)
    print("Current record: ")
    print(json.dumps(current_record, indent=2))

    field_name, action = get_user_input("Enter the field to change: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    new_value, action = get_user_input("Please enter the new value: ")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    current_record[field_name] = new_value
    database.set(redis_key, json.dumps(current_record))

    print(
        f"Updated '{field_name}' in {record_id} "
        f"to '{new_value}'.")

    return option_finished()


# func delete removes a record from Redis
def delete_record(database):
    print("\nDELETE RECORD")

    record_id, action = get_user_input("Please enter the record ID to delete: 3")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = "github:event:" + record_id

    if not database.exists(redis_key):
        print(f"Record {record_id} was not found.")
        return option_finished()

    confirmation, action = get_user_input("Please type DELETE to confirm")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    if confirmation.upper() == "DELETE":
        database.delete(redis_key)
        print(f"Record {record_id} was deleted.")
    else:
        print("Delete canceled.")

    return option_finished()


# Feature 1: Search records by a word, ending, hashtag, or key.
def search_records(database):
    search_word, action = get_user_input(
        "Please enter a word, filename ending, hashtag, or key: ")

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    print("Currently searching for:", search_word)
    matching_records = []

    for redis_key in database.scan_iter(match="github:event:*"):
        saved_record = database.get(redis_key)

        if search_word.lower() in saved_record.lower():
            matching_records.append(json.loads(saved_record))

    if len(matching_records) == 0:
        print("No matching records were found.")
    else:
        print(len(matching_records), "matching records were found: ")
        for record in matching_records:
            print(json.dumps(record, indent=2))

    return option_finished()


# Feature 2: Group records by a selected field.
def group_records(database):
    group_field, action = get_user_input(
        "Enter the field you want to group by, such as type")

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    grouped_records = {}

    for redis_key in database.scan_iter(match="github:event:*"):
        saved_record = database.get(redis_key)
        record = json.loads(saved_record)
        group_value = str(record.get(group_field, "Field not found"))

        if group_value not in grouped_records:
            grouped_records[group_value] = 1
        else:
            grouped_records[group_value] += 1

    if len(grouped_records) == 0:
        print("There are no records to group.")
    else:
        print(f"Records grouped by '{group_field}':")
        for group_value in grouped_records:
            print(group_value, ":", grouped_records[group_value])

    return option_finished()


#Write database records to a JSON file.
def export_records(database):
    output_file, action = get_user_input(
        "Enter the output JSON filename: ")

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    records = []

    for redis_key in database.scan_iter(match="github:event:*"):
        saved_record = database.get(redis_key)
        records.append(json.loads(saved_record))

    try:
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(records, json_file, indent=2)

        print(f"{len(records)} records were written to '{output_file}'.")

    except OSError as error:
        print("Sorry, the file could not be written.")
        print("Error:", error)

    return option_finished()


# Displaying the menu.
def display_menu():
    print("\nGROUP 2'S ARCHIVE DATABASE MENU")
    print("1) Import archive file")
    print("2) Create/append a record")
    print("3) Read a record")
    print("4) Update a record")
    print("5) Delete a record")
    print("6) Search records")
    print("7) Group records")
    print("8) Export/write records to JSON")
    print("0) Exit Application")


# Main menu loop.
def main():
    database = connect_to_database()

    if database is None:
        print("Please Start Redis and run the application again.")
        return

    app_cont = True

    while app_cont:
        display_menu()
        choice = input("Please select an option: ").strip()
        result = None

        if choice == "1":
            result = import_archive(database)
        elif choice == "2":
            result = create_record(database)
        elif choice == "3":
            result = read_record(database)
        elif choice == "4":
            result = update_record(database)
        elif choice == "5":
            result = delete_record(database)
        elif choice == "6":
            result = search_records(database)
        elif choice == "7":
            result = group_records(database)
        elif choice == "8":
            result = export_records(database)
        elif choice == "0":
            app_cont = False
        else:
            print("Error: Enter a number from 0 through 8.")

        if result == "exit":
            app_cont = False

        # If result is "back", the while loop automatically displays
        # the main menu again.

    print("APPLICATION EXITED. GOODBYE.")


if __name__ == "__main__":
    main()
