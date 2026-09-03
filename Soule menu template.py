import redis
import json

r=redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)
    

def main():

    try:
        r.ping()

        print()
        print("Successfully connected to Redis.")

        while True:

            print()
            print("REDIS JSON APPLICATION")
            print("1. Create a new record")
            print("2. Read a record")
            print("3. Update a record")
            print("4. Delete a record")
            print("5. Delete all Redis data")
            print("6. Most active repositories")
            print("7. User contribution history")
            print("8. Database summary")
            print("9. Exit")

            choice = input("Enter menu option: ")

            if choice == "1":
                create_event()

            elif choice == "2":
                read_event()

            elif choice == "3":
                update_event()

            elif choice == "4":
                delete_event()

            elif choice == "5":
                delete_all_data()

            elif choice == "6":
                repository_analysis()

            elif choice == "7":
                user_contribution_history()

            elif choice == "8":
                database_summary()

            elif choice == "9":
                print()
                print("Program closed.")
                break

            else:
                print("Invalid menu option.")

    except redis.exceptions.ConnectionError:

        print()
        print("ERROR: Unable to connect to Redis.")
        print("Make sure your Redis server is running.")


if __name__ == "__main__":
    main()
