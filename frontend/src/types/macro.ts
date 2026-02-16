export interface MacroDataPoint {
  date: string;
  value: number;
}

export interface MacroTimeSeries {
  series_id: string;
  name: string;
  unit: string;
  data: MacroDataPoint[];
}
