import matplotlib.pyplot as plt
from datetime import datetime

y = [38, -36, 70]
x = [datetime(2015, 11, 12, 12, 1, 10), datetime(2015, 11, 12, 12, 1, 20), datetime(2015, 11, 12, 12, 1, 30)]

plt.plot(x, y)
plt.show()