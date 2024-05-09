#START:PROMPT


def unique(l: list):
    """Return sorted unique elements in a list
    >>> unique([5, 3, 5, 2, 3, 3, 9, 0, 123])
    [0, 2, 3, 5, 9, 123]
    """

#END:PROMPT
#START:SOLUTION
    return sorted(list(set(l)))

#END:SOLUTION
#START:TEST


METADATA = {}


def check(candidate):
    assert candidate([5, 3, 5, 2, 3, 3, 9, 0, 123]) == [0, 2, 3, 5, 9, 123]


#END:TEST
#START:CHECK
check(unique)
#END:CHECK