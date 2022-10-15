#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : fileUtils.py
# @Description : 常用的文件、目录处理工具
# @Author      : sam
# @Time        : 2022年 10月 13日 08:55
# @Version     : 1.0
# -*- coding: utf-8 -*-
import os


def file_ext(filename, level=1):
    """
    return extension of filename

    Parameters:
    -----------
    filename: str
        name of file, path can be included
    level: int
        level of extension.
        for example, if filename is 'sky.png.bak', the 1st level extension
        is 'bak', and the 2nd level extension is 'png'

    Returns:
    --------
    extension of filename
    """
    return filename.split('.')[-level]


def _contain_file(path, extensions):
    """
    check whether path contains any file whose extension is in extensions list

    Parameters:
    -----------
    path: str
        path to be checked
    extensions: str or list/tuple of str
        extension or extensions list

    Returns:
    --------
    return True if contains, else return False
    """
    assert os.path.exists(path), 'path must exist'
    assert os.path.isdir(path), 'path must be dir'

    if isinstance(extensions, str):
        extensions = [extensions]

    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if (extensions is None) or (file_ext(file) in extensions):
                return True
    return False


def _process_extensions(extensions=None):
    """
    preprocess and check extensions, if extensions is str, convert it to list.

    Parameters:
    -----------
    extensions: str or list/tuple of str
        file extensions

    Returns:
    --------
    extensions: list/tuple of str
        file extensions
    """
    if extensions is not None:
        if isinstance(extensions, str):
            extensions = [extensions]
        assert isinstance(extensions, (list, tuple)), \
            'extensions must be str or list/tuple of str'
        for ext in extensions:
            assert isinstance(ext, str), 'extension must be str'
    return extensions


def get_files(path, extensions=None, is_recursive=True):
    """
    read files in path. if extensions is None, read all files, if extensions
    are specified, only read the files who have one of the extensions. if
    is_recursive is True, recursively read all files, if is_recursive is False,
    only read files in current path.

    Parameters:
    -----------
    path: str
        path to be read
    extensions: str or list/tuple of str
        file extensions
    is_recursive: bool
        whether read files recursively. read recursively is True, while just
        read files in current path if False

    Returns:
    --------
    files: the obtained files in path
    """
    extensions = _process_extensions(extensions)
    files = []
    # get files in current path
    if not is_recursive:
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            if os.path.isfile(fullname):
                if (extensions is None) or (file_ext(fullname) in extensions):
                    files.append(fullname)
        return files
    # get files recursively
    for main_dir, _, sub_file_list in os.walk(path):
        for filename in sub_file_list:
            fullname = os.path.join(main_dir, filename)
            if (extensions is None) or (file_ext(fullname) in extensions):
                files.append(fullname)
    return files


def get_folders(path, extensions=None, is_recursive=True):
    """
    read folders in path. if extensions is None, read all folders, if
    extensions are specified, only read the folders who contain any files that
    have one of the extensions. if is_recursive is True, recursively read all
    folders, if is_recursive is False, only read folders in current path.

    Parameters:
    -----------
    path: str
        path to be read
    extensions: str or list/tuple of str
        file extensions
    is_recursive: bool
        whether read folders recursively. read recursively is True, while just
        read folders in current path if False

    Returns:
    --------
    folders: the obtained folders in path
    """
    extensions = _process_extensions(extensions)
    folders = []
    # get folders in current path
    if not is_recursive:
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                if (extensions is None) or \
                        (_contain_file(fullname, extensions)):
                    folders.append(fullname)
        return folders
    # get folders recursively
    for main_dir, _, _ in os.walk(path):
        if (extensions is None) or (_contain_file(main_dir, extensions)):
            folders.append(main_dir)
    return folders


def traversal_files(path: str) -> dict:
    """
    遍历指定路径下的所有目录和文件
    :param path:
    :return: 返回字典集合 {"dirs": dirs, "files": files}
    """
    dirs, files = [], []
    for item in os.scandir(path):
        if item.is_dir():
            dirs.append(item)
        else:
            files.append(item)
    return {"dirs": dirs, "files": files}


if __name__ == '__main__':
    _path = r'.\data'

    _files = get_files(_path)
    print(_files)  # ==> ['D:\\data\\1.bmp', 'D:\\data\\2.bmp', 'D:\\data\\a\\a1.bmp', 'D:\\data\\b\\b1.bmp']

    folders = get_folders(_path)
    print(folders)  # ==> ['D:\\data', 'D:\\data\\a', 'D:\\data\\b']
