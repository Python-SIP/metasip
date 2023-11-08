# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from ....model import implements, Instance, Model, observe, Str
from ....ui import Application, Dialog, IView
from ....ui.actions import QuitAction

from ... import IQuitVeto, ITool, IShell


@implements(ITool)
class QuitTool(Model):
    """ The QuitTool is the default implementation of a :term:`tool`
    that handles the user's ability to quit the application.
    """

    # The tool's identifier.
    id = 'dip.shell.tools.quit'

    # The action.
    quit_action = QuitAction()

    # The text used as the preamble to the multiple list of reasons.
    user_quit_preamble = Str(
            "You may not want to quit because of the following reasons.")

    # The text used as the question asking if the user really wants to quit.
    user_quit_question = Str("Do you still want to quit?")

    # The text used as the title of any user dialogs.
    user_quit_title = Str()

    # The factory used to create the dialog when presenting multiple reasons to
    # the user.  The corresponding model will contain a 'preamble' string, a
    # 'reason' and a 'question' string.  The view must create an implementation
    # of :class:`~dip.ui.IOptionList` bound to the 'reason'.
    user_quit_view = Instance(Dialog)

    def query_single_reason(self, reason):
        """ Ask the user about a single reason to not quit.

        :param reason:
            is the reason not to quit.
        :return:
            ``True`` if the user wants to quit.
        """

        answer = Application.question(self.user_quit_title,
                reason + "\n\n" + self.user_quit_question, parent=self.shell)

        return (answer == 'yes')

    def query_multiple_reasons(self, reasons):
        """ Ask the user about a number of reasons not quit.

        :param reasons:
            is the list of reasons not to quit.
        :return:
            ``True`` if the user wants to quit.
        """

        model = dict(preamble=self.user_quit_preamble, reason=None,
                question=self.user_quit_question)

        dialog = self.user_quit_view(model=model, parent=self.shell)

        # Set the reasons.
        dialog.controller.reason_editor.options = reasons

        return dialog.execute()

    @user_quit_title.default
    def user_quit_title(self):
        """ Invoked to return the default user quit title. """

        return self.quit_action.plain_text

    @user_quit_view.default
    def user_quit_view(self):
        """ Invoked to return the default user quit view factory. """

        from ....ui import Label, OptionList, VBox

        return Dialog(
                VBox(
                    Label('preamble'),
                    OptionList('reason', read_only=True),
                    Label('question')),
                buttons=['yes', 'no'], title=self.user_quit_title)

    @observe('shell')
    def __shell_changed(self, change):
        """ Invoked when the shell changes. """

        if change.old is not None:
            IView(change.old).close_request_handlers.remove(
                    self._handle_close_request)

        if change.new is not None:
            IView(change.new).close_request_handlers.append(
                    self._handle_close_request)

    @quit_action.triggered
    def quit_action(self):
        """ Invoked when the Quit action is triggered. """

        # FIXME: We need to query all shells, ie. this tool needs to be able to
        # FIXME: be shared.

        if self._handle_close_request(self.shell):
            Application().quit()

    def _handle_close_request(self, shell):
        """ Determine if the shell should be closed. """

        # Collect the reasons why the close should be disallowed.
        reasons = []

        for tool in IShell(shell).tools:
            quit_veto = IQuitVeto(tool, exception=False)
            if quit_veto is not None:
                reasons.extend(quit_veto.reasons)

        nr_reasons = len(reasons)

        if nr_reasons == 0:
            allow_close = True
        elif nr_reasons == 1:
            allow_close = self.query_single_reason(reasons[0])
        else:
            allow_close = self.query_multiple_reasons(reasons)

        return allow_close
