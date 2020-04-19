from util import seq


def a(l):
    l.append(1)


if __name__ == '__main__':
    for alpha in seq(0, 20, 0.25):
        print('alpha: ' + str(alpha))
        for smaller_alpha in seq(alpha - 0.25, alpha, 0.1):
            print('smaller_alpha: ' + str(smaller_alpha))


