export interface HelloApiResponse {
  message: string
}

export interface HelloSolarResponse {
  message: string
}

export interface EnergyProcessFileResponse {
  message: string
}

export interface GetAllResultsTimeSlotsResponse {
  results: GetAllResultsTimeSlotsResults[]
}

export interface GetAllResultsTimeSlotsResults {
  analysisID: string
  created_at: Date
  name: null
  holder: null
  analysis_time_slots: boolean
}

export interface DeleteAnalysisResponse {
  message: string
}
