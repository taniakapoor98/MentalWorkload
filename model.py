import io
import sys
from tkinter import messagebox

import pandas as pd
import os
import pandas as pd
import numpy as np
from PIL import Image
from matplotlib.patches import Wedge
from mne.time_frequency import psd_array_welch
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Model:

    feature_cols = ['delta_power', 'theta_power', 'gamma_power', 'alpha_power', 'beta_power']  # , 'spectral_entropy']

    freq_bands = {
        'delta': (1, 4),
        'theta': (4, 8),
        'gamma': (30, 45),
        'alpha': (8, 13),
        'beta': (13, 30)

    }

    def __init__(self):
        self.session_id = None

    def reshape_data(self,df):
        reshaped_data = []
        # reshaped_labels = []
        reshaped_groups = []

        for (subject, trial), group in df.groupby(['subject', 'trial']):
            features = group[self.feature_cols].values.flatten()
            reshaped_data.append(features)
            # reshaped_labels.append(group['label'].values[0])  # Assuming the label is the same for each trial
            reshaped_groups.append(subject)

        return np.array(reshaped_data), np.array(reshaped_groups)

    def compute_band_power(self,data, sfreq, band):
        band_power, _ = psd_array_welch(data, sfreq=sfreq, fmin=band[0], fmax=band[1], n_per_seg=192, n_fft=128 * 6,
                                        verbose=False)
        return np.mean(band_power)

    def image_to_blob(image_path):
        with Image.open(image_path) as image:
            byte_array = io.BytesIO()
            image.save(byte_array, format=image.format)
            return byte_array.getvalue()
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        # Example preprocessing: filling missing values with zero
        print('Preprocessing..')
        try:
            # Replace with the actual path to the CSV file
            df = df

            all_data = []
            all_features = []
            all_labels = []
            all_subjects = []

            # Assuming the first column is 'subject'
            subjects = df['subject'].unique()

            for subject in subjects:
                subject_data = df[df['subject'] == subject].drop(columns=['subject'])
                labels = subject_data.index  # or some other method to generate labels
                data = subject_data.to_numpy()
                sfreq = 128  # Sampling frequency -- change to 128
                all_data.append(data)

                reshaped_data = data  # Adjust this based on the correct shape

                subject_features = []
                for trial in range(reshaped_data.shape[0]):
                    trial_data = reshaped_data[trial, :].reshape(-1, 14)  # Assuming 14 channels
                    trial_features = []
                    for channel in range(trial_data.shape[1]):  # Iterate over each channel
                        channel_data = trial_data[:, channel]
                        channel_features = []
                        for band_name, band_freq in self.freq_bands.items():
                            band_power = self.compute_band_power(channel_data, sfreq, band_freq)
                            channel_features.append(band_power)
                        trial_features.extend(channel_features)

                    # Store features along with subject ID
                    subject_features.append(np.array(trial_features))

                all_features.append(np.array(subject_features))  # shape (trials, features)
                all_labels.append(labels)
                all_subjects.extend([subject] * subject_data.shape[0])  # Keep track of subjects

            # Convert lists to arrays
            all_features = np.concatenate(all_features)
            all_labels = np.concatenate(all_labels)

            # Create a DataFrame with features and subject labels
            feature_columns = [f'{band}_power_channel_{ch + 1}' for ch in range(trial_data.shape[1]) for band in self.freq_bands.keys()]
            feature_df = pd.DataFrame(all_features, columns=feature_columns)
            feature_df['subject'] = all_subjects
            feature_df['trial'] = all_labels
            feature_df['label'] = all_labels

            df = feature_df.copy()
            # Initialize an empty DataFrame to store reshaped data
            channels = range(1, 15)  # Assuming 14 channels

            # Initialize an empty list to store dicts for DataFrame creation
            data_list = []

            # Iterate over each subject and trial to reshape the data
            for subj in df['subject'].unique():
                for trial in df[df['subject'] == subj]['trial'].unique():
                    subject_data = df[(df['subject'] == subj) & (df['trial'] == trial)]
                    for channel in channels:
                        channel_data = {
                            'subject': subj,
                            'trial': trial,
                            'channel': channel,
                            'delta_power': subject_data[f'delta_power_channel_{channel}'].values[0],
                            'theta_power': subject_data[f'theta_power_channel_{channel}'].values[0],
                            'alpha_power': subject_data[f'alpha_power_channel_{channel}'].values[0],
                            'beta_power': subject_data[f'beta_power_channel_{channel}'].values[0],
                            'gamma_power': subject_data[f'gamma_power_channel_{channel}'].values[0]
                        }
                        data_list.append(channel_data)

            # Create the reshaped DataFrame
            reshaped_data = pd.DataFrame(data_list)

            df = reshaped_data.copy()
            # Features columns

            # Reshape the data


            X, groups = self.reshape_data(df)
            print(X.shape)
            print('Preprocessing complete.')
        except Exception as e:
            print(f"Invalid file. Please upload file in correct format: {e}")
            messagebox.showerror("File error", "Invalid file. Please upload file in correct format.")

        return X

    def draw_gauge(self,subject, prediction, pdf):
        import gui
        colors = ["#ee4d55", "#fabd57", '#4dab6d']

        values = [0, 1, 2]

        x_axis_vals = [0, 0.44, 0.88, 1.32, 1.76, 2.2, 2.64]
        fig = plt.figure(figsize=(18, 18))

        ax = fig.add_subplot(projection="polar");

        ax.bar(x=[0, 1, 2], width=1.14, height=0.5, bottom=2,
               linewidth=3, edgecolor="white",
               color=colors, align="edge");

        plt.annotate("High", xy=(0.48, 2.2), rotation=-58, color="white", fontweight="bold");
        plt.annotate("Medium", xy=(1.6, 2.2), color="white", fontweight="bold");
        plt.annotate("Low", xy=(2.6, 2.25), rotation=55, color="white", fontweight="bold");

        # for loc, val in zip([0, 1,2], values):
        #     plt.annotate(val, xy=(loc, 2.5), ha="right" if val<=20 else "left");
        if prediction == 0:
            at = 'Low'
            xt = 2.55
        elif prediction == 1:
            at = 'Medium'
            xt = 1.55
        else :
            at = 'High'
            xt = 0.5
        plt.annotate(at, xytext=(0, 0), xy=(xt, 2.0),  # .5 - 2, 1.55 - 1 , 2.55 - 0
                     arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
                     bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
                     fontsize=45, color="white", ha="center"
                     );

        ax.set_axis_off();
        # Title
        plt.title(f'ID: {subject} Workload ', loc="center", pad=20, fontsize=35, fontweight="bold")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_blob = buf.read()
        db_ = gui.DB()



        db_.write_to_hist_table(session_id=self.session_id, subject=int(subject), prediction=at, img_blob=img_blob)
        print(subject)

        # Save the figure to the PDF
        pdf.savefig(fig)
        plt.close()

    def predict(self,X):

        model_path = resource_path(r'.\models\svm_loso.pkl')
        model = joblib.load(model_path)


        predictions = model.predict(X)

        result_df = pd.DataFrame({'Subject': self.subjects, 'Prediction': predictions})
        print(f'predictions:{result_df}')

        with PdfPages('workload_meters.pdf') as pdf:
            for index, row in result_df.iterrows():
                self.draw_gauge(row['Subject'], row['Prediction'], pdf)
        print('saved')
        return result_df

    def measure_workload(self, df: pd.DataFrame) -> pd.DataFrame:
        import gui
        self.subjects = df['subject']
        X = self.preprocess(df)
        db_ = gui.DB()
        self.session_id = db_.get_next_session_id()
        return self.predict(X)
