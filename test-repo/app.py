def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)


def get_second_largest(numbers):
    numbers = sorted(numbers)
    return numbers[-2]


def reverse_string(text):
    return text[::-1]
