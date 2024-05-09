#START:PROMPT


def greatest_common_divisor(a: int, b: int) -> int:
    """ Return a greatest common divisor of two integers a and b
    >>> greatest_common_divisor(3, 5)
    1
    >>> greatest_common_divisor(25, 15)
    5
    """

#END:PROMPT
#START:SOLUTION
    while b:
        a, b = b, a % b
    return a

#END:SOLUTION
#START:TEST


METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate(3, 7) == 1
    assert candidate(10, 15) == 5
    assert candidate(49, 14) == 7
    assert candidate(144, 60) == 12

#END:TEST
#START:CHECK
check(greatest_common_divisor)
#END:CHECK