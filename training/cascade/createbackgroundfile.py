import os


def start():
    folder = input("Please input directory for plain images")
    output_name = input("Please input name of output file")
    output_location = input("Please input destination of output")
    if os.path.exists(os.path.join(output_location, output_name)):
        select = False
        while not select:
            x = input("This file already exists, are you sure you want to overwrite it? Y/N")
            if x == 'n' or x == 'N':
                return()
            elif x == 'y' or x == 'Y':
                select = True
            else:
                print("Invalid selection")
    print("Placing generated file in " + os.path.join(output_location, output_name))
    output = ""
    for file in os.listdir(folder):
        output = output + os.path.join(folder, file) + "\n"
    out = open(os.path.join(output_location, output_name), "w")
    out.write(output)
    out.close()
    print("Complete")

