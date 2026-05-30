export type EqBand = {
  frequency_hz: number;
  gain_db: number;
  q: number;
  enabled: boolean;
};

export type ProjectSession = {
  project_id: string;
  name: string;
  status: string;
  track_ids: string[];
  analysis_ids: string[];
  action_ids: string[];
};

export type TrackSession = {
  track_id: string;
  project_id: string;
  filename: string;
  file_path: string;
  file_url: string;
  status: string;
};

export type AnalysisSession = {
  analysis_id: string;
  track_id: string;
  status: string;
  result: {
    duration_sec: number;
    sample_rate: number;
    channels: number;
    peak_dbfs: number;
    rms_dbfs: number;
  };
};

export type ActionSession = {
  action_id: string;
  track_id: string;
  type: string;
  status: string;
  params: {
    low_cut_hz?: number;
    high_cut_hz?: number;
    bands?: EqBand[];
  };
  processed_file_url: string | null;
};

export type ProjectDetail = ProjectSession & {
  tracks: TrackSession[];
  analyses: AnalysisSession[];
  actions: ActionSession[];
};
