#!/usr/bin/env python
# coding: utf-8

import os
import pickle
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd
import scipy.io
from mne.time_frequency import psd_array_welch
from scipy.stats import skew, kurtosis
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC


def install_packages():
    packages = ["numpy", "pandas", "matplotlib", "scipy", "mne", "scikit-learn", "nolds"]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


class EEGDataProcessor:
    def __init__(self, main_dir='dataset nBack'):
        self.main_dir = main_dir
        self.all_data = []
        self.all_data_std = []
        self.all_labels = []
        self.all_labels_enc = []

    def load_files(self):
        for subdir in os.listdir(self.main_dir):
            subdir_path = os.path.join(self.main_dir, subdir)
            if os.path.isdir(subdir_path):
                self._process_subdir(subdir_path)
        self._concatenate_data()

    def _process_subdir(self, subdir_path):
        scaler = StandardScaler()
        label_encoder = LabelEncoder()
        for file in os.listdir(subdir_path):
            if 'Session_1' in file and file.endswith('.mat'):
                file_path = os.path.join(subdir_path, file)
                mat_contents = scipy.io.loadmat(file_path, simplify_cells=True)
                clean_data = mat_contents['RunOutput']['clean']['correctOnly']
                labels = clean_data['labels_opt']
                data = clean_data['data']
                self.all_data.append(data)
                self.all_labels.append(labels)

                standardized_data = scaler.fit_transform(data.reshape(-1, data.shape[-1])).reshape(data.shape)
                self.all_data_std.append(standardized_data)

                label_enc = label_encoder.fit_transform(labels)
                self.all_labels_enc.append(label_enc)

    def _concatenate_data(self):
        self.all_data_np = np.concatenate(self.all_data, axis=2)
        self.all_data_std_np = np.concatenate(self.all_data_std, axis=2)
        self.all_labels_np = np.concatenate(self.all_labels, axis=0)
        print(f'All Data shape : {self.all_data_np.shape}')
        print(f'All Labels shape : {self.all_labels_np.shape}')

    def print_data_structure(self):
        print("data structure:")
        for i, session in enumerate(self.all_data):
            print(f"subject {i + 1} shape: {session.shape}")


class FeatureExtractor:
    def __init__(self, data, labels, freq_bands, sampling_rate=128):
        self.data = data
        self.labels = labels
        self.freq_bands = freq_bands
        self.sampling_rate = sampling_rate
        self.all_features = []

    def extract_features(self):
        self._extract_frequency_domain_features()
        return self.all_features

    def _extract_frequency_domain_features(self):
        for subject_data in self.data:
            subject_features = []
            for trial in range(subject_data.shape[2]):
                trial_data = subject_data[:, :, trial]
                trial_features = self._extract_band_powers(trial_data)
                subject_features.append(trial_features.T)
            self.all_features.append(np.array(subject_features))

    def _extract_band_powers(self, trial_data):
        trial_features = []
        for band_name, band_freq in self.freq_bands.items():
            band_power = self._compute_band_power(trial_data, band_freq)
            trial_features.append(band_power)
        return np.array(trial_features)

    def _compute_band_power(self, data, band):
        band_power, _ = psd_array_welch(data, sfreq=self.sampling_rate, fmin=band[0], fmax=band[1], n_per_seg=192,
                                        n_fft=128*6, verbose=False)
        return np.mean(band_power, axis=-1)


class DataPreparer:
    def __init__(self, data_std, all_features, labels_enc):
        self.selected_features = None
        self.data_std = data_std
        self.all_features = all_features
        self.labels_enc = labels_enc
        self.flattened_features = []
        self.flattened_labels = []

    def prepare_data(self):
        self._flatten_features()
        df_features = pd.DataFrame(self.flattened_features)
        df_labels = pd.DataFrame(self.flattened_labels, columns=['label'])
        df = pd.concat([df_features, df_labels], axis=1)
        return df

    def prepare_train_test(self, data_frame):
        self.select_features(data_frame)
        tmp_df = data_frame[["subject", "trial", "label"]]
        df = pd.concat([pd.DataFrame(self.selected_features), tmp_df], axis=1)
        df_train = df[df['subject'] < 41]
        df_test = df[df['subject'] > 40]
        return df_train, df_test

    def select_features(self, df, k=100):
        features_df = df.drop(['subject', 'trial', 'label'], axis=1)
        labels_df = df['label']
        selector = SelectKBest(score_func=f_classif, k=k)
        self.selected_features = selector.fit_transform(features_df, labels_df)
        selected_indices = selector.get_support(indices=True)
        print("Selected feature indices:", selected_indices)
        print("Shape of selected features:", self.selected_features.shape)

    def _flatten_features(self):
        for subj_idx, subject_data in enumerate(self.data_std):
            num_channels, num_samples, num_trials = subject_data.shape
            print(
                f"Processing subject {subj_idx + 1}/{len(self.data_std)}, with {num_channels} channels, {num_samples} samples, and {num_trials} trials")
            for trial in range(num_trials):
                trial_features = self._extract_trial_features(subj_idx, subject_data, trial)
                self.flattened_features.append(trial_features)
                self.flattened_labels.append(self.labels_enc[subj_idx][trial])

    def _extract_trial_features(self, subj_idx, subject_data, trial):
        feature_dict = {'subject': subj_idx, 'trial': trial}
        trial_features = []
        for channel in range(subject_data.shape[0]):
            signal = subject_data[channel, :, trial]
            # time_features = self._extract_time_domain_features(signal)
            # trial_features.extend(time_features)
            band_features = self.all_features[subj_idx][trial, channel, :]
            trial_features.extend(band_features)
        for trial_feature_id, trial_feature in enumerate(trial_features):
            feature_dict[f'feature_{trial_feature_id}'] = trial_feature
        return feature_dict

    @staticmethod
    def _extract_time_domain_features(signal):
        features = [np.mean(signal), np.std(signal), skew(signal), kurtosis(signal)]
        return features


class ModelTrainer:
    def __init__(self, df):
        self.df = df
        self.selected_features = None

    @staticmethod
    def reshape_data(df):
        features_df = df.drop(['subject', 'trial', 'label'], axis=1)
        feature_cols = features_df.columns.values
        reshaped_data, reshaped_labels, reshaped_groups = [], [], []
        for (subject, trial), group in df.groupby(['subject', 'trial']):
            features = group[feature_cols].values.flatten()
            reshaped_data.append(features)
            reshaped_labels.append(group['label'].values[0])
            reshaped_groups.append(subject)
        return np.array(reshaped_data), np.array(reshaped_labels), np.array(reshaped_groups)

    @staticmethod
    def save_model(model, name):
        model_pkl_file = "models/" + name + ".pkl"
        with open(model_pkl_file, 'wb') as file:
            pickle.dump(model, file)

    def train_svm(self, X, y, groups):
        logo = LeaveOneGroupOut()
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('svm', SVC(kernel='poly', decision_function_shape='ovr'))
        ])
        accuracies = []
        for train_idx, test_idx in logo.split(X, y, groups=groups):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            accuracies.append(accuracy)
            print(f'Subject {groups[test_idx][0]} - Accuracy: {accuracy:.3f}')
        average_accuracy = np.mean(accuracies)
        print(f'Average accuracy: {average_accuracy:.3f}')
        self.save_model(pipeline, 'svm_loso')
        print('SVM model saved')


def main():
    warnings.filterwarnings('ignore')
    processor = EEGDataProcessor()
    install_packages()
    processor.load_files()
    processor.print_data_structure()

    freq_bands = {
        'delta': (1, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45)
    }

    feature_extractor = FeatureExtractor(processor.all_data, processor.all_labels, freq_bands)
    all_features = feature_extractor.extract_features()

    data_preparer = DataPreparer(processor.all_data_std, all_features, processor.all_labels_enc)
    df = data_preparer.prepare_data()
    df_train, df_test = data_preparer.prepare_train_test(df)

    model_trainer = ModelTrainer(df_train)
    X, y, groups = model_trainer.reshape_data(df_train)
    model_trainer.train_svm(X, y, groups)


if __name__ == "__main__":
    main()
