# helping_functions.py


import json
from datetime import datetime


def save_data(data):
    try:
        with open('memory.json', 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the data: {e}")


def load_data():
    try:
        with open('memory.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("No file named memory.json found.")
        return []
    except json.JSONDecodeError:
        print("An error occurred while decoding memory.json.")
        return []


# def dict_in_list(title, memory, image=None):
#     data = {
#         "title": title,
#         "description": memory,
#         "date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
#         "image": image
#     }
#     return data


# def memory():
#     while True:
#         print("1. Create new memory")
#         print("2. Load existing memory")
#         print("0. Exit")
#         choice = input("Choose an option: ")
#         if choice == "1":
#             title = input("Enter a name for your memory: ")
#             print('-'*20)
#             memory = input("Enter your memory\n : ")
#             print('-'*20)
#             data = load_data()
#             if data["username"] not in data:
#                 data["username"] = title
#             data[name].append(dict_in_list(memory))
#             save_data(data)
#             print("Saved Successfully.")
#         elif choice == "2":
#             name = input("Enter the name of your memory: ")
#             data = load_data()
#             if name in data:
#                 print('-'*20)
#                 for i in data[name]:
#                     print(f"[{i["memory"]}] => {i["date_release"]}")
#                 print('-'*20)
#                 print("Loaded Successfully.")
#             else:
#                 print(f"No data found for memory.json.")
#         elif choice == "0":
#             break
#         else:
#             print("Invalid choice. Please choose a valid option.")
#     print("Thank You.")


# if __name__ == "__main__":
#     memory()