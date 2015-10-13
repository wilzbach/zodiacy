import re

def parse_horoscope(file):
    pattern = '<div class="daily overview">\s+<h3 class="title">Daily Overview</h3>\s+<div class="desc">(.*) <a'
    regex = re.compile(pattern)
    text = ''.join(file.readlines())
    result = regex.search(text)
    return result.group(1) if result is not None else None
