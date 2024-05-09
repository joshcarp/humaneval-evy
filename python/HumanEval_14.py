#START:PROMPT
from typing import List


def all_prefixes(string: str) -> List[str]:
    """ Return list of all prefixes from shortest to longest of the input string
    >>> all_prefixes('abc')
    ['a', 'ab', 'abc']
    """

#END:PROMPT
#START:SOLUTION
    result = []

    for i in range(len(string)):
        result.append(string[:i+1])
    return result

#END:SOLUTION
#START:TEST


METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('') == []
    assert candidate('asdfgh') == ['a', 'as', 'asd', 'asdf', 'asdfg', 'asdfgh']
    assert candidate('WWW') == ['W', 'WW', 'WWW']

#END:TEST
#START:CHECK
check(all_prefixes)
#END:CHECK