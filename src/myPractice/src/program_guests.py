from dateutil.parser import parse
from infrastructure.switchlang import switch
import program_hosts as hosts
import infrastructure.state as state
import src.services.data_service as svc


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')

    if not state.active_account:
        hosts.error_msg('You must log in first to add a snake')
        return

    name = input("What is your snake's name? ")
    if not name:
        hosts.error_msg('cancelled')
        return

    length = float(input('How long is your snake (in meters)? '))
    species = input('Species? ')
    is_venomous = input('Is your snake venomous [y]es, [n]o? ').lower().startswith('y')

    snake = svc.add_snake(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    hosts.success_msg('Created {} with id {}'.format(snake.name, snake.id))


def view_your_snakes():
    print(' ****************** Your snakes **************** ')

    if not state.active_account:
        hosts.error_msg('You must log in first to add a snake')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    print('You have {} snakes.'.format(len(snakes)))
    for s in snakes:
        print(" * {} is a {} that is {}m long and is {}venomous".format(
            s.name,
            s.species,
            s.length,
            '' if s.is_venomous else 'not '
        ))


def book_a_cage():
    print(' ****************** Book a cage **************** ')

    if not state.active_account:
        hosts.error_msg('You must log in first to add a snake')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    if not snakes:
        hosts.error_msg('You must first [a]dd a snake before you can book a cage.')
        return

    print("Let's start by finding available cages.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")

    if not start_text:
        hosts.error_msg('cancelled')
        return

    checkin = parse(start_text)

    checkout = parse(input('Check-out date [yyy-mm-dd]: '))

    if checkin >= checkout:
        hosts.error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(snakes):
        print('{}, {} (length: {}, venomous: {})'.format(
            idx + 1,
            s.name,
            s.length,
            'yes' if s.is_venomous else 'no'
        ))

    snake = snakes[int(input('Which snake do you want to book (number)')) - 1]

    cages = svc.get_available_cages(checkin, checkout, snake)

    print("There are {} cages available in that time.".format(len(cages)))
    for idx, c in enumerate(cages):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            c.name,
            c.square_meters,
            'yes' if c.is_carpeted else 'no',
            'yes' if c.has_toys else 'no'
        ))

    if not cages:
        hosts.error_msg('Sorry, no cages are available for that date.')
        return

    cage = cages[int(input('Which cage do you want to book (number) ')) - 1]
    svc.book_cage(state.active_account, snake, cage, checkin, checkout)

    hosts.success_msg('Successfully booked {} for {} at ${}/night.'.format(cage.name, snake.name, cage.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    # TODO: Require an account
    # TODO: List booking info along with snake info

    print(" -------- NOT IMPLEMENTED -------- ")
