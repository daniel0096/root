import os
import utils
from typing import TypeAlias, Optional, Union

eDir: TypeAlias = utils.eDirType

@utils.singleton
class FileManager:
    """
    Singleton class that handles file operations such as reading, writing and creating files
    within predefined working directories (log/config).
    
    Class Attributes:
        working_dir (str): Path to the current working directory.
    
    Instance Attributes:
        _file_name (str): Last file name used by the instance.
    """

    working_dir: str = None

    def __init__(self):
        """
        Initializes the FileManager instance.
        """
        self._file_name: str = None

    @utils.require_conditions(check_class_attr="working_dir", check_args_not_null=True)
    def create_file(self, file_name: str) -> bool:
        """
        Creates an empty file with the given name in the current working directory.

        Args:
            file_name (str): Name of the file to create.

        Returns:
            bool: True if the file was created successfully, False otherwise.
        """

        full_path = os.path.join(self.working_dir, file_name)
        
        print(full_path)

        try:
            with open(full_path, "w") as fp:
                fp.write("")
            self._file_name = full_path

            return True

        except Exception as err:
            print(f"There was an issue while creating the file: {err}")
            return False

    @utils.require_conditions(check_class_attr="working_dir", check_args_not_null=True)
    def read_file(self, file_name: str) -> Optional[list]:
        """
        Reads the contents of a file line by line.

        Args:
            file_name (str): Name of the file to read.

        Returns:
            Optional[list]: List of lines from the file, or None if reading failed.
        """

        full_path = os.path.join(self.working_dir, file_name)

        content = []

        try:
            with open(full_path, "r") as fp:
                content = fp.readlines()
                return content

        except Exception as err:
            print(f"There was an issue while reading the file: {err}")
            return None

    @utils.require_conditions(check_class_attr="working_dir", check_args_not_null=True)
    def write_file(self, file_name: str, content: Union[str, list[str]]) -> bool:
        """
        Appends content to a file in the current working directory.

        Args:
            file_name (str): Name of the file to write to.
            content (Union[str, list[str]]): Content to write. Can be a single string or a list of lines.

        Returns:
            bool: True if the content was written successfully, False otherwise.
        """

        full_path = os.path.join(self.working_dir, file_name)
        try:
            with open(full_path, "a", encoding="utf-8") as f:
                if isinstance(content, list):
                    f.writelines(
                        line if line.endswith("\n") else line + "\n"
                        for line in content
                    )
                else:
                    f.write(content + "\n")
            self._file_name = full_path
            return True
        except Exception as err:
            print(f"There was an issue while writing to the file: {err}")
            return False

    @classmethod
    def set_working_path(cls, dir_type: eDir):
        """
        Sets the working directory based on the directory type.

        Args:
            dir_type (eDirType): Enum specifying the desired working directory (log or config).

        Raises:
            utils.CheckException: If the directory type is unknown.
        """

        cur_path: str = os.path.abspath(__file__)

        root_path: str = os.path.dirname(os.path.dirname(cur_path))
        folder_name = utils.working_directories.get(dir_type)

        if folder_name is None:
            raise utils.CheckException(f"Unknown directory type: {dir_type}")

        cls.working_dir = os.path.join(root_path, folder_name)

        if not os.path.exists(cls.working_dir):
            os.makedirs(cls.working_dir)

    def build_init_files(self) -> bool:
        self.set_working_path(eDir.DIR_TYPE_LOG)
        self.create_file("sysser.txt")
        self.create_file("syslog.txt")
        self.set_working_path(eDir.DIR_TYPE_CONFIG)
        self.create_file("config.cfg")

if __name__ == "__main__":
    """
    Debugging and manual testing block.
    """

    file_manager = FileManager()
    file_manager.set_working_path(eDir.DIR_TYPE_LOG)
    file_manager.create_file("sysser.txt")
    file_manager.create_file("syslog.txt")
    file_manager.set_working_path(eDir.DIR_TYPE_CONFIG)
    file_manager.create_file("config.cfg")