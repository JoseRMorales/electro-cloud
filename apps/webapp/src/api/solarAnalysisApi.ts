import {
  type DeleteAnalysisResponse,
  type EnergyProcessFileResponse,
  type GetAllResultsTimeSlotsResponse,
  type HelloApiResponse,
  type HelloSolarResponse,
  type SelfPercentRatiosResponse
} from './responses'

class SolarAnalysisApi {
  private readonly url: string

  constructor () {
    this.url =
      process.env.SOLAR_ANALYSIS_API_URL ??
      (() => {
        throw new Error('SOLAR_ANALYSIS_API_URL is not defined')
      })()
  }

  async getHelloApi (): Promise<string> {
    const res = await fetch(`${this.url}/`)
    const data = (await res.json()) as HelloApiResponse
    const { message } = data
    return message
  }

  async getHelloSolar (): Promise<string> {
    const res = await fetch(`${this.url}/solar/`)
    const data = (await res.json()) as HelloSolarResponse
    const { message } = data
    return message
  }

  async postEnergyFile (formData: FormData): Promise<string> {
    // Extract the file from the FormData object
    const res = await fetch(`${this.url}/energy/time-slots`, {
      method: 'POST',
      body: formData
    })
    const data = (await res.json()) as EnergyProcessFileResponse
    const { analysisId } = data
    return analysisId
  }

  async getEnergyByTimeSlot (analysisId: string): Promise<string> {
    const res = await fetch(`${this.url}/energy/time-slots/${analysisId}`)
    const data = await res.text()
    return data
  }

  async getAllResultsTimeSlots (): Promise<GetAllResultsTimeSlotsResponse> {
    const res = await fetch(`${this.url}/energy/time-slots`)
    const data = (await res.json()) as GetAllResultsTimeSlotsResponse
    return data
  }

  async deleteAnalysis (analysisId: string): Promise<string> {
    const res = await fetch(`${this.url}/energy/time-slots/${analysisId}`, {
      method: 'DELETE'
    })
    const { message } = (await res.json()) as DeleteAnalysisResponse
    return message
  }

  async getSolarAnalysis (): Promise<GetAllResultsTimeSlotsResponse> {
    const res = await fetch(`${this.url}/solar/analysis`)
    const data = (await res.json()) as GetAllResultsTimeSlotsResponse
    return data
  }

  async getSolarConsumptionProductionPlot (analysisId: string): Promise<Blob> {
    const res = await fetch(
      `${this.url}/solar/monthly_consumption_production_plot/${analysisId}`
    )
    const data = await res.blob()
    return data
  }

  async getSolarMonthlyPlots (analysisId: string): Promise<ArrayBuffer> {
    const res = await fetch(
      `${this.url}/solar/results_monthly_plots/${analysisId}`
    )
    const data = await res.arrayBuffer()
    return data
  }

  async getSolarSelfPercentRatios (
    analysisId: string
  ): Promise<SelfPercentRatiosResponse> {
    const res = await fetch(
      `${this.url}/solar/self_percent_ratios/${analysisId}`
    )
    const data = (await res.json()) as SelfPercentRatiosResponse
    return data
  }

  async getSolarMonthlyProduction (analysisId: string): Promise<string> {
    const res = await fetch(
      `${this.url}/solar/monthly_production/${analysisId}`
    )
    const data = await res.text()
    return data
  }

  async getSolarMonthlyConsumption (analysisId: string): Promise<string> {
    const res = await fetch(
      `${this.url}/solar/monthly_consumption/${analysisId}`
    )
    const data = await res.text()
    return data
  }

  async postSolarForm (formData: FormData): Promise<string> {
    const res = await fetch(`${this.url}/solar/process-file`, {
      method: 'POST',
      body: formData
    })
    const data = (await res.json()) as EnergyProcessFileResponse
    const { analysisId } = data
    return analysisId
  }
}

export default SolarAnalysisApi
