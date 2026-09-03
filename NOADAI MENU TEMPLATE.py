from datetime import datetime

def function1( , ):

def function2( , ):

def function3( , ):
    
# main serves as the menu and branching options for the user end display and interaction.
def main():
    student_id = "NOADAI5500"

    menu_options = [
        "1 op 1",
        "2 op 2",
        "3 op 3",
        "4 Exit Menu"]

    app_cont = True

    while app_cont:

        print()
        print(student_id + "Group2's  Menu")
        print("Choose a number from the following options:")

        # Nested for-loop displays the menu options
        for option in menu_options:
            print(option)

        choice = input("Enter your choice: ")

        if choice == "1" or choice == "2" or choice == "3":
            current_date_time = datetime.now()
            print("You selected", choice, "at", current_date_time)
            
             # inputting 1  will call getInput, 2 calls viewdata showing current csv data and 3 will currently display the not implemented error.
            if choice == "1":
                menuPath1(##fillFunction)

            elif choice == "2":
                menuPath2(##fillFunction)

           elif choice == "3":
                menuPath3(##fillFunction)
                
            # user input for back or exit
            return_choice = input(
                "Enter B to go back to the menu or E to exit: ")

            while return_choice.upper() != "B" and return_choice.upper() != "E":
                print("Error: Invalid choice selected.")
                return_choice = input(
                    "Enter B to go back to the menu or E to exit: ")

            if return_choice.upper() == "E":
                app_cont = False

        elif choice == "4":
            app_cont = False

        else:
            print("Error: Invalid option selected.")

    print("APPLICATION EXITED. GOODBYE.")

main()


