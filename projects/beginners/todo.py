# Todo Application

# Importing Modules
import os
import time
import sys
import datetime


# Defining Functions
def add_task():
    print("Add Task")
    print("---------")
    task = input("Enter Task: ")
    with open("todo.txt", "a") as f:
        f.write(task + "\n")
    print("Task Added Successfully.")
    
def view_task():
    print("View Task")
    print("---------")
    with open("todo.txt", "r") as f:
        tasks = f.readlines()
        if len(tasks) == 0:
            print("No Tasks Found.")
        else:
            for i in range(len(tasks)):
                print(str(i + 1) + ". " + tasks[i].strip("\n"))
                
def delete_task():
    print("Delete Task")
    print("------------")
    with open("todo.txt", "r") as f:
        tasks = f.readlines()
        if len(tasks) == 0:
            print("No Tasks Found.")
        else:
            for i in range(len(tasks)):
                print(str(i + 1) + ". " + tasks[i].strip("\n"))
            task_no = int(input("Enter Task Number to Delete: "))
            if task_no > len(tasks):
                print("Invalid Task Number.")
            else:
                del tasks[task_no - 1]
                with open("todo.txt", "w") as f:
                    for task in tasks:
                        f.write(task)
                print("Task Deleted Successfully.")
                
def delete_all_task():
    print("Delete All Task")
    print("----------------")
    with open("todo.txt", "r") as f:
        tasks = f.readlines()
        if len(tasks) == 0:
            print("No Tasks Found.")
        else:
            for i in range(len(tasks)):
                print(str(i + 1) + ". " + tasks[i].strip("\n"))
            confirm = input("Are you sure you want to delete all tasks? (Y/N): ")
            if confirm in ("Y", "y"):
                with open("todo.txt", "w") as f:
                    f.write("")
                print("All Tasks Deleted Successfully.")
            elif confirm in ("N", "n"):
                print("No Tasks Deleted.")
            else:
                print("Invalid Choice.")
                
def exit():
    print("Exit")
    print("-----")
    confirm = input("Are you sure you want to exit? (Y/N): ")
    if confirm in ("Y", "y"):
        print("Exiting...")
        time.sleep(1)
        sys.exit()
    elif confirm in ("N", "n"):
        print("Not Exiting.")
    else:
        print("Invalid Choice.")
        
def restart():
    print("Restart")
    print("--------")
    confirm = input("Are you sure you want to restart? (Y/N): ")
    if confirm in ("Y", "y"):
        print("Restarting...")
        time.sleep(1)
        os.system("python todo.py")
    elif confirm in ("N", "n"):
        print("Not Restarting.")
    else:
        print("Invalid Choice.")
        
def help():
    print("Help")
    print("----")
    print("Add Task: Add a task to the todo list.")
    print("View Task: View all tasks in the todo list.")
    print("Delete Task: Delete a task from the todo list.")
    print("Delete All Task: Delete all tasks from the todo list.")
    print("Exit: Exit the application.")
    print("Restart: Restart the application.")
    print("Help: View help.")
    

# Main Program
print("Todo Application")
print("----------------")
print("Select Operation.")
print("1. Add Task")
print("2. View Task")
print("3. Delete Task")
print("4. Delete All Task")
print("E. Exit")
print("R. Restart")
print("H. Help")

while True:
    choice = input("Enter Choice (1/2/3/4/E/R/H): ")
    
    if choice == "1":
        add_task()
    elif choice == "2":
        view_task()
    elif choice == "3":
        delete_task()
    elif choice == "4":
        delete_all_task()
    elif choice.upper() == "E":
        exit()
    elif choice.upper() == "R":
        restart()
    elif choice.upper() == "H":
        help()
    else:
        print("Invalid Choice.")