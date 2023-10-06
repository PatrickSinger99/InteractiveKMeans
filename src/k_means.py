from typing import Sequence, Union
import random


class KMeans:
    def __init__(self, observations: Sequence[Sequence[Union[int, float]]], k: int):
        self.observations = observations
        self.classes = []
        self.centroids = []
        self.k = k
        self.iteration = 0

        """INITIAL CALLS"""

        self.set_random_centroids()
        self.set_classes()

    @staticmethod
    def distance(point_a, point_b):
        added_distances = 0
        for i in range(len(point_a)):
            added_distances += (point_a[i] - point_b[i])**2
        return added_distances**.5

    def set_random_centroids(self):
        self.centroids = random.sample(self.observations, k=self.k)

    def set_classes(self):
        self.classes = []

        for observation in self.observations:
            distances_to_centroid = []

            for i, centroid in enumerate(self.centroids):
                distances_to_centroid.append(self.distance(observation, centroid))

            self.classes.append(distances_to_centroid.index(min(distances_to_centroid)))

    def recalculate_centroids(self):
        sum_of_obs = [[0] * len(self.centroids[0]) for _ in range(len(self.centroids))]

        for obs_index, observation in enumerate(self.observations):
            for dim_index, dim_value in enumerate(observation):
                sum_of_obs[self.classes[obs_index]][dim_index] += dim_value

        for cen_index, new_cen_sum in enumerate(sum_of_obs):
            class_amount = self.classes.count(cen_index)
            self.centroids[cen_index] = [dim_sum/class_amount for dim_sum in new_cen_sum]

    def step(self, new_observations: Sequence[Sequence[Union[int, float]]] = None):
        # If new observations have been added during run, add them to observations list and update classes list
        if new_observations:
            self.observations += new_observations
            self.set_classes()

        # Find new positions of centroids and recalculate the nearest class for each observation
        self.recalculate_centroids()
        self.set_classes()

        # Increment iteration counter
        self.iteration += 1


if __name__ == '__main__':
    obs = [[random.randint(0, 500) for _ in range(2)] for _ in range(20)]
    kmeans = KMeans(obs, k=4)
    kmeans.set_classes()
    print(kmeans.centroids)
    kmeans.recalculate_centroids()
    print(kmeans.centroids)