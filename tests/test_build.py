"""Tests for build.py"""
from collections import namedtuple
from os import getcwd, path

from scipio import build

from mock import patch
# from nose import with_setup

# defined in download.py
Project = namedtuple('Project', 'folder, workspace_files, project_files')
Mockargs = namedtuple('Mockargs', 'plistv, plistb, project, workspace')

# def test_parse_xcodebuild_list():
#    """Decompose xcode -list output to lists"""
    # parse_xcodebuild_list(output_string)


# def test_run_build():
#    """Run the build command through xcodebuild"""
    # run_build(command, verbose, project)


# def test_setup_build():
#    """Go to the folder/project or folder/workspace and check if any of the configuration, sdk,
#    scheme, or target args supplied exist in it, set up the build with as many of them as do"""
    # setup_build(project, possible_args, workspace=False)


@patch('scipio.build.setup_build')
@patch('scipio.build.edit_plist')
@patch('scipio.build.walk')
@patch('scipio.build.chdir')
class Test_build_project_or_workspace:
    """test build_project_or_workspace()"""
    test_workspace = Project(folder='folder name',
                             workspace_files=['/first.xcworkspace', '/second.xcworkspace'],
                             project_files=['/first.xcodeproj', '/second.xcodeproj'])
    test_project = Project(folder='folder name',
                           workspace_files=None,
                           project_files=['/first.xcodeproj', '/second.xcodeproj'])
    project_file = path.join(getcwd(), 'folder name')

    def test_plistv(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist, mock_setup_build_fn):
        """test plistv"""
        args = Mockargs(plistv='0.4.2',
                        plistb=None,
                        project='second',
                        workspace='second') # will get the second workspace
        mock_walk_fn.return_value = [('subfolder', [], ['something.plist', 'something.else'])]
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_walk_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_called_once_with('0.4.2', None,
                                                path.join(getcwd(),
                                                          'subfolder/something.plist'))
        mock_setup_build_fn.assert_called_once_with('/second.xcworkspace',
                                                    Mockargs(plistv='0.4.2',
                                                             plistb=None,
                                                             project='second',
                                                             workspace='second'),
                                                    workspace=True)


    def test_plistb(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist, mock_setup_build_fn):
        """test plistb"""
        args = Mockargs(plistv=None,
                        plistb='1.0.0',
                        project='second',
                        workspace='second') # will get the second workspace
        mock_walk_fn.return_value = [('subfolder', [], ['something.plist', 'something.else'])]
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_walk_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_called_once_with(None, '1.0.0',
                                                path.join(getcwd(),
                                                          'subfolder/something.plist'))
        mock_setup_build_fn.assert_called_once_with('/second.xcworkspace',
                                                    Mockargs(plistv=None,
                                                             plistb='1.0.0',
                                                             project='second',
                                                             workspace='second'),
                                                    workspace=True)


    def test_plist_v_and_b(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist, mock_setup_build_fn):
        """test plistv and b"""
        args = Mockargs(plistv='0.0.1',
                        plistb='0.0.2',
                        project='second',
                        workspace='second') # will get the second workspace
        mock_walk_fn.return_value = [('subfolder', [], ['something.plist', 'something.else'])]
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_walk_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_called_once_with('0.0.1', '0.0.2',
                                                path.join(getcwd(),
                                                          'subfolder/something.plist'))
        mock_setup_build_fn.assert_called_once_with('/second.xcworkspace',
                                                    Mockargs(plistv='0.0.1',
                                                             plistb='0.0.2',
                                                             project='second',
                                                             workspace='second'),
                                                    workspace=True)


    def test_valid_workspace(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist,
                             mock_setup_build_fn):
        """valid workspace"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project='second',
                        workspace='second') # will get the second workspace
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/second.xcworkspace',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project='second',
                                                             workspace='second'),
                                                    workspace=True)


    def test_invalid_workspace_but_proj(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist,
                                        mock_setup_build_fn):
        """invalid workspace but valid project"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project='second',
                        workspace='unknown') # will get the second project
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/second.xcodeproj',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project='second',
                                                             workspace='unknown'))


    def test_invalid_workspace_and_proj(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist,
                                        mock_setup_build_fn):
        """invalid workspace and invalid project"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project='unknown',
                        workspace='unknown') # will get the first workspace
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_workspace, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/first.xcworkspace',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project='unknown',
                                                             workspace='unknown'),
                                                    workspace=True)

######
    def test_valid_project(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist,
                           mock_setup_build_fn):
        """no workspace, a valid project in the args"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project='second',
                        workspace=None) # will get the second project
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_project, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/second.xcodeproj',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project='second',
                                                             workspace=None))


    def test_no_valid_project(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist,
                              mock_setup_build_fn):
        """no workspace, a project in args which doesn't exist"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project='unknown',
                        workspace=None) # will get the first project
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_project, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/first.xcodeproj',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project='unknown',
                                                             workspace=None))


    def test_no_project(self, mock_chdir_fn, mock_walk_fn, mock_edit_plist, mock_setup_build_fn):
        """no workspace, no project"""
        args = Mockargs(plistv=None,
                        plistb=None,
                        project=None,
                        workspace=None) # will get the first project
        mock_walk_fn.return_value = []
        build.build_project_or_workspace(self.test_project, args)

        mock_chdir_fn.assert_called_once_with(self.project_file)
        mock_edit_plist.assert_not_called()
        mock_setup_build_fn.assert_called_once_with('/first.xcodeproj',
                                                    Mockargs(plistv=None,
                                                             plistb=None,
                                                             project=None,
                                                             workspace=None))
