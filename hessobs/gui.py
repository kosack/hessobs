from . import Darkness
from matplotlib import pyplot as plt

# GTK3 GUI stuff:
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar


class ScheduleOverviewWindow(Gtk.Window):
    def __init__(self, schedule):
        Gtk.Window.__init__(self)
        self.resize(1124, 640)
        self.connect("delete-event", Gtk.main_quit)

        nb = Gtk.Notebook()
        self._nb = nb
        self._sched = schedule
        self._pagenames = schedule._schedules.keys()
        self._pages = dict()
        self._curperiod = None
        self._figures = dict()

        for name in schedule._schedules:

            fig = schedule._schedules[name].draw()
            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, self)

            canvas.mpl_connect("motion_notify_event", self.on_motion)
            canvas.mpl_connect("button_press_event", self.on_click)

            self._figures[name] = fig

            vbox = Gtk.VBox()
            vbox.pack_start(toolbar, False, False, 0)
            vbox.pack_start(canvas, True, True, 0)

            label = Gtk.Label(name)
            self._pages[name] = nb.append_page(vbox, label)

        vbox1 = Gtk.VBox()
        self._stat = Gtk.Statusbar()
        self._statcontext = self._stat.get_context_id("default")
        vbox1.pack_start(nb, True, True, 0)
        vbox1.pack_start(self._stat, False, False, 0)

        self.add(vbox1)
        self.show_all()

    def redraw(self,):
        print("Redraw!")
        num = self._nb.get_current_page()
        name = self._sched._schedules.keys()[num]
        sched = self._sched._schedules[name]
        plt.sca(self._figures[name].axes[0])
        self._figures[name].axes[0].clear()
        sched.draw(period=self._curperiod, newfig=False)
        self._figures[name].canvas.draw()
        self._curperiod = 2

    def on_motion(self, event):
        num = self._nb.get_current_page()
        sched = self._sched._schedules[self._sched._schedules.keys()[num]]
        text = sched.get_status_at_point(event.xdata, event.ydata)
        if text is not None:
            self._stat.push(self._statcontext, text)

    def on_click(self, event):
        num = self._nb.get_current_page()
        sched = self._sched._schedules[self._sched._schedules.keys()[num]]
        sched.on_click(event)
        self.redraw()
