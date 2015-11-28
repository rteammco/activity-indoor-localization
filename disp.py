import Tkinter as Tk
import time

from pf import ParticleFilter, PFConfig


class DisplayWindow():

  # Display settings.
  _PARTICLE_RADIUS = 10
  _UPDATE_INTERVAL_MS = 500

  def __init__(self, pf):
    self._pf = pf
    self._main_window = Tk.Tk()
    self._main_window.title('Particle Filter')
    self._canvas = Tk.Canvas(
        self._main_window, width=500, height=500, background='white')
    self._canvas.pack()

  def start(self):
    self._update()
    self._main_window.mainloop()

  def _update(self):
    self._pf.update()
    self._render()
    self._main_window.after(self._UPDATE_INTERVAL_MS, self._update)

  def _render(self):
    self._canvas.delete('all')
    for particle in self._pf.particles:
      x1 = particle.x - self._PARTICLE_RADIUS / 2
      y1 = particle.y - self._PARTICLE_RADIUS / 2
      x2 = x1 + self._PARTICLE_RADIUS
      y2 = y1 + self._PARTICLE_RADIUS
      self._canvas.create_oval(x1, y1, x2, y2, fill='blue')


if __name__ == '__main__':
  print 'Starting...'
  config = PFConfig()
  pf = ParticleFilter(config)
  w = DisplayWindow(pf)
  w.start()
  print 'Goodbye!'
