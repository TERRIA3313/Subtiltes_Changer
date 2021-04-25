import os
import wx
import wx.adv


class NumberCtrl(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size):
        wx.TextCtrl.__init__(self, parent=parent, id=id, value=value, size=size, pos=pos)
        self.Bind(wx.EVT_CHAR, lambda event: self.force_numeric(event))

    def force_numeric(self, event):
        raw_value = self.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and '.' not in raw_value:
                event.Skip()


class main(wx.Frame):
    def __init__(self, parent, main_id, title):
        wx.Frame.__init__(self, parent, main_id, title, wx.DefaultPosition, size=(650, 720),
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX)

        menu_bar = wx.MenuBar()
        system_bar = wx.Menu()
        system_bar.Append(1, '&폴더 열기', '동영상과 자막이 있는 폴더를 엽니다')
        system_bar.Append(2, '&나가기', '프로그램을 종료합니다')
        menu_bar.Append(system_bar, '&시스템')
        self.SetMenuBar(menu_bar)
        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        self.directory = ""

        self.movies = wx.adv.EditableListBox(self.panel, -1, "동영상", (10, 10), (300, 500), wx.LB_SINGLE)
        self.subtitles = wx.adv.EditableListBox(self.panel, -1, "자막", (320, 10), (300, 500), wx.LB_SINGLE)

        self.name_box = wx.StaticBox(self.panel, id=14, pos=(10, 580), size=(380, 50), label="파일 이름")
        self.start_box = wx.StaticBox(self.panel, id=15, pos=(10, 520), size=(70, 50), label="시작 번호")

        self.name = wx.TextCtrl(self.name_box, id=11, pos=(15, 20), size=(350, 20))
        self.name_text = wx.StaticText(self.panel, id=12, pos=(100, 525),
                                       label="넘버링이 들어갈 부분을 지우고 *을 입력하여 주십시오."
                                             "\n*은 1개만 입력해야 합니다."
                                             "\n시작 번호부터 넘버링되어 변환/저장됩니다.")
        self.start = NumberCtrl(self.start_box, id=13, pos=(15, 20), size=(40, 20), value="")

        self.rename = wx.Button(self.panel, id=101, pos=(410, 520), size=(210, 110), label="변환")

        self.Bind(wx.EVT_MENU, self.open_dir, id=1)
        self.Bind(wx.EVT_BUTTON, self.change_name, self.rename)

    def open_dir(self, event):
        open_dlg = wx.DirDialog(self, "폴더 선택")
        if open_dlg.ShowModal() == wx.ID_OK:
            self.directory = open_dlg.GetPath()
            files = os.listdir(self.directory)
            self.search(files)

    def search(self, files):
        movie_list = []
        subtitle_list = []
        movie_extensions = [".avi", ".mkv", ".mp4", ".mpeg"]
        subtitle_extensions = [".smi", ".srt", ".ssa", ".ass"]

        for i in movie_extensions:
            for j in files:
                if i in j.casefold():
                    movie_list.append(j)

        for i in subtitle_extensions:
            for j in files:
                if i in j.casefold():
                    subtitle_list.append(j)

        self.movies.SetStrings(movie_list)
        self.subtitles.SetStrings(subtitle_list)
        self.get_name()

    def get_name(self):
        self.name.SetValue(self.movies.GetStrings()[0][:-4])

    def change_name(self, event):
        if self.directory == "":
            dlg = wx.MessageDialog(self, "시스템-폴더 열기를 먼저 진행하여 주십시오.", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.start.GetValue() == "":
            dlg = wx.MessageDialog(self, "시작 번호가 비었습니다.", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.name.GetValue() == "":
            dlg = wx.MessageDialog(self, "파일 이름이 지정되지 않았습니다.", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if not len(self.movies.GetStrings()) == len(self.subtitles.GetStrings()):
            dlg = wx.MessageDialog(self, "자막과 파일의 갯수가 같지 않습니다.", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if "*" not in self.name.GetValue():
            dlg = wx.MessageDialog(self, "* 이 없습니다", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            number = int(self.start.GetValue())
            count = 0
            name = self.name.GetValue().split("*")
            for i in self.movies.GetStrings():
                os.rename(self.directory + "\\" + i, self.directory + "\\" + name[0] + str(number).zfill(3) +
                          name[1] + self.movies.GetStrings()[count][-4:])
                number += 1
                count += 1
            count = 0
            number = int(self.start.GetValue())
            for i in self.subtitles.GetStrings():
                os.rename(self.directory + "\\" + i, self.directory + "\\" + name[0] + str(number).zfill(3) +
                          name[1] + self.subtitles.GetStrings()[count][-4:])
                number += 1
                count += 1
            dlg = wx.MessageDialog(self, str(count) + "개 변환 완료", "Subtitles Changer", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()


class run(wx.App):
    def OnInit(self):
        frame = main(None, -1, 'Subtitles Changer')
        frame.Show(True)
        frame.Centre()
        return True


if __name__ == "__main__":
    app = run(0)
    app.MainLoop()
