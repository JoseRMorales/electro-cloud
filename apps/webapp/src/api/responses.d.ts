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
  createdAt: Date
  name: null
  holder: null
  analysisTimeSlots: boolean
}
