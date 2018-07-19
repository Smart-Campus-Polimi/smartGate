'''
plt.plot(*zip(*p0b), color='green');
plt.plot(*zip(*p1b), color='orange');
plt.ylim(-0.2, 1.2)
green_pir = mlines.Line2D([], [], color='green', label='P0B')
orange_pir = mlines.Line2D([], [], color='orange', label='P1B')
plt.legend(handles=[green_pir, orange_pir])
plt.title("Pir b-side")
plt.show();

plt.plot(*zip(*windowed_analog), color='blue');
blue_an = mlines.Line2D([], [], color='blue', label='Analog');
plt.yticks(np.arange(0, 1024, 50))
plt.legend(handles=[blue_an])
plt.title("Analog")
plt.show();

plt.plot(*zip(*p0a), color='green');
plt.plot(*zip(*p1a), color='orange');
plt.ylim(-0.2, 1.2)
green_pir = mlines.Line2D([], [], color='green', label='P0A')
orange_pir = mlines.Line2D([], [], color='orange', label='P1A')
plt.legend(handles=[green_pir, orange_pir])
plt.title("Pir a-side")
plt.show();

plt.plot(*zip(*infrared), color='blue');
blue_an = mlines.Line2D([], [], color='blue', label='Infrared');
plt.legend(handles=[blue_an])
plt.show();

plt.plot(*zip(*p0b), color='green');
plt.plot(*zip(*p1b), color='orange');
plt.plot(*zip(*p0a), color='red');
plt.plot(*zip(*p1a), color='blue');
plt.ylim(-0.2, 1.2)
green_pir = mlines.Line2D([], [], color='green', label='P0B')
orange_pir = mlines.Line2D([], [], color='orange', label='P1B')
red_pir = mlines.Line2D([], [], color='red', label='P0A')
blue_pir = mlines.Line2D([], [], color='blue', label='P1A')
plt.legend(handles=[green_pir, orange_pir, red_pir, blue_pir])
plt.show()
'''
