from basecampy3.exc import UnauthorizedError, Basecamp3Error
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from basecampy3 import Basecamp3
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)


def expiring_cache(seconds=300):
    def actual_decorator(function):
        start_time = time.time()
        memo = {}

        @wraps(function)
        def wrapper(*args):
            nonlocal start_time

            logger.debug("Expires at %s" % str(start_time + seconds))
            logger.debug("Now %s" % str(time.time()))
            if time.time() > (start_time + seconds):
                logger.info("Cache expire")
                memo.pop(args, None)

            try:
                logger.info("Cache check")
                return memo[args]
            except KeyError:
                start_time = time.time()
                logger.info("Cache miss")
                rv = function(*args)
                memo[args] = rv
                return rv
        return wrapper
    return actual_decorator


class BasecampExtension(Extension):

    def __init__(self):
        super(BasecampExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, ExtensionKeywordListener())
        try:
            self.bc3 = Basecamp3()
        except Basecamp3Error as exc:
            logger.error(exc)
            self.bc3 = None
        self.projects_list = None

    @expiring_cache()
    def get_projects_list(self):
        self.projects_list = list(self.bc3.projects.list())
        return self.projects_list


class ExtensionKeywordListener(EventListener):
    def on_event(self, event, extension):
        items = []
        query = event.get_argument() or ""

        if (not extension.bc3) or query == "configure":
            items.append(ExtensionResultItem(icon='image/icon.png',
                                             name='Configure Basecampy3',
                                             description='Spawn a terminal to configure Basecampy3',
                                             on_enter=RunScriptAction("bc3 configure")))

        if extension.bc3:
            for project in extension.get_projects_list():
                if query.lower() in project.name.lower():
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                     name=project.name,
                                                     description='Open project in browser',
                                                     on_enter=OpenUrlAction(project.app_url)))

        logger.info("Completed query")
        return RenderResultListAction(items)


if __name__ == '__main__':
    BasecampExtension().run()
