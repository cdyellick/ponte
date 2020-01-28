from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np


class Bridge:
    """Creates a waterfall or bridge chart using matplotlib.

    Parameters
    ----------
    segment_labels : list of str
        Segment labels to show along the x-axis.
    total_segments : list of bool
        A mask indicated which segments are segment totals and should
        start at zero (the default is None, which means no segment are
        segment totals.)
    **kwargs : keywords
        Options to pass to matplotlib subplots()

    """

    def __init__(self, segment_labels, total_segments=None, **kwargs):

        self.layers = []
        self.segment_labels = segment_labels
        self.segment_count = len(segment_labels)

        # If passed, check that total_segments is the same size as segment labels
        if total_segments and len(segment_labels) != len(total_segments):
            raise ValueError('total_segments must be the same size as the series_labels.')

        # If total_segments is not passed, create a mask of all Falses
        self.total_segments = total_segments or [False] * self.segment_count

        # Create matplotlib fig
        self.fig, self.ax = plt.subplots(**kwargs)

        # Set segment (xtick) positions and labels
        self.ax.set_xticks(range(0, len(self.segment_labels)))
        self.ax.set_xticklabels(self.segment_labels)


    def _repr_png_(self):
        return display(self.fig)


    def add_layer(self, values, add_to_bottom=True, bar_args={}):
        """Add a layer of segments to the chart.

        Parameters
        ----------
        values : numpy.array or a list of numbers
            Segment values for the layer. Must be the same size as the
            series_labels used to initialize the bridge.
        add_to_bottom : bool
            Puts the layer at the bottom (the default is True).

        Returns
        -------
        None

        """

        if self.segment_count != len(values):
            raise ValueError('values must be the same size as the series_labels used to initialize the bridge.')

        layer = SimpleNamespace(**{
            'values': np.array(values).astype(float),
            'bar_args': bar_args})

        if add_to_bottom:
            self.layers.insert(0, layer)
        else:
            self.layers.append(layer)

        # Update the plot
        self._plot()


    def _plot(self):
        """Plot the waterfall chart using matplotlib."""

        # Clear axes
        self.ax.clear()
        
        # Set segment (xtick) positions and labels
        self.ax.set_xticks(range(0, len(self.segment_labels)))
        self.ax.set_xticklabels(self.segment_labels)

        segment_tops = [0] * self.segment_count  # Tracks the top of all plotted segments

        for layer in self.layers:

            values = layer.values
            bottom = self._calc_bottom(values, segment_tops)
            
            # Plot
            self.ax.bar(range(0, self.segment_count), values, bottom=bottom, **layer.bar_args)

            # Update segment_tops
            segment_tops = [x + y for x, y in zip(segment_tops, np.nan_to_num(values))]


    def _calc_bottom(self, segment_values, segment_tops):
        """Calculate the bottom for each segment"""

        # Copy values as not to modify the source array
        segment_values = segment_values.copy()

        # Shift segment_values one to the right and add to top_of_segment
        segment_values = np.nan_to_num(segment_values)
        segment_values = np.insert(segment_values, 0, 0)[:-1]
        bottom_step1 = [x + y for x, y in zip(segment_tops, segment_values)]

        # bottom_step1 is summed in a cumulative fashion, except on total
        # segments where the sum is reset to the value in top_of_segments
        bottom_step2 = []
        cumulative_b = 0

        for total_segment, b, st in zip(self.total_segments, bottom_step1, segment_tops):
            if total_segment:
                bottom_step2.append(st)
                cumulative_b = st
            else:
                cumulative_b += b
                bottom_step2.append(cumulative_b)

        return bottom_step2
