# Lucas Justiniano
# 1.6 Group Project - Redis Integration
# Date: September 3, 2026

import json
import os
import redis


# ---------------------------------------------------------
# Redis connection
# ---------------------------------------------------------
def connect_to_redis():
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )

        client.ping()
        print("\nConnected to Redis successfully!")
        return client

    except redis.exceptions.ConnectionError:
        print("\nERROR: Could not connect to Redis.")
        print("Make sure the Redis server is running.")
        return None


# ---------------------------------------------------------
# Import JSON data into Redis
# ---------------------------------------------------------
def import_json_data(client):
    file_path = os.path.expanduser(
        "~/Downloads/GitHubArchive-Dataset/Sample_Repos.json"
    )

    if not os.path.exists(file_path):
        print("\nERROR: Sample_Repos.json was not found.")
        print("Expected location:")
        print(file_path)
        return

    imported = 0

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                repo_name = data.get("repo_name")
                watch_count = data.get("watch_count", "0")

                if repo_name:
                    key = f"repo:{repo_name}"

                    client.hset(
                        key,
                        mapping={
                            "repo_name": repo_name,
                            "watch_count": watch_count
                        }
                    )

                    imported += 1

        print(f"\nImport complete!")
        print(f"{imported} repository records were loaded into Redis.")

    except Exception as error:
        print("\nAn error occurred while importing the data:")
        print(error)


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------
def create_repository(client):
    print("\n--- CREATE REPOSITORY ---")

    repo_name = input("Enter repository name: ").strip()
    watch_count = input("Enter watch count: ").strip()

    if not repo_name:
        print("Repository name cannot be empty.")
        return

    key = f"repo:{repo_name}"

    if client.exists(key):
        print("That repository already exists.")
        return

    client.hset(
        key,
        mapping={
            "repo_name": repo_name,
            "watch_count": watch_count
        }
    )

    print("Repository created successfully.")


# ---------------------------------------------------------
# READ
# ---------------------------------------------------------
def read_repository(client):
    print("\n--- READ REPOSITORY ---")

    repo_name = input("Enter repository name: ").strip()
    key = f"repo:{repo_name}"

    repository = client.hgetall(key)

    if repository:
        print("\nRepository found:")
        print(f"Repository Name: {repository.get('repo_name')}")
        print(f"Watch Count: {repository.get('watch_count')}")
    else:
        print("Repository not found.")


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------
def update_repository(client):
    print("\n--- UPDATE REPOSITORY ---")

    repo_name = input("Enter repository name: ").strip()
    key = f"repo:{repo_name}"

    if not client.exists(key):
        print("Repository not found.")
        return

    new_watch_count = input("Enter the new watch count: ").strip()

    client.hset(key, "watch_count", new_watch_count)

    print("Repository updated successfully.")


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------
def delete_repository(client):
    print("\n--- DELETE REPOSITORY ---")

    repo_name = input("Enter repository name: ").strip()
    key = f"repo:{repo_name}"

    if client.delete(key):
        print("Repository deleted successfully.")
    else:
        print("Repository not found.")


# ---------------------------------------------------------
# FEATURE 1
# Show most watched repositories
# ---------------------------------------------------------
def most_watched_repositories(client):
    print("\n--- FEATURE 1: MOST WATCHED REPOSITORIES ---")

    repositories = []

    for key in client.scan_iter("repo:*"):
        data = client.hgetall(key)

        try:
            watch_count = int(data.get("watch_count", 0))
        except ValueError:
            watch_count = 0

        repositories.append(
            (
                data.get("repo_name", "Unknown"),
                watch_count
            )
        )

    if not repositories:
        print("No repository data is available.")
        return

    repositories.sort(
        key=lambda item: item[1],
        reverse=True
    )

    print("\nTop 10 Most Watched Repositories:")

    for number, repository in enumerate(
        repositories[:10],
        start=1
    ):
        print(
            f"{number}. {repository[0]} "
            f"- {repository[1]} watchers"
        )


# ---------------------------------------------------------
# FEATURE 2
# Search repositories by keyword
# ---------------------------------------------------------
def search_repositories(client):
    print("\n--- FEATURE 2: SEARCH REPOSITORIES ---")

    keyword = input(
        "Enter a keyword to search for: "
    ).strip().lower()

    if not keyword:
        print("Search keyword cannot be empty.")
        return

    matches = []

    for key in client.scan_iter("repo:*"):
        data = client.hgetall(key)

        repo_name = data.get("repo_name", "")

        if keyword in repo_name.lower():
            matches.append(data)

    if not matches:
        print("No matching repositories were found.")
        return

    print(f"\nRepositories containing '{keyword}':")

    for number, repo in enumerate(
        matches[:20],
        start=1
    ):
        print(
            f"{number}. "
            f"{repo.get('repo_name')} "
            f"- Watch Count: "
            f"{repo.get('watch_count')}"
        )

    if len(matches) > 20:
        print(
            f"\nShowing 20 of "
            f"{len(matches)} matching repositories."
        )


# ---------------------------------------------------------
# FEATURE 3
# Repository statistics
# ---------------------------------------------------------
def repository_statistics(client):
    print("\n--- FEATURE 3: REPOSITORY STATISTICS ---")

    total_repositories = 0
    total_watchers = 0
    highest_watch_count = 0
    highest_repo = ""

    for key in client.scan_iter("repo:*"):
        data = client.hgetall(key)

        total_repositories += 1

        try:
            watch_count = int(
                data.get("watch_count", 0)
            )
        except ValueError:
            watch_count = 0

        total_watchers += watch_count

        if watch_count > highest_watch_count:
            highest_watch_count = watch_count
            highest_repo = data.get(
                "repo_name",
                "Unknown"
            )

    if total_repositories == 0:
        print("No repository data is available.")
        return

    average_watchers = (
        total_watchers / total_repositories
    )

    print(
        f"Total repositories in Redis: "
        f"{total_repositories}"
    )

    print(
        f"Total watch count: "
        f"{total_watchers}"
    )

    print(
        f"Average watch count: "
        f"{average_watchers:.2f}"
    )

    print(
        f"Most watched repository: "
        f"{highest_repo}"
    )

    print(
        f"Highest watch count: "
        f"{highest_watch_count}"
    )


# ---------------------------------------------------------
# Display database count
# ---------------------------------------------------------
def show_record_count(client):
    count = 0

    for _ in client.scan_iter("repo:*"):
        count += 1

    print(
        f"\nThere are currently "
        f"{count} repository records in Redis."
    )


# ---------------------------------------------------------
# Main menu
# ---------------------------------------------------------
def display_menu():
    print("\n======================================")
    print("      GITHUB ARCHIVE REDIS APP")
    print("======================================")
    print("1. Import GitHub Archive JSON Data")
    print("2. Create Repository")
    print("3. Read Repository")
    print("4. Update Repository")
    print("5. Delete Repository")
    print("6. Show Most Watched Repositories")
    print("7. Search Repositories")
    print("8. Show Repository Statistics")
    print("9. Show Redis Record Count")
    print("0. Exit")
    print("======================================")


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------
def main():
    client = connect_to_redis()

    if client is None:
        return

    while True:
        display_menu()

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":
            import_json_data(client)

        elif choice == "2":
            create_repository(client)

        elif choice == "3":
            read_repository(client)

        elif choice == "4":
            update_repository(client)

        elif choice == "5":
            delete_repository(client)

        elif choice == "6":
            most_watched_repositories(client)

        elif choice == "7":
            search_repositories(client)

        elif choice == "8":
            repository_statistics(client)

        elif choice == "9":
            show_record_count(client)

        elif choice == "0":
            print("\nThank you for using the Redis application.")
            print("Program ended.")
            break

        else:
            print(
                "\nInvalid choice. "
                "Please select an option from the menu."
            )


if __name__ == "__main__":
    main()
