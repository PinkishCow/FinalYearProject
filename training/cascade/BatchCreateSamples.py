import subprocess

a = [[10, 10], [20, 20], [30, 30], [40, 40], [50, 50], [60, 60], [70, 70], [80, 80], [40, 30], [80, 60]]

info = [("Butter", 1024), ("Can", 974), ("Cereal", 855), ("Crisps-1", 1091),
        ("Crisps-2", 978), ("Milk", 983), ("Spray", 986)]

for x in a:
    for n in info:
        do = ['D:\\Documents\\opencv-3.4.9\\build\\bin\\Release\\opencv_createsamples.exe '
              '-info "D:\\Desktop\\Dissertation\\images\\{}-Fixed.txt" '
              '-num {} '
              '-w {} '
              '-h {} '
              '-vec "D:\\Desktop\\Dissertation\\images\\vec files\\{}{}{}.vec"'.format
              (n[0], n[1], x[0], x[1], n[0], x[0], x[1])]
        proc = subprocess.run(do[0])
        print(proc.args)
