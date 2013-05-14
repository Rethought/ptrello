#!/usr/bin/env python
"""
Test getting trello cards by API and printing

Dirty piece of hackery.
"""
import json
from optparse import OptionParser
from jinja2 import Environment, PackageLoader
import trello
import settings


jinja_env = Environment(loader=PackageLoader('trello', 'templates'))
# map the value of --type to a template
# keys used to determine valid choices for --type
TEMPLATES = {'text': 'board_summary.txt',
             'html': 'board_summary.html',
             }


def get_lists(tconn, board_id):
    return tconn.boards(board_id).lists.request()


def cards_for_list(tconn, list_id):
    return tconn.lists(list_id).cards().request()


def get_checklist(tconn, c_id):
    return tconn.checklists(c_id).request()


def set_checked(checklist):
    """
    Add a `checked` property to the items in checklist dict.
    Set `True` if checklist item `state` is 'Complete'
    """
    for item in checklist['checkItems']:
        item['checked'] = True if item['state'] == u'complete' else False
    return checklist


def augment_card(tconn, card):
    """
    De-normalise some properties, e.g. check lists, into this card record
    """
    card['checklists'] = [set_checked(get_checklist(tconn, cid))
                          for cid in card['idChecklists']]
    return card


def strip(s):
    """
    Custom filter, calls strip on the string and returns
    Unlike `trim` builtin filter this removes \\n and \\r
    """
    return s.strip()


def subst(s, target, replace):
    """
    Custom filter to replace all occurences of `target` with `replace`.
    """
    return s.replace(target, replace)


def parformat(s, line_len=80, split_str='\n'):
    """
    Jinja filter that inserts `split_str` every `line_len` characters
    or fewer to fit on a word boundary.
    """
    tokens = s.split()
    new_tokens = []
    count = 0
    while tokens:
        token = tokens.pop(0)
        l = len(token)
        if count+l > line_len:
            new_tokens.append(split_str)
            count = 0
        new_tokens.append(token)
        count += l+1  # +1 for the space needed

    return " ".join(new_tokens)


def render(data, suffix='text', title='Stories'):
    """
    Render the dataset with template suggested by suffix
    """
    filters = dict(strip=strip, parformat=parformat, subst=subst)
    jinja_env.filters.update(filters)
    filename = TEMPLATES[suffix]
    template = jinja_env.get_template(filename)
    print(template.render(lists=data, title=title))


def print_board(tconn, board, suffix='text', card_filter="", dump=False,
                title='Stories', prune=False):
    inlists = get_lists(tconn, board)
    outlists = []
    while inlists:
        lst = inlists.pop(0)
        lst['cards'] = [augment_card(tconn, card)
                        for card in cards_for_list(tconn, lst['id'])
                        if card['name'].find(card_filter) >= 0]
        if prune and not lst['cards']:
            pass
        else:
            outlists.append(lst)

    if dump:
        print json.dumps(outlists)
    else:
        render(outlists, suffix, title)


def load(tconn, input_file, suffix='text', title='Stories'):
    """
    Load JSON dataset from `input_file` and render with the
    appropriate template.
    """
    with open(input_file, 'rt') as inf:
        data = json.loads(inf.read())
        render(data, suffix, title)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', '--board',
                      default=settings.DEFAULT_BOARD,
                      help="The board ID to use [default: %default]")
    parser.add_option('-f', '--filter',
                      default="",
                      help="Display only cards with description containing "
                           "this value")
    parser.add_option('-t', '--type',
                      default='html',
                      choices=TEMPLATES.keys(),
                      help="Output format text or html (default: %default)")
    parser.add_option('', '--title',
                      default='Trello story board',
                      help="Set the document title (default: %default)")
    parser.add_option('', '--load',
                      default=None,
                      help="Load a previously dumped data set for rendering")
    parser.add_option('', '--dump',
                      action="store_true",
                      default=False,
                      help="Dump acquired data as JSON rather than rendering")
    parser.add_option('', '--prune',
                      action="store_true",
                      default=False,
                      help="Prune out lists with no stories - has no impact "
                           "with --load (default: %default)")
    parser.add_option('', '--key',
                      default=settings.KEY,
                      help="API key to use (overrides that in settings)")
    parser.add_option('', '--secret',
                      default=settings.SECRET,
                      help="Secret key to use (overrides that in settings)")
    parser.add_option('', '--token',
                      default=settings.TOKEN,
                      help="API token to use (overrides that in settings)")

    (options, args) = parser.parse_args()
    tconn = trello.Trello(options.key, options.token)
    if options.load:
        load(tconn, options.load, options.type, title=options.title)
    else:
        print_board(tconn, options.board, options.type, options.filter,
                    title=options.title,
                    dump=options.dump,
                    prune=options.prune)
