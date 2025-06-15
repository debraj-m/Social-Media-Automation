import os

def print_tree(start_path, indent=""):
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        if os.path.isdir(item_path):
            print(indent + "📁 " + item)
            print_tree(item_path, indent + "    ")
        else:
            print(indent + "📄 " + item)

# Replace with the path you want to inspect, or leave it as "." for the current directory
folder_path = "."  # Example: "C:/Users/YourName/Desktop/Project"
print_tree(folder_path)
