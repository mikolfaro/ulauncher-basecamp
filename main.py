from basecampy3.exc import UnauthorizedError, Basecamp3Error
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
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
        self.subscribe(ItemEnterEvent, BasecampItemEnterEventListener())
        try:
            self.bc3 = Basecamp3()
        except Basecamp3Error as exc:
            logger.error(exc)
            self.bc3 = None
        self.projects_list = None

    def build_open_action(self, url):
        if self.preferences['basecamp_browser']:
            return RunScriptAction("%s %s &" % (self.preferences['basecamp_browser'], url))
        else:
            return OpenUrlAction(url)

    @expiring_cache()
    def get_projects_list(self):
        self.projects_list = list(self.bc3.projects.list())
        return self.projects_list

    def get_project_todos(self, project):
        project_todos = []
        todolists = list(self.bc3.todolists.list(project))
        for todolist in todolists:
            logger.debug("TODO LIST: %s" % todolist.title)
            todos = list(self.bc3.todos.list(todolist, project))
            for todo in todos:
                if todo is not None:
                    logger.debug("TODO: %s" % todo.title)
                    project_todos.append(todo)
        return project_todos

    def markAsDone(self, project_id, todo_id):
        logger.info("Completed todo #%s of project %s" % (project_id, todo_id))
        self.bc3.todos.complete(todo_id, project_id)


class ExtensionKeywordListener(EventListener):
    def on_event(self, event, extension):
        items = []
        projects = []
        query = event.get_argument() or ""

        if (not extension.bc3) or query == "configure":
            items.append(ExtensionResultItem(icon='image/icon.png',
                                             name='Configure Basecampy3',
                                             description='Spawn a terminal to configure Basecampy3',
                                             on_enter=RunScriptAction("bc3 configure")))

        if extension.bc3:
            clean_query = query.strip().lower()
            for project in extension.get_projects_list():
                if clean_query in project.name.lower():
                    projects.append(project)
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                     name=project.name,
                                                     description='Open project in browser',
                                                     on_enter=extension.build_open_action(project.app_url)))
            if projects and len(projects) == 1 and projects[0] is not None:
                logger.info("Loading TODOs for prject %s" % projects[0].name)
                for todo in extension.get_project_todos(projects[0]):
                    if todo.status == "active" and not todo.completed:
                        items.append(ExtensionResultItem(icon='images/todo.png',
                                                         name=todo.title,
                                                         description='Mark as done',
                                                         on_enter=ExtensionCustomAction({'type': 'MarkTodoAsDone', 'projectId': projects[0].id, 'todoId': todo.id})))
        logger.info("Completed query")
        return RenderResultListAction(items)


class BasecampItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        logger.info("Should mark as Done")
        data = event.get_data()
        extension.markAsDone(data['projectId'], data['todoId'])
        return DoNothingAction()


if __name__ == '__main__':
    BasecampExtension().run()
