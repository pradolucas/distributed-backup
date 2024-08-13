from Manager import Manager


def main():
    m = Manager("localhost", 50000)
    m.start()


if __name__ == '__main__':
    main()