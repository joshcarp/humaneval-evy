#START:PROMPT


def strlen(string: str) -> int:
    """ Return length of given string
    >>> strlen('')
    0
    >>> strlen('abc')
    3
    """

#END:PROMPT
#START:SOLUTION
    return len(string)

#END:SOLUTION
#START:TEST


METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == 0
    assert candidate('x') == 1
    assert candidate('asdasnakj') == 9

#END:TEST
#START:CHECK
check(strlen)
#END:CHECK