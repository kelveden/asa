from .asana import Asana
from colorama import Fore, Style

from term_image import image

LINE_SEPARATOR = "--------------------------------------"

def _new_asana_client(args):
    return Asana(args.token, args.verbose)


def who(args):
    """
    Prints basic details of the user currently being used for authentication to Asana.

    :param args:
        open: Whether to bypass CLI output and just open the user details page in the browser.
    """
    asana = _new_asana_client(args)
    data = asana.get_user(user_id="me")

    print(LINE_SEPARATOR)
    print(f"{Fore.CYAN}Name:{Fore.RESET} {data['name']}")
    print(f"{Fore.CYAN}Id:{Fore.RESET}   {data['gid']}")
    print(LINE_SEPARATOR)

    image_data = image.from_url(data['photo']['image_128x128'], width=30)
    print(image_data)



