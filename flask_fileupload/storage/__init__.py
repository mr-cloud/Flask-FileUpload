from werkzeug.utils import secure_filename
from .utils import convert_to_snake_case


class StorageNotAllowed(Exception):
    def __init__(self):
        super(StorageNotAllowed, self).__init__("This file extension is not allowed.")


class StorageExists(Exception):
    def __init__(self):
        super(StorageExists, self).__init__("File already exists, choose an other name")


class StorageNotExists(Exception):
    def __init__(self):
        super(StorageNotExists, self).__init__("File does not exist")


class AbstractStorage(object):
    def __init__(self, app):
        self.app = app
        self.allowed = list(map(str.lower, app.config.get("FILEUPLOAD_ALLOWED_EXTENSIONS", list())))
        self.all_allowed = app.config.get("FILEUPLOAD_ALLOW_ALL_EXTENSIONS", False)
        self.snake_case = app.config.get("FILEUPLOAD_CONVERT_TO_SNAKE_CASE", False)

        self.app.jinja_env.globals.update(fu_get_existing_files=self.get_abs_existing_files)
        self.app.jinja_env.filters["fu_filename"] = AbstractStorage.filename

    def get_abs_existing_files(self):
        return [self.get_base_path() + f for f in self.get_existing_files()]

    @staticmethod
    def filename(full_file_path):
        return full_file_path[full_file_path.rfind("/")+1:]

    def get_existing_files(self):
        """
        :return:  list of files
        """
        raise NotImplementedError()

    def get_base_path(self):
        """
        :return: base path where the image can be found
        """
        raise NotImplementedError()

    def _store(self, filename, file_data):
        raise NotImplementedError()

    def _delete(self, filename):
        raise NotImplementedError()

    @staticmethod
    def _lower_file_extension(filename):
        last_dot = filename.rfind(".")
        if last_dot == -1:
            raise StorageNotAllowed()
        extension = filename[last_dot:].lower()
        if len(extension) == 1:  # Just a dot
            raise StorageNotAllowed()
        return filename[:last_dot] + extension

    def store(self, filename, file_data):
        filename = secure_filename(filename)
        filename = AbstractStorage._lower_file_extension(filename)
        if self.snake_case:
            filename = convert_to_snake_case(filename)

        if self.all_allowed or any(filename.endswith('.' + x) for x in self.allowed):
            self._store(filename, file_data)
        else:
            raise StorageNotAllowed()

    def delete(self, filename):
        filename = AbstractStorage._lower_file_extension(filename)
        self._delete(filename)
