import tkinter as tk
import random
from k_means import KMeans


class Display(tk.Tk):
    def __init__(self):
        super().__init__()

        """APP SETTINGS"""

        self.title("K-Means Experiment")
        self.resizable(False, False)

        """CONTROL AREA"""

        self.control_frame = tk.Frame(self, width=200, height=500, bg="light grey")
        self.control_frame.pack_propagate(False)
        self.control_frame.pack(side="left")

        self.start_button = tk.Button(self.control_frame, text="Start", command=self.on_start_button)
        self.start_button.pack()

        self.validation_info = tk.Label(self.control_frame, text="", fg="red")
        self.validation_info.pack()

        self.centroid_slider_variable = tk.IntVar()
        self.centroid_slider = tk.Scale(self.control_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                        variable=self.centroid_slider_variable)
        self.centroid_slider.pack()

        self.speed_slider_variable = tk.IntVar()
        self.speed_slider = tk.Scale(self.control_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                     variable=self.speed_slider_variable)
        self.speed_slider_variable.set(5)
        self.speed_slider.pack()

        self.reset_observations_button = tk.Button(self.control_frame, text="Reset", command=self.reset_run)
        self.reset_observations_button.pack()

        self.random_intencity_slider_variable = tk.IntVar()
        self.random_intencity_slider = tk.Scale(self.control_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                                variable=self.random_intencity_slider_variable)
        self.random_intencity_slider_variable.set(15)
        self.random_intencity_slider.pack()

        self.add_random_obs_button = tk.Button(self.control_frame, text="Add randoms", command=self.add_random_obs)
        self.add_random_obs_button.pack()

        """CANVAS AREA"""

        self.canvas_frame = tk.Frame(self, width=500, height=500)
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.pack(side="right")

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0, relief="ridge")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button 1>", lambda e: self.on_canvas_click(e))

        """INITIAL STATE"""

        self.class_colors = []  # Saves a hex color for every centroid
        self.new_observations = []  # Saves observations that are added by user during
        self.k_means_instance = None

    def on_canvas_click(self, event):
        # Draw new observation on canvas
        self.draw_point(event.x, event.y)
        self.new_observations.append((event.x, event.y))

    def draw_point(self, x, y, size=10, color="black", centroid=False):
        fac = int(size/2)  # Offset factor for edges of the point

        # Draw circle on canvas. Centroids are displayed as outline. Obervations are filled in
        if centroid:
            self.canvas.create_oval(x-fac, y-fac, x+fac, y+fac, width=2, fill="", outline=color)
        else:
            self.canvas.create_oval(x-fac, y-fac, x+fac, y+fac, width=0, fill=color)

    def draw_state(self, observations, classes, centroids):
        # Check if the current class colors are still valid
        if len(self.class_colors) != len(centroids):
            self.class_colors = [self.get_random_color() for _ in range(len(centroids))]

        # Draw all observations
        for i, (obs_x, obs_y) in enumerate(observations):
            self.draw_point(obs_x, obs_y, color=self.class_colors[classes[i]])

        # Draw all centroids
        for i, (cen_x, cen_y) in enumerate(centroids):
            self.draw_point(cen_x, cen_y, color=self.class_colors[i], centroid=True, size=16)

    @staticmethod
    def get_random_color():
        r = lambda: random.randint(0, 255)
        return '#%02X%02X%02X' % (r(), r(), r())

    def run(self, k_means: KMeans):
        # Only run if k means instance is still current running instance
        if k_means == self.k_means_instance:

            # Update k means class instance
            k_means.step(new_observations=self.new_observations)
            self.new_observations = []  # Reset bc they have been added to the k means class instance

            # Update canvas
            self.canvas.delete("all")
            self.draw_state(k_means.observations, k_means.classes, k_means.centroids)

            # Execute next step after set delay
            self.after(self.get_speed(), lambda: self.run(k_means=k_means))

    def on_start_button(self):

        # If restart occurs, copy over the previous observation coords to the new k means run
        if self.k_means_instance:
            self.new_observations += self.k_means_instance.observations

        # Validate start conditions
        if len(self.new_observations) < self.centroid_slider_variable.get():
            # CASE: INVALID START
            self.validation_info.configure(text="Cant have more centroids than observations!")
            return

        # CASE: VALID START
        self.start_button.configure(text="Restart")
        self.validation_info.configure(text="")

        # Create new k means class instance
        k_means_instance = KMeans(observations=self.new_observations, k=self.centroid_slider_variable.get())
        self.new_observations = []  # Reset bc they have been added to the k means class instance
        self.k_means_instance = k_means_instance

        # Draw the initial state of the observations
        self.canvas.delete("all")
        self.draw_state(k_means_instance.observations, k_means_instance.classes, k_means_instance.centroids)

        self.after(self.get_speed(), lambda: self.run(k_means_instance))

    def get_speed(self):
        return int(1000/self.speed_slider_variable.get())

    def reset_run(self):
        self.k_means_instance = None
        self.new_observations = []
        self.canvas.delete("all")

    def add_random_obs(self):
        center_x, center_y = random.randint(0, 500), random.randint(0, 500)
        intensity = self.random_intencity_slider_variable.get()

        for _ in range(intensity):
            rand_x, rand_y = (random.randint(center_x-intensity*3, center_x+intensity*3),
                              random.randint(center_y-intensity*3, center_y+intensity*3))

            self.draw_point(rand_x, rand_y)
            self.new_observations.append((rand_x, rand_y))


if __name__ == '__main__':
    display = Display()
    display.mainloop()
