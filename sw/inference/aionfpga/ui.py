#!/usr/bin/env python3

'''aionfpga ~ ui
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import io

import PySimpleGUI as sg
import matplotlib.pyplot as plt

import fhnwtoys.inference as fh

class UI():
    def __init__(self):
        self.bg_color = '#2c2c2c'

        sg.LOOK_AND_FEEL_TABLE['fhnwtoys'] = {
            'BACKGROUND': self.bg_color,
            'TEXT': '#ffffff',
            'INPUT': sg.DEFAULT_INPUT_ELEMENTS_COLOR,
            'TEXT_INPUT': sg.DEFAULT_INPUT_TEXT_COLOR,
            'SCROLL': sg.DEFAULT_SCROLLBAR_COLOR,
            'BUTTON': sg.DEFAULT_BUTTON_COLOR,
            'PROGRESS': sg.DEFAULT_PROGRESS_BAR_COLOR,
            'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0
        }

        sg.theme('fhnwtoys')

        self.boot_window()

    def paint_window(self, timeout=100):
        self.window.read(timeout=timeout)

    def boot_window(self):
        column = [[sg.Image(filename=fh.dir_graphics / 'fhnwlogo.png', pad=(38, 37), size=(556, 53))]]

        layout = [[sg.Column(column)],
                  [sg.Text('AI on FPGA', key='-TITLE-', font=('Agency FB', 200), pad=(0, (100, 0)))],
                  [sg.Text('by Nico Canzani and Dominik Müller', key='-AUTHOR-', font=('Agency FB', 50))],
                  [sg.Text(' '*100, key='-MESSAGE-', font=('Agency FB', 50), pad=(0, 150))]]

        self.window = sg.Window('boot_window', layout=layout, no_titlebar=True, location=(0, 0), size=(1920, 1080), keep_on_top=True, element_justification='c', element_padding=(0, 0), margins=(0, 0), finalize=True)
        self.window.FindElement('-TITLE-').Widget.config(cursor='none') # hide the cursor when hovering over the title text
        self.window.FindElement('-AUTHOR-').Widget.config(cursor='none') # hide the cursor when hovering over the author text
        self.paint_window()

    def update_boot_window(self, message):
        if self.window.Title != 'boot_window':
            self.boot_window()

        self.window['-MESSAGE-'].update(value=message)
        self.paint_window()

    def inference_window(self):
        layout = [[sg.Image(filename=fh.dir_graphics / 'fhnwlogo.png', pad=(38, 37), size=(556, 53))],
                  [sg.Image(key='-FRAME-', pad=(0, 4), size=(1024, 819)), sg.Image(key='-PREDICTION-', pad=(113, 0))]]

        self.window = sg.Window('inference_window', layout=layout, no_titlebar=True, location=(0, 0), size=(1920, 1080), keep_on_top=True, element_justification='l', element_padding=(0, 0), margins=(0, 0), finalize=True)
        self.window.FindElement('-FRAME-').Widget.config(cursor='none') # hide the cursor when hovering over the frame
        self.paint_window()

    def figure(self, predictions, percentages):
        fig, ax = plt.subplots(figsize=(6.7, 6.7), dpi=100)

        font_best_percentage = {
            'family': 'Agency FB',
            'color': 'white',
            'weight': 'normal',
            'size': 90
        }

        font_best_prediction = {
            'family': 'Agency FB',
            'color': 'white',
            'weight': 'normal',
            'size': 40
        }

        font_predictions = {
            'family': 'Agency FB',
            'color': 'white',
            'weight': 'normal',
            'size': 24
        }

        colors = ['#cccccc', '#acacac', '#8c8c8c', '#6c6c6c', '#4c4c4c']
        wedgeprops = {'edgecolor': self.bg_color, 'linewidth': 5, 'linestyle': 'solid', 'antialiased': True}

        circle = plt.Circle((0, 0), radius=0.79, facecolor=self.bg_color, antialiased=True)
        ax.add_artist(circle)

        ax.text(0, 0.25, f'{percentages[0]}%', fontdict=font_best_percentage, ha='center')
        ax.text(0, 0.05, predictions[0], fontdict=font_best_prediction, ha='center')

        num_predictions = len(predictions)

        if num_predictions > 1:
            x_offset_perc = -0.175
            x_offset_pred = -0.125
            y_offset = -0.2
            y_scaling = 0.12
            if num_predictions < 5:
                y_offset = y_offset - y_scaling

            for idx, (pred, perc) in enumerate(zip(predictions[1:], percentages[1:])):
                ax.text(x_offset_perc, y_offset - idx * y_scaling, f'{perc}%', fontdict=font_predictions, ha='right', va='center')
                ax.text(x_offset_pred, y_offset - idx * y_scaling, pred, fontdict=font_predictions, ha='left', va='center')

            x_pos = (x_offset_perc + x_offset_pred) / 2
            y_min = y_offset - (num_predictions - 2) * y_scaling - 0.05
            y_max = y_offset + 0.07
            ax.plot([x_pos, x_pos], [y_min, y_max], color='white', antialiased=True)

        if percentages[-1] < 0.7:
            percentages[-1] = 0.7
        ax.pie(percentages, colors=colors, labels=None, startangle=90, counterclock=False, wedgeprops=wedgeprops)

        plt.tight_layout()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)

        return fig

    def get_img_from_figure(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, transparent=True, format='png')
        buf.seek(0)
        img = buf.read()
        return img

    def update_inference_window(self, predictions, percentages, frame):
        fig = self.figure(predictions, percentages)
        img_prediction = self.get_img_from_figure(fig)

        if self.window.Title != 'inference_window':
            self.inference_window()

        self.window['-FRAME-'].update(data=frame)
        self.window['-PREDICTION-'].update(data=img_prediction)
        self.paint_window()
