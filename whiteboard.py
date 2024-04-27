from tkinter import *
from threading import Thread
import threading, socket, sys, os

root = Tk()
root.title("Whiteboard")
root.geometry("1000x1000")

my_canvas = Canvas(root, width=1000, height=1000, bg="white")
my_canvas.pack()

# VARIABLES

action_history_list = []

# boolean values for tool selection
isLine = False
isRect = False
isCircle = False
isText = False

# default colour is black (in hex)
colour = "#000000"

# variables for drawing
draw_list = []
draw_id = 0
my_select = "none"

# UTILITY FUNCTIONS

# function to convert from rgb values to a hex value
def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

#function to check tool type
def check_drawing_type(canvas, item_id):
    tags = canvas.gettags(item_id)
    if "line" in tags:
        return "line"
    if "circle" in tags:
        return "circle"
    elif "rectangle" in tags:
        return "rectangle"
    elif "text" in tags:
        return "text"
    else:
        return "unknown"

# MAIN FUNCTIONS

def output_help():
    print("Welcome to the CLI Help!")
    print("help: lists all available commands and their usage")
    print("tool {line | rectangle | circle | text}: selects a tool for drawing")
    print("colour {RGB}}: sets the drawing colour using rgb values")
    print("draw {parameters}: draws with the currently selected tool")
    print("list {all | line | rectangle | circle | text} {all | mine}: displays issued draw commands")
    print("select {none | ID}: selects an existing draw command to be modified by a subsequent draw command")
    print("delete {ID}: deletes the draw command with the specified ID")
    print("undo: reverts the user's last action")
    print("clear {all | mine}: clears the whiteboard")
    print("show {all | mine}: controls what is displayed on the client's canvas")
    print("exit: disconnects from the server and exits the application")

def set_tool(my_input):
    global isLine, isRect, isCircle, isText
    tool = my_input.split("tool ")[1]
    if(tool == "line"):
        isRect = isCircle = isText = False
        isLine = True
    elif(tool == "rectangle"):
        isLine = isCircle = isText = False
        isRect = True
    elif(tool == "circle"):
        isLine = isRect = isText = False
        isCircle = True
    elif(tool == "text"):
        isLine = isCircle = isRect = False
        isText = True
    else:
        print("This tool does not exist! Pick from line/rectangle/circle/text.")

def set_colour(my_input):

    global colour, my_select

    rgb_values = my_input.split("colour ")[1]
    rgb_list = rgb_values.split(" ")
    colour_code = rgb_to_hex(int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))
    colour = colour_code

    if my_select != "none":
        my_canvas.itemconfig(int(my_select), fill=colour)

def draw(my_input):

    global isLine, isRect, isCircle, isText, my_select, draw_list, draw_id

    coords = my_input.split("draw ")[1]
            
    # check which tool is selected
    if isLine or isRect or isCircle:
        coords_list = coords.split()
        coords_list = [int(x) for x in coords_list]

        if(isLine):
            if my_select != "none":
                my_canvas.coords(int(my_select), coords_list[0],coords_list[1], coords_list[2], coords_list[3])
                index = None
                for i, pair in enumerate(draw_list):
                    if pair[0] == int(my_select):
                        index = i
                        break
                draw_list[index] = (int(my_select), coords_list)
            else:
                draw_id = my_canvas.create_line(coords_list[0],coords_list[1], coords_list[2], coords_list[3], fill=colour)
                my_canvas.itemconfig(draw_id, tags=("line",))
                draw_list.append((draw_id, coords_list))
        elif(isRect):
            if my_select != "none":
                my_canvas.coords(int(my_select), coords_list[0],coords_list[1], coords_list[2], coords_list[3])
                index = None
                for i, pair in enumerate(draw_list):
                    if pair[0] == int(my_select):
                        index = i
                        break
                draw_list[index] = (int(my_select), coords_list)
            else:
                draw_id = my_canvas.create_rectangle(coords_list[0],coords_list[1], coords_list[2], coords_list[3], fill=colour)
                my_canvas.itemconfig(draw_id, tags=("rectangle",))
                draw_list.append((draw_id, coords_list))
        elif(isCircle):
            if my_select != "none":
                my_canvas.coords(int(my_select), coords_list[0],coords_list[1], coords_list[2], coords_list[3])
                index = None
                for i, pair in enumerate(draw_list):
                    if pair[0] == int(my_select):
                        index = i
                        break
                draw_list[index] = (int(my_select), coords_list)
            else:
                draw_id = my_canvas.create_oval(coords_list[0],coords_list[1], coords_list[2], coords_list[3], fill=colour)
                my_canvas.itemconfig(draw_id, tags=("circle",))
                draw_list.append((draw_id, coords_list))
    elif(isText):
        start_index = coords.find('"')
        end_index = coords.rfind('"')

        if start_index != -1 and end_index != -1:
            # Extract x, y coordinates
            coords_and_text = coords[:start_index].split()

            if len(coords_and_text) == 2:
                my_x, my_y = coords_and_text
                my_x = int(my_x)
                my_y = int(my_y)
                coords_list = [my_x,my_y]
                # Extract the text within inverted commas
                my_text = coords[start_index+1:end_index]

                coords_and_text = [my_x,my_y,my_text]

                if my_select != "none":
                    my_canvas.itemconfig(int(my_select), text=my_text)
                    my_canvas.coords(int(my_select), my_x, my_y)
                    index = None
                    for i, pair in enumerate(draw_list):
                        if pair[0] == int(my_select):
                            index = i
                            break
                    draw_list[index][1] = coords_and_text
                else:
                    draw_id = my_canvas.create_text(my_x, my_y, text=my_text, fill=colour, font=("Arial", 14))
                    my_canvas.itemconfig(draw_id, tags=("text",))
                    draw_list.append((draw_id, coords_and_text))

            else:
                print("Error: Coordinates should consist of exactly two values.")
        else:
            print("Error: Text should be enclosed in inverted commas.")
 
    if my_select != "none":
        print("Resetting select...")
        my_select ="none"

    print("Drawings: " + ", ".join(map(str, draw_list)))

def show_drawings(my_input):
    show_split = my_input.split("show ")
    # Checking if the split operation found the delimiter
    if len(show_split) < 2:
        print("Invalid input! Please input user (all/mine).")
    else:
        user = show_split[1]
        if user == "all":
            print("Showing all drawings...")
        elif user == "mine":
            print("Showing only your drawings...")
        else:
            print("Invalid input! Please input 'all' or 'mine'.")

def list_drawings(my_input):

    global draw_list

    # Splitting the string based on "list"
    split_input = my_input.split("list ")

    # Checking if the split operation found the delimiter
    if len(split_input) < 2:
        print("Invalid input! Please input both tool type (all/rectangle/circle/text) and user (all/mine).")
    else:
        type_and_owner = split_input[1]
        if not type_and_owner:
            print("Please input tool type and user.")
        else:
            type_and_owner_list = type_and_owner.split(" ")
            if len(type_and_owner_list) < 2:
                print("Please input both tool type (all/rectangle/circle/text) and user (all/mine).")
            else:
                tool_type = type_and_owner_list[0]
                owner = type_and_owner_list[1]

                # check tool type
                if(tool_type == "all"):
                    print("Listing all draw commands...")
                    print(draw_list)
                    for pair in draw_list:
                        id = pair[0]
                        type = check_drawing_type(my_canvas, id)
                        print("[",id-1,"] => [", type, "]", draw_list[id-1][1])
                elif(tool_type == "line"):
                    print("Listing line draw commands...")
                    for pair in draw_list:
                        id = pair[0]
                        if check_drawing_type(my_canvas, id) == "line":
                            print("[",id-1,"] => [line]", draw_list[id-1][1])
                elif(tool_type == "rectangle"):
                    print("Listing rectangle draw commands...")
                    for pair in draw_list:
                        id = pair[0]
                        if check_drawing_type(my_canvas, id) == "rectangle":
                            print("[",id-1,"] => [rectangle]", draw_list[id-1][1])
                elif(tool_type == "circle"):
                    print("Listing circle draw commands...")
                    for pair in draw_list:
                        id = pair[0]
                        if check_drawing_type(my_canvas, id) == "circle":
                            print("[",id-1,"] => [circle]", draw_list[id-1][1])
                elif(tool_type == "text"):
                    print("Listing text draw commands...")
                    for pair in draw_list:
                        id = pair[0]
                        if check_drawing_type(my_canvas, id) == "text":
                            print("[",id-1,"] => [text]", draw_list[id-1][1])
                else:
                    print("Invalid tool type! Please type 'all'/'rectangle'/'circle'/'text'.")
                
                # check user
                if(owner == "all"):
                    print("Listing all users commands...")
                elif(owner == "mine"):
                    print("Listing your commands...")
                else:
                    print("Invalid user! Please type 'all' or 'mine'.")

def select_drawing(my_input):

    global draw_list, my_select

    select_split = my_input.split("select ")
    # Checking if the split operation found the delimiter
    if len(select_split) < 2:
        print("Invalid input! Please input 'none' or a valid drawing ID.")
    else:
        my_select = select_split[1]
        if my_select == "none":
            print("Select operation cancelled.")
        else:
            found = False
            for pair in draw_list:
                if int(my_select) == pair[0]:
                    found = True
                    print(f"Selecting {my_select} with command {pair[1]}...")
                    break

            if not found:
                print("Invalid input! Please input a valid drawing ID.")

def undo_action():

    global action_history_list, colour, my_select, draw_list

    # Removes the last ACTION (draw, select, colour, show)
    action_before_last = action_history_list[len(action_history_list) - 2]
    if "draw" in action_before_last:
        print("Erasing drawing...")
        my_canvas.delete(draw_list[-1][0]) # remove from canvas
        del draw_list[len(draw_list)-1] # remove from draw_list
    if "select" in action_before_last:
        print("Reverting select back to none...")
        my_select = "none"
    if "colour" in action_before_last:
        print("Resetting to default colour...")
        colour = "#000000"
        if "select" in action_history_list[len(action_history_list) - 3]:
            my_canvas.itemconfig(int(my_select), fill=colour)

def delete_drawing(my_input):
    
    global draw_list

    delete_split = my_input.split("delete ")
    # Checking if the split operation found the delimiter
    if len(delete_split) < 2:
        print("Invalid input! Please input a valid drawing ID.")
    else:
        confirm_delete = input("Are you sure you want to delete this drawing? Warning: action cannot be reversed! (y/n)")
        if confirm_delete == "y":
            delete_id = int(delete_split[1])
            found = False
            for pair in draw_list:
                if delete_id == pair[0]:
                    found = True
                    print(f"Deleting drawing {delete_id}...")
                    draw_list.remove(pair) # remove from draw_list
                    my_canvas.delete(delete_id) # remove from canvas
                    print("Updated draw list: ", draw_list)
                    break
            if not found:
                print("Invalid input! Please input a valid drawing ID.") 
        elif confirm_delete == "n":
            print("Delete operation cancelled.")
        else:
            print("Invalid input! Please type 'y' for yes or 'n' for no.")

def clear_whiteboard(my_input):
    
    global draw_list

    split_input = my_input.split("clear ")
    # Checking if the split operation found the delimiter
    if len(split_input) < 2:
        print("Invalid input! Please input user (all/mine).")
    else:
        user = split_input[1]
        if user == "all":
            my_confirmation = input("Are you sure you want to delete users' drawings? Warning: action cannot be reversed! (y/n)")
            if my_confirmation.lower() == "y":
                print("Deleting users' drawings...")
                draw_list = [] # reset draw_list
                my_canvas.delete("all")
            else: 
                print("Deletion operation cancelled.")
        elif user == "mine":
            print("Deleting your drawings...")
            draw_list = [] #reset draw_list
        else:
            print("Invalid input! Please input 'all' or 'mine'.")

def exit_whiteboard():
    print("Exiting whiteboard...")
    root.quit()
    os._exit(1)

def receive_commands(sock):
    global isLine, isRect, isCircle, isText, colour, draw_list, draw_id, my_select

    while True:

        data = sock.recv(1024)
        if not data:
            break

        response = data.decode()
        stripped_response = response.rstrip()

        if response.startswith("HTTP/1.1 400 Bad Request"):
            print("Oops... looks like you're not connected to the server properly!")

        commands_list = stripped_response.split("\n")

        # load all commands in server
        for i in range(len(commands_list)):
            # check input for valid commands
            if("tool" in commands_list[i]):
                set_tool(commands_list[i])
            elif("colour" in commands_list[i]):
                set_colour(commands_list[i])
            elif("draw" in commands_list[i]):
                draw(commands_list[i])
            elif("list" in commands_list[i]):
                list_drawings()
            elif("select" in commands_list[i]):
                select_drawing(commands_list[i])
            elif("delete" in commands_list[i]):
                delete_drawing(commands_list[i])
            elif("undo" in commands_list[i]):
                undo_action()
            elif("clear" in commands_list[i]):
                clear_whiteboard(commands_list[i])
            elif("show" in commands_list[i]):
                show_drawings()

def cli_loop():

    global isLine, isRect, isCircle, isText, colour, draw_list, draw_id, my_select

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Extract IP address and port number from command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python whiteboard.py <server_ip> <server_port>")
        exit_whiteboard()
 
    # Check if server_port is a valid integer
    try:
        server_port = int(sys.argv[2])
    except ValueError:
        print("Error: port must be an integer.")
        exit_whiteboard()

    # Check if server_port is within the valid port range
    if not (0 < server_port < 65536):
        print("Error: port must be between 1 and 65535.")
        exit_whiteboard()

    # Check if server_ip is a valid IPv4 address
    try:
        server_ip = sys.argv[1]
        socket.inet_aton(server_ip)
    except socket.error:
        print("Error: ip address is not a valid IPv4 address.")
        exit_whiteboard()

    # Connect to server
    server_address = (server_ip, server_port)
    client_socket.connect(server_address)

    threading.Thread(target=receive_commands, args=(client_socket,)).start()

    while True:

        my_input = input("Enter a command: ").strip()
        action_history_list.append(my_input)
        client_socket.sendall(my_input.encode())

        # check input for valid commands
        if(my_input == "help"):
            output_help()
        elif("tool" in my_input):
            set_tool(my_input)
        elif("colour" in my_input):
            set_colour(my_input)
        elif("draw" in my_input):
            draw(my_input)
        elif("list" in my_input):
            list_drawings()
        elif("select" in my_input):
            select_drawing(my_input)
        elif("delete" in my_input):
            delete_drawing(my_input)
        elif("undo" in my_input):
            undo_action()
        elif("clear" in my_input):
            clear_whiteboard(my_input)
        elif("show" in my_input):
            show_drawings()
        elif(my_input == "exit"):
            print("Disconnecting from server...")
            client_socket.close()
            break
        else:
            print("Invalid command! Type 'help' for more command list.")
            break
    exit_whiteboard()

# Start the CLI loop in a separate thread
cli_thread = Thread(target=cli_loop)
cli_thread.start()

# Start the Tkinter event loop
root.mainloop()

# Wait for the CLI thread to finish
cli_thread.join()