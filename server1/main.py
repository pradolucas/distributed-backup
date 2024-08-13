from Worker import Worker


def main():
    w1 = Worker("localhost", 60000, "./server1")
    w1.start()


if __name__ == '__main__':
    main()
