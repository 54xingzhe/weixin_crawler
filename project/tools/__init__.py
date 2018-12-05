def restart():
    import os,sys
    print(sys.executable)
    print(*([sys.executable]+sys.argv))
    os.execl(sys.executable, "python.exe", *sys.argv)

