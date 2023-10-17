import tkinter as tk
import random
from k_means import KMeans
from tkinter.font import Font


class Display(tk.Tk):
    def __init__(self):
        super().__init__()

        """APP SETTINGS"""

        self.title("K-Means Demo")
        self.resizable(False, False)
        self.configure(bg="grey")

        """SIDE AREA"""

        # FRAME: Side Area
        self.side_frame = tk.Frame(self, width=200, height=500)
        self.side_frame.pack_propagate(False)
        self.side_frame.pack(side="left", pady=5, padx=(5, 0))

        # TITLE BAR
        self.title_bar = tk.Label(self.side_frame, text="K-Means Demo", bg="grey", fg="white",
                                  font=Font(size=12, weight="bold"))
        self.title_bar.pack(fill="x", ipady=5)

        """CONTROL AREA"""

        # FRAME: Control Area
        self.control_frame = tk.Frame(self.side_frame, bg=self.side_frame.cget("bg"))
        self.control_frame.pack(padx=10)

        # SETTINGS CATEGORY: General Settings
        (tk.Label(self.control_frame, text="1. General Settings", font=Font(weight="bold", size=9), anchor="w")
         .pack(fill="x"))

        # CONTROL: Centroid count
        self.centroid_slider_variable = tk.IntVar()
        self.centroid_slider = tk.Scale(self.control_frame, from_=1, to=10, orient=tk.HORIZONTAL, label="Centroids",
                                        variable=self.centroid_slider_variable, cursor="hand2")
        self.centroid_slider_variable.set(2)
        self.centroid_slider.pack(fill="x")

        # CONTROL: Simulation speed
        self.speed_slider_variable = tk.IntVar()
        self.speed_slider = tk.Scale(self.control_frame, from_=1, to=10, orient=tk.HORIZONTAL, label="Simulation Speed",
                                     variable=self.speed_slider_variable, cursor="hand2")
        self.speed_slider_variable.set(5)
        self.speed_slider.pack(fill="x")

        # SETTINGS CATEGORY: Observations
        (tk.Label(self.control_frame, text="2. Add Points", font=Font(weight="bold", size=9), anchor="w")
         .pack(fill="x", pady=(10, 0)))
        tk.Label(self.control_frame, text="Add points by clicking directly on the grid, or add random points below.",
                 wraplength=200, anchor="w", justify="left", fg="grey").pack(fill="x")

        # SUB FRAME: Random points controls
        self.random_control_frame = tk.Frame(self.control_frame)
        self.random_control_frame.pack(fill="x")

        # CONTROL: Random observation adding intensity (Combination of amount and spread)
        self.random_intencity_slider_variable = tk.IntVar()
        self.random_intencity_slider = tk.Scale(self.random_control_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                                variable=self.random_intencity_slider_variable, label="Amount",
                                                cursor="hand2")
        self.random_intencity_slider_variable.set(15)
        self.random_intencity_slider.pack(side="left", fill="x", expand=True)

        # CONTROL: Add random observations
        self.add_random_obs_button = tk.Button(self.random_control_frame, text="Place\nRandom", bg="light grey",
                                               command=self.add_random_obs, cursor="hand2")
        self.add_random_obs_button.pack(side="right", fill="y")

        # SETTINGS CATEGORY: Observations
        (tk.Label(self.control_frame, text="3. Start Simulation", font=Font(weight="bold", size=9), anchor="w")
         .pack(fill="x", pady=(10, 0)))

        # FRAME: Exec Buttons
        self.sim_exec_controls = tk.Frame(self.control_frame)
        self.sim_exec_controls.pack(fill="x", pady=(5, 0))
        self.sim_exec_controls.columnconfigure(1, weight=1)

        # CONTROL: Reset run and observations
        self.reset_observations_button = tk.Button(self.sim_exec_controls, text="Reset", command=self.reset_run,
                                                   bg="light grey", cursor="hand2")
        self.reset_observations_button.grid(row=0, column=0, ipadx=5, ipady=2)

        # CONTROL: Start run
        self.start_button = tk.Button(self.sim_exec_controls, text="Start", command=self.on_start_button,
                                      cursor="hand2", bg="#8ACE88")
        self.start_button.grid(row=0, column=1, sticky="ew", ipady=2)

        # DISPLAY: Start validation info (Info on invalid configurations)
        self.validation_info = tk.Label(self.sim_exec_controls, text="", fg="red", wraplength=200)
        self.validation_info.grid(row=1, column=0, columnspan=2)

        """CANVAS AREA"""

        self.canvas_frame = tk.Frame(self, width=500, height=500)
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.pack(side="right", padx=5, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0, relief="ridge", cursor="hand2")
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
        fac = int(size / 2)  # Offset factor for edges of the point

        # Draw circle on canvas. Centroids are displayed as outline. Obervations are filled in
        if centroid:
            self.canvas.create_oval(x - fac, y - fac, x + fac, y + fac, width=2, fill="", outline=color)
        else:
            self.canvas.create_oval(x - fac, y - fac, x + fac, y + fac, width=0, fill=color)

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
        def rand_int(): return random.randint(0, 255)
        return '#%02X%02X%02X' % (rand_int(), rand_int(), rand_int())

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
            self.validation_info.configure(text="Can't have more centroids than observations!")
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
        return int(1000 / self.speed_slider_variable.get())

    def reset_run(self):
        self.k_means_instance = None
        self.new_observations = []
        self.canvas.delete("all")

    def add_random_obs(self):
        center_x, center_y = random.randint(0, 500), random.randint(0, 500)
        intensity = self.random_intencity_slider_variable.get()

        for _ in range(intensity):
            rand_x, rand_y = (random.randint(center_x - intensity * 3, center_x + intensity * 3),
                              random.randint(center_y - intensity * 3, center_y + intensity * 3))

            self.draw_point(rand_x, rand_y)
            self.new_observations.append((rand_x, rand_y))


if __name__ == '__main__':
    display = Display()
    display.mainloop()
