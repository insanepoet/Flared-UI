import pkgutil
import importlib
from flask import Blueprint
from FlaredUI.Logging import get_logger



class ModulesUtility:
    """A class for utility functions related to module management and logging."""
    def __init__(self, module_name):
        # Import ModuleLogger here (deferred import)
        from FlaredUI.Modules.Errors.GeneralErrors import ModuleLogger
        self.logger = ModuleLogger(module_name)

    def import_submodules(self, package):
        """Programmatically imports all submodules of a package."""
        for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if not is_pkg:
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    # Import ModuleImportError here (deferred import)
                    from FlaredUI.Modules.Errors.GeneralErrors import ModuleImportError
                    raise ModuleImportError(module_name, str(e))  # Raise ModuleImportError

    def export_globals(self):  # Remove the module_name argument
        """Dynamically creates __all__ to include all objects (except those starting with "_") from the module's
        namespace."""
        caller_globals = dict(importlib.import_module(self.logger.logger.name).__dict__)
        # Remove private attributes (starting with "_") and the logger itself
        public_globals = [name for name in caller_globals if not name.startswith('_') and name != 'logger']
        globals()['__all__'] = public_globals


class BlueprintUtility:
    """A class for utility functions related to blueprint registration."""

    def __init__(self, app):
        self.app = app

    def register_blueprints(self, package):
        """Dynamically registers all blueprints found within a package."""
        for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if not is_pkg:
                try:
                    module = importlib.import_module(module_name)
                    for attr in dir(module):
                        if attr.endswith('_bp'):
                            blueprint = getattr(module, attr)
                            if isinstance(blueprint, Blueprint):
                                self.app.register_blueprint(blueprint)
                except ImportError as e:
                    from FlaredUI.Modules.Errors.GeneralErrors import ModuleImportError
                    raise ModuleImportError(module_name, str(e))

    def export_globals(self):  # Remove the module_name argument
        """Dynamically creates __all__ to include all objects (except those starting with "_") from the module's
        namespace."""
        caller_globals = dict(importlib.import_module(self.logger.logger.name).__dict__)
        public_globals = [name for name in caller_globals if not name.startswith('_') and name != 'logger']
        globals()['__all__'] = public_globals
