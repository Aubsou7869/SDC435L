"""Group 2 redis and mongodb program v3"""
##--- run command prompt and run "python -m pip install redis pymongo to ensure python program can function propperly--##
import json
import os
import redis
import pymongo

#Sep datasets i/o to stop sample and full records from overwrting each other.
DATASETS = ["Commits", "Contents", "Files", "Languages", "Licenses",
            "Sample_Commits", "Sample_Contents", "Sample_Files", "Sample_Repos"]

# key fields are being used together to id a record within each dataset.
KEY_FIELDS = {
    "Commits": ["commit"],
    "Sample_Commits": ["commit", "repo_name"],
    "Contents": ["id"],
    "Sample_Contents": ["id"],
    "Files": ["repo_name", "ref", "path", "id"],
    "Sample_Files": ["repo_name", "ref", "path", "id"],
    "Languages": ["repo_name"],
    "Licenses": ["repo_name"],
    "Sample_Repos": ["repo_name"]}


def choose_dataset():
    for dataset in DATASETS:
        print(dataset)
    while True:
        dataset, action = get_user_input("Enter a dataset name from the list")
        if action != "continue":
            return None, action
        if dataset in DATASETS:
            return dataset, "continue"
        print("Enter a name exactly as shown, without .json.")


def make_record_key(record, dataset):
    if not isinstance(record, dict):
        return None
    values = []
    for field in KEY_FIELDS[dataset]:
        value = record.get(field)
        if not isinstance(value, str) or value.strip() == "":
            return None
        values.append(value)
    # A JSON list keeps multiple key parts separate, even if paths contain colons.
    return "github:archive:" + dataset + ":" + json.dumps(values, separators=(",", ":"))


def convert_value(text, old_value):
    # Keep numbers stored as strings in the original dataset as strings.
    if isinstance(old_value, str):
        return text
    value = json.loads(text)
    if type(value) != type(old_value):
        raise ValueError("The new value must have the same data type as the old value.")
    return value



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
            "Enter B to return to the menu or E to exit: ").strip()

        if choice.upper() == "B":
            return "back"
        elif choice.upper() == "E":
            return "exit"
        else:
            print("Error: Enter B to go back or E to exit the program.")


# Function for the Redis database connection sequence.
def connect_to_database():
    """Connect to a Redis database running on this system."""

    try:
        database = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5)

        # ping() test fr Redis connection.
        database.ping()
        print("Redis connection was successful.")
        return database

    except redis.exceptions.RedisError as error:
        print("ATTENTION: Unable to connect to Redis.")
        print("Error:", error)
        return None


# Function for reading a GitHub Archive file.
def read_archive_file(file_path, maximum_records):
    records = []
    with open(file_path, "r", encoding="utf-8-sig") as archive_file:
        for line in archive_file:
            if line.strip() == "":
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append(None)  # Count anomalous lines as invalid records.
            if len(records) >= maximum_records:
                break
    return records


def import_archive(database):
    ##Load archive recs and creates them in Redis##

    file_path, action = get_user_input(
        "Enter the path to an extracted JSON file (not the ZIP)")

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    # Use the supplied filename to choose the dataset automatically.
    dataset = os.path.splitext(os.path.basename(file_path))[0]
    if dataset not in DATASETS:
        dataset, action = choose_dataset()
        if action != "continue":
            return action

    while True:
        limit_text, action = get_user_input("Maximum records to read [100]")
        if action != "continue":
            return action
        if limit_text == "":
            maximum_records = 100
            break
        if limit_text.isdigit() and int(limit_text) > 0:
            maximum_records = int(limit_text)
            break
        print("Enter a whole number greater than zero.")

    try:
        records = read_archive_file(file_path, maximum_records)
    except (OSError, UnicodeError) as error:
        print("The archive could not be read.")
        print("Error:", error)
        return option_finished()

    new_records = 0
    duplicate_records = 0
    invalid_records = 0

    for record in records:
        redis_key = make_record_key(record, dataset)
        if redis_key is None:
            invalid_records += 1
        else:

            # using nx=True cause it will prevent a existing record from being replaced.
            record_saved = database.set(
                redis_key,
                json.dumps(record),
                nx=True)

            if record_saved:
                new_records += 1
            else:
                duplicate_records += 1

    print(f"{len(records)} records were processed from {dataset}.")
    print("New records:", new_records)
    print("Duplicate records:", duplicate_records)
    print("Invalid records:", invalid_records)

    return option_finished()


# func for creating / adds new record to redis
def collect_new_record():
    print("\nCREATE RECORD")
    dataset, action = choose_dataset()
    if action != "continue":
        return None, None, action

    # These are basic fields from the actual files. Import preserves ALL fields.
    # Empty values below specify the data type; they are not saved as defaults.
    if dataset == "Commits":
        new_record = {"commit": "", "repo_name": [], "subject": "", "message": ""}
    elif dataset == "Sample_Commits":
        new_record = {"commit": "", "repo_name": "", "subject": "", "message": ""}
    elif dataset in ["Files", "Sample_Files"]:
        new_record = {"repo_name": "", "ref": "", "path": "", "id": "", "mode": ""}
    elif dataset in ["Contents", "Sample_Contents"]:
        new_record = {"id": "", "size": "", "content": "", "binary": False, "copies": ""}
        if dataset == "Sample_Contents":
            new_record.update({"sample_repo_name": "", "sample_ref": "",
                               "sample_path": "", "sample_mode": ""})
    elif dataset == "Languages":
        new_record = {"repo_name": "", "language": []}
    elif dataset == "Licenses":
        new_record = {"repo_name": "", "license": ""}
    else:
        new_record = {"repo_name": "", "watch_count": ""}

    for field in new_record:
        if isinstance(new_record[field], list):
            if field == "language":
                print('Example language list: [{"name": "Python", "bytes": "500"}]')
            else:
                print('Example repository list: ["owner/project"]')
        elif isinstance(new_record[field], bool):
            print("Enter true or false for the binary field.")
        while True:
            value, action = get_user_input("Enter " + field)
            if action != "continue":
                return None, None, action
            try:
                new_record[field] = convert_value(value, new_record[field])
                break
            except ValueError as error:
                print("Invalid value:", error)

    return new_record, dataset, "continue"


def create_record(database):
    new_record, dataset, action = collect_new_record()
    if action != "continue":
        return action

    redis_key = make_record_key(new_record, dataset)
    if redis_key is None:
        print("The identifying fields cannot be empty.")
        return option_finished()

    print("\nRecord to save:")
    print(json.dumps(new_record, indent=2))
    confirmation, action = get_user_input("Enter Y to save or N to cancel")
    if action != "continue":
        return action
    if confirmation.upper() == "Y":
        record_saved = database.set(redis_key, json.dumps(new_record), nx=True)
        if record_saved:
            print("Record created. Redis key:", redis_key)
        else:
            print("Sorry, record with that key already exists.")
    else:
        print("Record creation canceled.")
    return option_finished()


def read_record(database):
    print("\nREAD RECORD")

    record_id, action = get_user_input("Paste the full Redis key shown from search")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = record_id
    if not redis_key.startswith("github:archive:"):
        print("Use Search to find this program's full Redis key.")
        return option_finished()
    saved_record = database.get(redis_key)

    if saved_record is None:
        print(f"Record {record_id} was not found.")
    else:
        print(json.dumps(json.loads(saved_record), indent=2))

    return option_finished()


# fuc update for uipdate/appending already est data
def update_record(database):
    print("\nUPDATE RECORD")

    record_id, action = get_user_input("Paste the full Redis key to update")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = record_id
    if not redis_key.startswith("github:archive:"):
        print("Use Search to find this program's full Redis key.")
        return option_finished()
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

    new_value, action = get_user_input("Enter the new value (use JSON for lists, objects, or booleans)")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    dataset = redis_key.split(":", 3)[2]
    if dataset not in KEY_FIELDS or field_name in KEY_FIELDS[dataset]:
        print("Identifying fields cannot be changed. Create a new record instead.")
        return option_finished()
    if field_name not in current_record:
        print("Choose one of the existing top-level fields shown above.")
        return option_finished()
    try:
        current_record[field_name] = convert_value(new_value, current_record[field_name])
    except ValueError as error:
        print("Invalid value:", error)
        return option_finished()
    # xx=True updates only an existing key.
    if not database.set(redis_key, json.dumps(current_record), xx=True):
        print("The record no longer exists.")
        return option_finished()

    print(
        f"Updated '{field_name}' in {record_id} "
        f"to '{new_value}'.")

    return option_finished()


# func delete removes a record from Redis
def delete_record(database):
    print("\nDELETE RECORD")

    record_id, action = get_user_input("Paste the full Redis key to delete")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    redis_key = record_id
    if not redis_key.startswith("github:archive:"):
        print("Use Search to find this program's full Redis key.")
        return option_finished()

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


# first feat search records by a word, ending, hashtag, or key.
def search_records(database):
    search_word, action = get_user_input(
        "Enter a word, path, hash, or key (press Enter to list records)")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    print("Currently searching for:", search_word)
    matching_records = []
    seen_keys = set()
    for redis_key in database.scan_iter(match="github:archive:*"):
        if redis_key in seen_keys:
            continue
        seen_keys.add(redis_key)
        saved_record = database.get(redis_key)
        if saved_record is None:
            continue
        if search_word.lower() in (redis_key + " " + saved_record).lower():
            matching_records.append(redis_key)
            print(len(matching_records), "Redis key:", redis_key)
            # lowering results here so when searching the return is a reasonable/realistic amount of contnt for user scanning through.
            if len(matching_records) == 25:
                print("Showing up to 25 matches. Please narrow the search for closer results.")
                break

    if len(matching_records) == 0:
        print("No matching records found.")
        return option_finished()

    while True:
        selection, action = get_user_input("Enter a result number to view")
        if action != "continue":
            return action
        if selection.isdigit() and 1 <= int(selection) <= len(matching_records):
            redis_key = matching_records[int(selection) - 1]
            saved_record = database.get(redis_key)
            print("Redis key:", redis_key)
            if saved_record is not None:
                print(json.dumps(json.loads(saved_record), indent=2))
            else:
                print("This record no longer exists.")
            return option_finished()
        print("Please choose a result number from the list.")


def group_records(database):
    group_field, action = get_user_input(
        "Enter a top-level field such as repo_name, license, or mode")

    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    grouped_records = {}

    seen_keys = set()
    for redis_key in database.scan_iter(match="github:archive:*"):
        if redis_key in seen_keys:
            continue
        seen_keys.add(redis_key)
        saved_record = database.get(redis_key)
        if saved_record is None:
            continue
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
    dataset, action = choose_dataset()
    if action != "continue":
        return action
    output_file, action = get_user_input("Enter the output JSON filename")
    if action == "back":
        return "back"
    elif action == "exit":
        return "exit"

    if os.path.exists(output_file):
        confirmation, action = get_user_input("File exists. Please type OVERWRITE to replace it")
        if action != "continue":
            return action
        if confirmation != "OVERWRITE":
            print("Export canceled.")
            return option_finished()

    records_written = 0
    seen_keys = set()
    try:
        with open(output_file, "w", encoding="utf-8") as json_file:
            for redis_key in database.scan_iter(match="github:archive:" + dataset + ":*"):
                if redis_key in seen_keys:
                    continue
                seen_keys.add(redis_key)
                saved_record = database.get(redis_key)
                if saved_record is not None:
                    # One record per line, matching the supplied archive format.
                    json_file.write(json.dumps(json.loads(saved_record)) + "\n")
                    records_written += 1
        print(f"{records_written} records were written to '{output_file}'.")
        print("Select the same dataset if you import this file later.")
    except OSError as error:
        print("The file could not be fully written:", error)
    return option_finished()


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


# Redis selected main menu loop.
def redis_menu():
    database = connect_to_database()

    if database is None:
        print("Please Start Redis and run the application again.")
        return

    app_cont = True

    while app_cont:
        display_menu()
        choice = input("Please select an option: ").strip()
        result = None

        try:
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
        except (redis.exceptions.RedisError, ValueError) as error:
            print("Operation stopped:", error)
            print("Any records already saved remain in Redis.")
            result = option_finished()

        if result == "exit":
            app_cont = False

        # If result is "back", the while loop automatically displays
        # the main menu again.

    database.close()
    print("The Redis session has ended.")


# *** MONGODB Program half begins here***
#Due to sep menu pathing choosing either MONGODB or Redis in starting menu will now begin executing the respected db's program routes.
## don't forget within next revision revisit running both together when you have more time to play with it##


# Separated functions showing the MongoDB commands so program isnt mistakenly changing the Redis half of programs commands.
# Each field below is for exact matches search using an index
MONGO_SEARCH_FIELDS = {
    "Commits": ["repo_name", "commit", "author.name"],
    "Sample_Commits": ["repo_name", "commit", "author.name"],
    "Files": ["repo_name", "path", "id"],
    "Sample_Files": ["repo_name", "path", "id"],
    "Contents": ["id"],
    "Sample_Contents": ["id", "sample_repo_name", "sample_path"],
    "Languages": ["repo_name", "language.name"],
    "Licenses": ["repo_name", "license"],
    "Sample_Repos": ["repo_name", "watch_count"]}


def create_mongo_indexes(database):
    # MongoDB automatically indexes _id and req it to be unique
    # Additional indexes will allow MongoDB to locate our field values better.
    for dataset in DATASETS:
        myCollection = database[dataset]
        for field in MONGO_SEARCH_FIELDS[dataset]:
            myCollection.create_index(field)


def connect_to_mongodb():
    print("Connecting to local Mongo database...")

    # using localhost:27017
    connection_address = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    myClient = pymongo.MongoClient(connection_address, serverSelectionTimeoutMS=5000)

    try:
        #testing the connection and  then get into our given database.
        myClient.admin.command("ping")
        db = myClient["group2_github_archive"]
        create_mongo_indexes(db)
        print("MongoDB connection successful.")
        return db

    except pymongo.errors.PyMongoError as error:
        myClient.close()
        print("Unable to connect to MongoDB or create indexes:", error)
        return None


def watch_count_number(value):
    # the archive is storing watch_count as text. MongoDB stores whole number.
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("Watch count must be a whole number.")
    number = int(value)
    if number < 0:
        raise ValueError("Watch count cannot be negative.")
    return number


def prepare_mongo_record(record, dataset):
    record_key = make_record_key(record, dataset)
    if record_key is None:
        raise ValueError("The identifying fields are either missing or empty.")
    document = record.copy()
    # Reuse of the same stable ID so re-importing doesn't create dupes
    document["_id"] = record_key
    if dataset == "Sample_Repos":
        document["watch_count"] = watch_count_number(document.get("watch_count"))
    return document


def mongo_import_archive(database):
    file_path, action = get_user_input("Enter the path to an extracted JSON file")
    if action != "continue":
        return action
    dataset = os.path.splitext(os.path.basename(file_path))[0]
    if dataset not in DATASETS:
        dataset, action = choose_dataset()
        if action != "continue":
            return action
    while True:
        limit_text, action = get_user_input("Maximum records to read [100]")
        if action != "continue":
            return action
        if limit_text == "":
            maximum_records = 100
            break
        if limit_text.isdigit() and int(limit_text) > 0:
            maximum_records = int(limit_text)
            break
        print("Enter a whole number greater than zero.")
    try:
        records = read_archive_file(file_path, maximum_records)
    except (OSError, UnicodeError) as error:
        print("The archive could not be read:", error)
        return option_finished()

    myCollection = database[dataset]
    new_records = 0
    duplicate_records = 0
    invalid_records = 0
    for record in records:
        try:
            document = prepare_mongo_record(record, dataset)
        except (ValueError, TypeError):
            invalid_records += 1
            continue
        try:
            # CREATE: insert_one saves one dictionary as a document.
            myCollection.insert_one(document)
            new_records += 1
        except pymongo.errors.DuplicateKeyError:
            duplicate_records += 1
    print(f"{len(records)} records were processed from {dataset}.")
    print("New records:", new_records)
    print("Duplicate records:", duplicate_records)
    print("Invalid records:", invalid_records)
    return option_finished()


def mongo_create_record(database):
    new_record, dataset, action = collect_new_record()
    if action != "continue":
        return action
    try:
        document = prepare_mongo_record(new_record, dataset)
    except (ValueError, TypeError) as error:
        print("Invalid record:", error)
        return option_finished()
    print(json.dumps(document, indent=2))
    confirmation, action = get_user_input("Enter Y to save or N to cancel")
    if action != "continue":
        return action
    if confirmation.upper() == "Y":
        try:
            myCollection = database[dataset]
            myCollection.insert_one(document)
            print("Document created. Record ID:", document["_id"])
        except pymongo.errors.DuplicateKeyError:
            print("A document with that ID already exists.")
    else:
        print("Create canceled.")
    return option_finished()


def choose_mongo_record(database):
    dataset, action = choose_dataset()
    if action != "continue":
        return None, None, action
    record_id, action = get_user_input("Paste the full Record ID shown by Search")
    if action != "continue":
        return None, None, action
    # find_one returns a dictionary, or None if no document matches.
    myCollection = database[dataset]
    query = {"_id": record_id}
    document = myCollection.find_one(query)
    return dataset, document, "continue"


def mongo_read_record(database):
    dataset, document, action = choose_mongo_record(database)
    if action != "continue":
        return action
    if document is None:
        print("Document not found in that dataset.")
    else:
        print(json.dumps(document, indent=2))
    return option_finished()


def mongo_update_record(database):
    dataset, document, action = choose_mongo_record(database)
    if action != "continue":
        return action
    if document is None:
        print("Document not found.")
        return option_finished()
    print(json.dumps(document, indent=2))
    field, action = get_user_input("Enter an existing top-level field to change")
    if action != "continue":
        return action
    if field == "_id" or field in KEY_FIELDS[dataset]:
        print("Identifying fields cannot be changed. Create a new record instead.")
        return option_finished()
    if field not in document or "." in field or field.startswith("$"):
        print("Choose an existing top-level field.")
        return option_finished()
    value, action = get_user_input("Enter the new value (use JSON for lists/objects/booleans)")
    if action != "continue":
        return action
    try:
        if dataset == "Sample_Repos" and field == "watch_count":
            value = watch_count_number(value)
        else:
            value = convert_value(value, document[field])
    except (ValueError, TypeError) as error:
        print("Invalid value:", error)
        return option_finished()
    # $set changes this field while preserving the rest of the document.
    myCollection = database[dataset]
    query = {"_id": document["_id"]}
    updateData = {"$set": {field: value}}
    result = myCollection.update_one(query, updateData)
    if result.matched_count == 0:
        print("The document no longer exists.")
    elif result.modified_count == 0:
        print("The field already contains that value.")
    else:
        print("Document updated.")
    return option_finished()


def mongo_delete_record(database):
    dataset, document, action = choose_mongo_record(database)
    if action != "continue":
        return action
    if document is None:
        print("Document not found.")
        return option_finished()
    print("Record ID:", document["_id"])
    confirmation, action = get_user_input("Type DELETE to confirm")
    if action != "continue":
        return action
    if confirmation.upper() == "DELETE":
        myCollection = database[dataset]
        query = {"_id": document["_id"]}
        result = myCollection.delete_one(query)
        print("Documents deleted:", result.deleted_count)
    else:
        print("Delete canceled.")
    return option_finished()


def mongo_search_records(database):
    dataset, action = choose_dataset()
    if action != "continue":
        return action
    print("Search fields:", ", ".join(MONGO_SEARCH_FIELDS[dataset]))
    field, action = get_user_input("Enter a field, or press Enter to list documents")
    if action != "continue":
        return action
    query = {}
    if field:
        if field not in MONGO_SEARCH_FIELDS[dataset]:
            print("Choose one of the listed fields.")
            return option_finished()
        value, action = get_user_input("Enter the exact field value (case-sensitive)")
        if action != "continue":
            return action
        if field == "watch_count":
            value = watch_count_number(value)
        query[field] = value
    # Only retrieve ids for the list larger source-codes will stay in MongoDB.
    myCollection = database[dataset]
    showFields = {"_id": 1}
    data = myCollection.find(query, showFields).limit(25)
    results = []
    for document in data:
        results.append(document)
    if not results:
        print("No matches found.")
        return option_finished()
    print("Showing up to 25 matches:")
    for number, document in enumerate(results, start=1):
        print(number, "Record ID:", document["_id"])
    while True:
        selection, action = get_user_input("Enter a result number to view")
        if action != "continue":
            return action
        if selection.isdigit() and 1 <= int(selection) <= len(results):
            selected_record = results[int(selection) - 1]
            query = {"_id": selected_record["_id"]}
            document = myCollection.find_one(query)
            if document is None:
                print("The document no longer exists.")
            else:
                print(json.dumps(document, indent=2))
            return option_finished()
        print("Choose a number from the results.")


def mongo_group_records(database):
    dataset, action = choose_dataset()
    if action != "continue":
        return action
    field, action = get_user_input("Enter a top-level field such as repo_name, license, or mode")
    if action != "continue":
        return action
    if field == "" or "." in field or field.startswith("$"):
        print("Enter a top-level field name.")
        return option_finished()

    myCollection = database[dataset]
    query = {}
    showFields = {field: 1}
    data = myCollection.find(query, showFields)
    grouped_records = {}

    # Same basic counting loop as the Redis' func used earlier.
    # For  list, whole list is treated as one group value.
    for document in data:
        group_value = str(document.get(field, "Field not found"))
        if group_value not in grouped_records:
            grouped_records[group_value] = 1
        else:
            grouped_records[group_value] += 1

    if len(grouped_records) == 0:
        print("No documents to group.")
    else:
        for group_value in grouped_records:
            print(group_value, ":", grouped_records[group_value])
    return option_finished()


def mongo_export_records(database):
    dataset, action = choose_dataset()
    if action != "continue":
        return action
    output_file, action = get_user_input("Enter an output JSON filename")
    if action != "continue":
        return action
    if os.path.exists(output_file):
        answer, action = get_user_input("Type OVERWRITE to replace the existing file")
        if action != "continue":
            return action
        if answer != "OVERWRITE":
            print("Export canceled.")
            return option_finished()
    count = 0
    # _id: 0 excludes the MongoDB identifier. Import aloows it to exist and be accesible later.
    myCollection = database[dataset]
    query = {}
    showFields = {"_id": 0}
    data = myCollection.find(query, showFields)
    with open(output_file, "w", encoding="utf-8") as output:
        for document in data:
            output.write(json.dumps(document) + "\n")
            count += 1
    print(count, "documents exported. Select", dataset, "when re-importing.")
    return option_finished()

""" we already have 3 aditional features these are 2 extra funcs mr.bellet sparked
these might be snipped out all in all and just added into github as 3 functions in case
we want to use for next project! or if we can get it fired up and running they can just stay!"""
#***----Feat idea "Templates" to display templated forms of full id syntax or other uer inputed requirements to allow user friendly
#view of what to type for the menu options

# FEATURE 1: Find longest and shortest full owner/repository names.
def repository_name_report(database):
    shortest = None
    longest = None
    count = 0
    myCollection = database["Sample_Repos"]
    query = {}
    showFields = {"repo_name": 1, "_id": 0}
    data = myCollection.find(query, showFields)
    for document in data:
        name = document.get("repo_name")
        if not isinstance(name, str) or not name:
            continue
        count += 1
        # Keep one example of the shortest and longest names found.
        if shortest is None or len(name) < len(shortest):
            shortest = name
        if longest is None or len(name) > len(longest):
            longest = name
    if count == 0:
        print("Import Sample_Repos.json first.")
    else:
        print("Imported repository names examined:", count)
        print("Shortest:", shortest, "-", len(shortest), "characters")
        print("Longest:", longest, "-", len(longest), "characters")
        print("Lengths include owner/ and repository. The first name found is shown for ties.")
    return option_finished()


# FEATURE 2: Watch-count distribution and the top ten imported repositories.
def watch_count_report(database):
    myCollection = database["Sample_Repos"]
    if myCollection.count_documents({}) == 0:
        print("Import Sample_Repos.json first.")
        return option_finished()

    print("Watch-count distribution of imported Sample_Repos:")
    ranges = [(0, 9), (10, 99), (100, 999), (1000, 9999)]
    for minimum, maximum in ranges:
        # $gte is greater than or equal; $lte is less than or equal.
        query = {"watch_count": {"$gte": minimum, "$lte": maximum}}
        count = myCollection.count_documents(query)
        print(f"{minimum}-{maximum}: {count} repositories")

    query = {"watch_count": {"$gte": 10000}}
    count = myCollection.count_documents(query)
    print("10000+:", count, "repositories")

    print("Top 10 by watch count:")
    query = {}
    showFields = {"_id": 0, "repo_name": 1, "watch_count": 1}
    data = myCollection.find(query, showFields)
    # -1 sorts largest first; limit(10) displays up to ten documents.
    data = data.sort("watch_count", -1).limit(10)
    for document in data:
        print(document["repo_name"], ":", document["watch_count"])
    return option_finished()


# FEATURE 3: Count the most common words in imported commit messages.
def commit_word_report(database):
    dataset, action = get_user_input("Enter Commits or Sample_Commits")
    if action != "continue":
        return action
    if dataset not in ["Commits", "Sample_Commits"]:
        print("Choose one of the two commit datasets.")
        return option_finished()
    repository, action = get_user_input("Exact repo_name to filter, or Enter for all imported commits")
    if action != "continue":
        return action
    query = {}
    if repository:
        # Matches a scalar Sample_Commits.repo_name or an element of Commits.repo_name.
        # The repo_name index works with the filter also.
        query["repo_name"] = repository
    counts = {}
    messages = 0
    ignored = {"the", "and", "for", "with", "this", "that", "from", "into", "to", "of", "in", "is", "a", "an"}
    myCollection = database[dataset]
    showFields = {"message": 1, "_id": 0}
    data = myCollection.find(query, showFields)
    for document in data:
        message = document.get("message")
        if not isinstance(message, str):
            continue
        messages += 1
        # Splits at whitespaces/remove punctuation from each word's edges.
        # the punctuation INSIDE words still stays, ex. bug-fix will count as one word due to the dash withiin singular word syntax.
        for word in message.lower().split():
            word = word.strip(".,!?;:()[]{}\"'")
            if len(word) < 2 or word in ignored:
                continue
            if word not in counts:
                counts[word] = 1
            else:
                counts[word] += 1
    print("Imported commit messages examined:", messages)
    if not counts:
        print("No words to report. Import a commit dataset or check the filter.")
    else:
        print("Top 10 words (occurrences; common connecting words omitted):")
        # Sort by each word's count, largest first, and keep ten words.
        sorted_words = sorted(counts, key=counts.get, reverse=True)
        top_words = sorted_words[:10]
        for word in top_words:
            print(word, ":", counts[word])
    return option_finished()
            
def Help():
    print()
    print("1. Templates")
    print("2. FAQ")

    HelpChoice, action = get_user_input("Enter 1 for Templates or 2 for FAQ: ")
    if action !="continue":
        return action

    if HelpChoice == "1":
        print()
        print("Templates")
        print("Full record ID input Reference: github:archive:Sample_Repos:[IDENTIFYING_VALUE]")
        print("Repository full record ID reference: github:archive:Sample_Repos:[OWNER/REPOSITORY]")
        return option_finished()

    elif HelpChoice == "2":
        print()
        print("FAQ")
        print("Question 1: How to import files?")
        print("Question 2: Why doesn't pymongo work?")

        QuestionChoice, action = get_user_input("Enter 1 or 2")
        if action != "continue":
            return action

        if QuestionChoice == "1":
            print("When importing files or archives, verify the full path to ensure proper records are imported into MongoDB. The current archive used in MongoDB Compass is set as group2_github_archive.")
            print("If you want this changed, locate connect_to_mongodb() and modify the database name or connection address.")
            return option_finished()
        
        elif QuestionChoice == "2":
            print("Please verify that you have the imports installed using: python -m pip install redis pymongo")
            return option_finished()

        else:
            print("Error: Enter 1 or 2, B to return to the database menu, or E to exit.")

    else:
        print("Error: Enter 1 or 2, B to return to the database menu, or E to exit.")



def mongodb_menu():
    database = connect_to_mongodb()
    if database is None:
        print("Please start MongoDB and run the program again.")
        return
    app_cont = True
    try:
        while app_cont:
            display_menu()
            print("Database: MongoDB additional features.")
            print("9) Longest and shortest repository names")
            print("10) Watch-count distribution and top repositories")
            print("11) Most common commit-message words")
            print("12) FAQ Help")
            choice = input("Please select an option: ").strip()
            result = None
            try:
                if choice == "1":
                    result = mongo_import_archive(database)
                elif choice == "2":
                    result = mongo_create_record(database)
                elif choice == "3":
                    result = mongo_read_record(database)
                elif choice == "4":
                    result = mongo_update_record(database)
                elif choice == "5":
                    result = mongo_delete_record(database)
                elif choice == "6":
                    result = mongo_search_records(database)
                elif choice == "7":
                    result = mongo_group_records(database)
                elif choice == "8":
                    result = mongo_export_records(database)
                elif choice == "9":
                    result = repository_name_report(database)
                elif choice == "10":
                    result = watch_count_report(database)
                elif choice == "11":
                    result = commit_word_report(database)
                elif choice == "12":
                    result = Help()
                elif choice == "0":
                    app_cont = False
                else:
                    print("Enter a number from 0 through 11.")
            except (pymongo.errors.PyMongoError, OSError, ValueError, TypeError) as error:
                print("Operation stopped:", error)
                print("Any documents or exported lines already written will remain saved.")
                result = option_finished()
            if result == "exit":
                app_cont = False
    finally:
        database.client.close()
    print("MongoDB session ended.")


def main():
    while True:
        print("\nCHOOSE DATABASE")
        print("1) Redis")
        print("2) MongoDB")
        print("0) Exit Application")
        choice = input("Select a database: ").strip().upper()
        if choice == "1":
            redis_menu()
            break
        elif choice == "2":
            mongodb_menu()
            break
        elif choice in ["0", "E"]:
            break
        else:
            print("Enter 1, 2, or 0.")
    print("APPLICATION EXITED. GOODBYE.")


if __name__ == "__main__":
    main()
