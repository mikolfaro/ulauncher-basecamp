from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from basecampy3 import Basecamp3
import logging

logger = logging.getLogger(__name__)


class BasecampExtension(Extension):

    def __init__(self):
        super(BasecampExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, ExtensionKeywordListener())
        self.bc3 = Basecamp3()
        self.projects_list = None

    def get_projects_list(self):
        if self.projects_list:
            return self.projects_list
        else:
            self.projects_list = list(self.bc3.projects.list())
            return self.projects_list


class ExtensionKeywordListener(EventListener):
    def on_event(self, event, extension):
        items = []
        query = event.get_argument() or ""

        for project in extension.get_projects_list():
            if query.lower() in project.name.lower():
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=project.name,
                                                 description='Open project in browser',
                                                 on_enter=OpenUrlAction(project.app_url)))

        return RenderResultListAction(items)


if __name__ == '__main__':
    BasecampExtension().run()
