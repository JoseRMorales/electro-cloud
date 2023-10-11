export interface HelloApiResponse {
  message: string
}

export interface HelloSolarResponse {
  message: string
}

export interface EnergyProcessFileResponse {
  analysisId: string
}

export interface GetAllResultsTimeSlotsResponse {
  results: GetAllResultsTimeSlotsResults[]
}

export interface GetAllResultsTimeSlotsResults {
  analysisId: string
  created_at: string
  name: null
  holder: null
  analysis_time_slots: boolean
}

export interface DeleteAnalysisResponse {
  message: string
}
