from matplotlib.animation import FuncAnimation

from main import Group, Sim
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons


class Animation:

    def __init__(self, day):
        self.day = day
        self.nums = [history[Group.RAIDER][day], history[Group.SURVIVALIST][day], history[Group.CIVILIAN][day],
                     history[Group.ZOMBIE][day], history[Group.REMOVED][day]]

    def update(self):
        ax.clear()
        ax.axis('equal')
        day = self.day
        str_day = f'Day {day}'
        if day < len(history[Group.RAIDER]):
            self.nums = [history[Group.RAIDER][day], history[Group.SURVIVALIST][day], history[Group.CIVILIAN][day],
                         history[Group.ZOMBIE][day], history[Group.REMOVED][day]]
        ax.pie(self.nums, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=140)
        ax.set_title(str_day)

    def set_day(self, new_day):
        self.day = new_day
        self.update()

    def increment_day(self):
        self.day += 1
        self.update()


if __name__ == "__main__":
    sim = Sim()
    sim.simulate()
    history = sim.history
    colors = ['#94bb8b', '#911d00', '#8e3823', '#557530', '#919191']
    explode = (0.01, 0.01, 0.01, 0.01, 0.01)
    labels = ['Raider', 'Survivalist', 'Civilian', 'Zombie', 'Removed']

    fig, ax = plt.subplots()
    axfreq = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    slider = Slider(
        ax=axfreq,
        label='Day',
        valmin=1,
        valmax=len(history[Group.RAIDER]) - 1,
        valinit=1,
        valstep=1,
    )

    rax = fig.add_axes([0.0, 0, 0.15, 0.1])
    check = CheckButtons(
        ax=rax,
        labels=['Animated']
    )
    animation = Animation(day=1)
    slider.on_changed(animation.set_day)
    # ani = FuncAnimation(fig, animation.increment_day, frames=range(int(len(history[Group.RAIDER])), repeat=False)

    plt.show()
